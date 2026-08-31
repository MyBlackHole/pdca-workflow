---
schema: pdca.asset/v1
id: ontology:domain/rdb-config-audit-findings
type: domain
layer: Knowledge
status: active
summary: rdb.conf 配置解析契约与审计结论（T0369）
domain:
- ontology:domain/rdb-config
relations:
  specializes:
  - ontology:domain/rdb-config
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# rdb.conf 配置解析契约与审计结论（T0369）

## 配置文件身份
- 代码文件名 `rdb.conf`，默认路径 `DEFAULT_RDB_CONFIG_PATH=/opt/aio/cfg/rdb.conf`；运维/用户常称 `rdb.cfg`，二者指同一文件。
- 常量单一来源：`libs/cfg_path.h`（T0369 F3 去重，原 6 处 config.h 重复定义已移除）。

## 4 层解析契约（C 侧 `libs/rdb-config.c`）
`sec_resolve_str/int/bool` 优先级（**权威定义**）：
1. 环境变量（env）
2. 工具段（如 `[oss]`/`[rdbcomm]` 的 key）
3. 全局段（`[security]` 的 key）
4. 默认值

> 跨语言一致性红线：Go 侧（oss）`resolveCertPaths` 的 `chooseStr` 必须保持 `CLI > env > 配置文件 > 默认`，
> 即 env 高于工具段/全局段（修复前 oss 曾把 env 放在工具段之后，与 C 不一致 → T0369 F1）。

## 解析语义（inih 对齐）
- section/key **大小写敏感**（inih 默认不 lowercasing，C 的 do_parse_config 亦未 lowercasing）。
- 跳过 `#`/`;` 注释与空行；重复 key 后者覆盖（do_parse_config 从 count-1 倒序遍历）。
- `config_get_string` **默认不做**「工具段 → 文件顶部无 section 键」隐式回退（T0369 F4 关闭，原会误命中顶部键）；如需回退调用 `config_set_global_fallback(1)`。
- `config_get_int` 经 `parse_strict_int` 严格校验，脏值/空串回退 default 并告警（不再静默当 0）。
- `CONFIG_KV_MAX=1024`；达上限时 `do_parse_config` 返回 1（继续解析）并告警一次，不再静默截断（T0369 F2）。
- 双缓冲 `_kv_stores[2]` 切换由 `g_cfg_lock`（pthread_mutex）保护（T0369 F6）。

## 已知未修复项
- **F9（中，仅建议）**：`sec_resolve_str` 第1层直接返回 `getenv` 指针，运行时 env 变化即变行为；`RPC_TLS_CERT_DIR` 等未做路径校验（证书路径注入风险，依赖 env 可信）。留安全专项。
- **F7 配置源分散**：dmsbtex 仍读 `sbt-config.conf`，与 `rdb.conf` 并存；合并到统一配置源列为后续优化，未强行合并以免破坏既有部署。
- 构建环境（`tls_cert.c` 截断阻断，**已修正/作废**）：原记 `libs/tls_cert.c:336-338` 触发 `-Werror=stringop-truncation` 实为过时——代码已改 `safe_strcpy`，且提交 `57fca54` 已修复 xmake test 的 `-Werror` 阻断；T0390 重新审查实证重编 `tls_cert.c` 仅余无关弃用告警（`X509_NAME_get_text_by_NID`）并正常归档 `libtls_cert.a`。该"未修复"记录作废。

## 配置加载入口（T0388/D2 已修复）
- **原缺陷**：生产代码唯一 `init_config` 调用点是 `__attribute__((constructor))` 的 `rdb_auto_init`（`libs/rdb-config.c`），两硬伤：①构造函数无法向 main 返回错误，解析失败（非 ENOENT）静默吞掉；②静态库链接时 `.o` 未被引用可能被丢弃，配置根本不加载。
- **修复（方案 B 重构）**：移除 `rdb_auto_init` constructor，改为在**最外层入口**显式调用 `init_config`（fail-closed：非 ENOENT 错误 → `return EXIT_FAILURE` / 库入口 `return -1`）。入口清单：rdbcommd-main / rdbcomm-main / dmsbtex-main / fs-backup fsdeamon+fsclient main / rpc main+rpc-client / libobk `sbtinit`+`sbtinit2`（Oracle SBT 库）/ libobk `FileTransferAgent` CLI / `param_registry_test.c`。
- **mtls 硬失败**：`rdbcommd-main.c` 在 audit/auth 硬失败块之后新增 mtls 开关 `<0` 硬失败（与 audit/auth 一致）；其余 mtls 消费点此前已具备 `<0` 校验。
- **策略要点**：`init_config` 必须保持"每次强制重加载"语义；**不可**在 `rpc_init_config` / `*_tls_config_init` 等聚合函数内部调用（会与"先 `parse_config` 再调聚合函数"的测试契约冲突，且会覆盖测试配置）。入口加载、聚合函数只读 `g_param_table`。
- 合法 `0/1` 与 ENOENT（无配置文件）行为不变；非法开关 / 错误 rdb.conf（非 ENOENT）从静默改为启动/初始化失败。

