# 修复 libobk rdb config 重复初始化

## 问题陈述
T0388 移除 `rdb_auto_init` constructor 后，改为在多个最外层入口显式调用 `init_config`。在 libobk（Oracle SBT 库 + FileTransferAgent 独立 CLI）中，`init_config` 被放在了 `sbtinit`、`sbtinit2`、`main.c` 三处。Oracle SBT 标准调用序为 `sbtinit`（进程级，调一次）→ 多次 `sbtinit2`（每次备份会话），导致 `init_config` 至少被调两次，且每个备份会话都重新解析配置文件——属于"重复初始化"，偏离原 constructor"进程内只加载一次"语义。

## 初步事实（Triage 已查证）
- 调用点：`libobk/lib/sbt/libobk.c:802`（`sbtinit`）、`libobk/lib/sbt/libobk.c:379`（`sbtinit2`，内部再走 `sbt_client_tls_config_init`）、`libobk/main.c`（FileTransferAgent CLI，在 `sbt_server_tls_config_init` 前）。
- Oracle SBT 约定：`sbtinit` 必须最先调用一次；`sbtinit2` 每次备份/恢复会话调用一次（可能多次）。
- `init_config`（`libs/rdb-config.c:157`）→ `parse_config` 为双缓冲交换、幂等可重入；重复调用**不崩溃**，但属于冗余重解析（逐会话重复），且是设计层面的重复初始化。
- `init_config` 必须保持"每次强制重加载"语义（T0388 为 `rdb_config_test` 明确保留），因此**不能在 `init_config` 内部加一次性守卫**，只能在 libobk 入口层做。

## 方案方向（一次性守卫）
在 libobk 入口层引入进程级一次性守卫，使 `init_config` 在 libobk 视角下只真正加载一次，同时不触碰 `init_config` 自身语义：

- 守卫定义于 `libobk/lib/logic/oracleCmdTbl.c`（线程安全，采用 `pthread_once`；该 TU 在 `sbt` 库与 `FileTransferAgent` 中均被编译，故两目标共用同一份实现与标志）：
  ```c
  /* T0389：libobk 入口层一次性加载 rdb config 守卫（pthread_once 线程安全）。
   * pthread_once 保证 init 例程进程内仅执行一次；失败置 g_libobk_rdb_inited=-1，
   * 后续调用均返回失败（fail-closed，且不可重试）；成功置 1；ENOENT（无配置文件）按合法处理。 */
  static pthread_once_t g_libobk_rdb_once = PTHREAD_ONCE_INIT;
  static int g_libobk_rdb_inited = 0;

  static void libobk_rdb_once_init(void)
  {
      char err[256];
      if (init_config(NULL, err, sizeof err) != 0) {
          ErrorLog("rdb-config load failed: %s", err);
          g_libobk_rdb_inited = -1;
          return;
      }
      g_libobk_rdb_inited = 1;
  }

  int libobk_ensure_rdb_config(void)
  {
      pthread_once(&g_libobk_rdb_once, libobk_rdb_once_init);
      return g_libobk_rdb_inited > 0 ? 0 : -1;
  }
  ```
  说明：选用 `pthread_once` 而非"互斥锁+标志"——其一，`pthread_once` 是进程内一次性初始化的地道线程安全惯用法，无重入/死锁风险（锁与 `init_config` 内部 `g_cfg_lock` 无关，且 once 例程不回调用本函数）；其二，fail-closed 要求"配置加载失败即拒绝"，`pthread_once` 失败后所有后续调用均返回 -1，语义正确。代价是失败后不可重试（进程内固化），而本场景配置失败属持续性错误（坏文件/坏 env），无重试必要。
- `oracleCmdTbl.h` 声明 `extern int libobk_ensure_rdb_config(void);`（libobk.c 与 main.c 均 include 该头）。
- `sbtinit`、`sbtinit2`（libobk.c）、`main.c`（FileTransferAgent）三处 `init_config(NULL, ...)` 调用替换为 `libobk_ensure_rdb_config()`。

## 验收标准
- [ ] AC-1: 引入 `libobk_ensure_rdb_config()` 一次性守卫；`sbtinit`、`sbtinit2`、`main.c`(FileTransferAgent) 三处改调守卫，进程内 `init_config` 仅真正执行一次（重复入口/多会话不再重复重解析）。
- [ ] AC-2: `init_config` 自身"每次强制重加载"语义不变——直接调用方（`rdb_config_test`、`param_registry_test`）及 rpc/dmsbtex/fs-backup 入口不受影响。
- [ ] AC-3: `libobk_session_test` 通过（exit 0）；可观测守卫只加载一次（如新增轻量计数/日志断言，或会话测试下无重复加载副作用）。
- [ ] AC-4: 构建通过——`sbt` 库、`FileTransferAgent` 及依赖 rdb-config 的 rpc/dmsbtex/fs-backup/rdbcomm 等目标编译链接不受影响。
- [ ] AC-5: 合法 `0/1` 与 ENOENT 行为不变；非法配置（非 ENOENT）仍 fail-closed（与 T0388 一致）。

## 声明的测试接缝
- seam: libobk/lib/sbt/libobk.c + libobk/main.c -> libs/rdb-config.c（入口 init 守卫）

## 范围外
- 不改 `init_config` 内部实现，不动其他已改入口（rdbcomm/dmsbtex/rpc/fs-backup）的 init 策略。
- 不改 Go(oss) 侧。
- 不处理 `libobk_protocol_test` 既有 `-Werror=unused-variable` 编译阻断（与本次无关）。

## 备注
- 父任务：T0388（confirmed，已归档）。知识：`knowledge/rdb-config/audit-findings.md`、`optim-roadmap.md`（D2 已修复：入口显式 init_config）。
- development 场景，含测试接缝。