## 回归测试
- `libs/tests/rdb_config_test.c`：15/15（含 F2/F4/F5 用例；注：原 16 计数含一次重复用例，实测 15 项全过）。
- `libs/tests/param_registry_test.c`：9/9（sec_get_bool fail-closed、audit/auth env 等）。
- `rpc/tests/rpc_config_test.cpp`：4/4（init_fills / env override / invalid audit env fails / reload）。
- `libobk/test/session_test.c`（`libobk_session_test`）：通过（exit 0，覆盖 sbt client/server tls config init）。
- `oss/cmd/oss_https_test.go`：`TestResolveCertPaths` 含 F1 env 优先用例。

## 入口重复初始化收敛（T0389 已修复）
- **原缺陷**：libobk 在 `sbtinit`（`libobk/lib/sbt/libobk.c`）、`sbtinit2`（同文件）、`main.c`（FileTransferAgent CLI）三处各自调用 `init_config(NULL, ...)`。Oracle SBT 调用序为 `sbtinit` 一次 + `sbtinit2` 多次（每会话一次、可能并发），导致 `init_config` 被重复执行（重复解析 rdb config，效率与可观测性差）。
- **修复（线程安全一次性守卫）**：新增 `libobk_ensure_rdb_config()`，采用 `pthread_once`（POSIX 进程内一次性初始化惯用法），定义于 `oracleCmdTbl.c`（该 TU 同时被 `sbt` 库与 `FileTransferAgent` 编译，两目标共用同一份实现与标志）。三处入口改调守卫；守卫以三态记录结果（`0`=未初始化 / `1`=成功 / `-1`=失败），失败后所有调用均返回 `-1`（fail-closed，不可重试——符合"配置加载失败即拒绝"语义）。
- **未改动** `init_config` 内部实现，其"每次强制重加载"语义保持不变（T0388 为 `rdb_config_test` 刻意保留）；守卫只在 libobk 入口层生效。
- 验收：5 条 AC 全过（`libobk_session_test`、`rdb_config_test` 15/15、`param_registry_test` 9/9、`rpc_config_test` 4/4 均通过，`sbt`/`FileTransferAgent` 及依赖目标构建正常）。

## libobk_protocol_test 构建阻断（T0390 已修复）
- **原问题**：`libobk/test/protocol_test.c` 在 release（`-DNDEBUG`）构建下编译失败：`-Werror=uninitialized`（`fds` 未初始化）+ `-Werror=unused-variable`（`head`/`body`/`expect`）。
- **根因**：测试用 `assert()` 做 `socketpair` 初始化与 `_baseSend`/`_baseRecv` 结果校验；release 下 `assert` 展开为空，导致 `fds` 未初始化、且收发调用被死代码消除后相关变量判定未使用。被测逻辑（`_baseSend`/`_baseRecv`/`obk_hs_session_init_plain`，由 `sbt` 库提供）正确无误。
- **修复**：全部 `assert(...)` 改为真实错误检查（`if (...) { fprintf(stderr,...); return 1; }`），补 `#include <stdio.h>`；仅改测试错误检查方式，被测逻辑不动。debug/release 均 `build ok` 且运行 `exit 0`。

## mTLS 生产上下文最低 TLS 版本显式锁定（T0391 已修复 / F1）
- **F1（中危）**：`libs/tls_cert.c` 的 `tls_cert_slot_create` 原仅 `SSL_CTX_new(TLS_method())` 创建上下文，未显式设最低协议版本，依赖 OpenSSL 默认（OpenSSL4 默认最低 TLS1.2）+「仅配置 TLS1.3 套件」的隐式约束。纵深防御不足：若未来套件配置放宽或默认值变化，可能协商到弱版本。
- **修复**：`SSL_CTX_new` 成功后新增 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`，失败即 fail-closed（`SSL_CTX_free` + 返回 `TLS_CERT_ERR_SSL_CREATE`）。server/client 共用该函数，一处覆盖全部生产上下文。
- **覆盖性**：全仓生产 `.c/.cpp` 中 `SSL_CTX_new` 仅出现在 `libs/tls_cert.c:236`（已修复）、`libs/tls_keygen.c:1529/1534`（工具，自身已设 TLS1_3）、`libs/tests/tls_cert_test.c`（测试）。rpc/dmsbtex/libobk/rdbcomm 均无直接 `SSL_CTX_new`，全部经 `tls_cert_init_*` / `*_handshake` / `*_ctx_acquire` 间接到达 → 无绕过路径。
- **回归测试**：`libs/tests/tls_cert_test.c` 新增 `tls_cert_min_proto_version_enforced`，经 `tls_cert_get_ssl_ctx` 取 AES/SM4 两 slot 的 `SSL_CTX`，断言 `SSL_CTX_get_min_proto_version == TLS1_3_VERSION`。可判别：无修复时 OpenSSL4 默认最低 TLS1.2，断言必失败。运行 20/20 通过。
- **适用范围/限制**：仅作用域 `libs/tls_cert.c` 生产上下文；不影响握手/验证回调/套件逻辑。F2（CRL 强制）/F3（GET_TIME 豁免）/F5（subject 白名单）为独立后续项；F4（dmsbtex 强制分散）经复查为误报，详见下节。

## mTLS 全面安全审查结论（T0392）
- **总体判定**：五道 mTLS 防线（配置 fail-closed / 握手强制 / 降级拒绝 / 算法白名单 / 证书·CA 绑定 / 最低 TLS 版本）全部 fail-closed 一致，**无高危缺陷**。F1（中危，生产上下文未显式设最低 TLS 版本）已由 T0391 修复并验证。
- **覆盖性审计**：全仓生产 `.c/.cpp` 仅 `libs/tls_cert.c:236` 一处 `SSL_CTX_new`（F1 已修复）；`libs/tls_keygen.c` 工具自身已设 TLS1_3；rpc/dmsbtex/libobk/rdbcomm 无直接创建，全部经 `tls_cert_init_*` / `*_handshake` / `*_ctx_acquire` 间接到达 → 修复无绕过路径。
- **遗留建议（F2–F5，低危/一致性）**：
  - F2：CRL 仅当 `crl.pem` 存在才启用，无 OCSP；高安全场景建议强制吊销检查。
  - F3：`rpc/rpc-server.cpp:400` 对 `MT_GET_TIME` 做预握手豁免，mTLS 强制下仍可明文送达，建议收紧。
  - F4（已复查为误报）：原认为 `dmsbtex/network.c` `dm_server_handshake` 不检查 `mtls_enabled` 与其余三者不一致；实际 `mtls_enabled=0` 表示「不强制（可选）」，握手函数在客户端主动发起 mTLS 时本就应当按 ctx 是否存在（能力）决定是否执行，与 rpc/rdbcomm/libobk 一致（握手层查能力、业务帧层查是否强制）。原实现 `if (!sbt_server_ctx)` 正确，无需改动。
  - F5：`tls_cert_verify_peer_cn` 仅校 issuer CN，未校 subject CN/SAN 白名单（标准 mTLS PKI 语义），按需补充。
- 完整证据见 `pdca/tasks/0826-mtls-comprehensive-review/review-report.md` 与 `records/T0392-0826-mtls-comprehensive-review/`。

## dmsbtex dm_server_handshake 强制逻辑复查（T0393 误报 / F4）
- **F4（误报，低危/一致性，已撤回）**：原判断 `dmsbtex/network.c` `dm_server_handshake` 不检查 `mtls_enabled` 与其余三者不一致。经语义确认 `mtls_enabled=0` 表示「不强制（mTLS 可选/明文允许）」：握手函数仅在客户端主动发 `CMD_HANDSHAKE` 时被调用，此时应按「ctx 是否存在（能力）」决定是否执行 mTLS，而非按 `mtls_enabled` 拒绝。原实现 `if (!sbt_server_ctx)` 行为正确，且与 rpc/rdbcomm/libobk 一致（握手层查能力、业务帧层 `main.c:271` 查是否强制）。
- **交叉核对（mtls=0=可选，四模块一致）**：rpc `rpc-server.cpp:284` 仅在 `mtls_enabled` 时校验，`else`(L339) 分支客户端要 mTLS 且 `sctx` 存在即照常做 mTLS（可选）；rdbcomm `server.c:496` `if(!sctx)` 才拒、`mtls_enabled` 不参与握手拒绝；libobk `oracleCmdTbl.c:119` `if(!sbt_server_ctx)` 才拒；dmsbtex 原 `network.c:211` `if(!sbt_server_ctx)` 才拒。四者强制（"必须 mTLS"）均落在业务帧层按 `mtls_enabled` 把关（rpc/rdbcomm/libobk 对应帧层 + dmsbtex `main.c:271`）。故原 dmsbtex 握手逻辑与三者对齐，F4 为误报。
- **处置**：T0393 修复（`|| !cfg->mtls_enabled` 拒握手 + 区分性用例）已撤销；代码仓 `git revert b79b3b0`（commit `204f048`），`dmsbtex_session_test` 全 PASS、原 `no-downgrade reject` 行为完好。F4 重新定性为审查误报，无代码改动。
- **状态**：F4 关闭（误报，无需修复）；mTLS 审查遗留候选仅 F2/F3/F5。
