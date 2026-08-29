# D2（T0388）实现计划 + 自我审查（B 重构 · 聚合点策略版）

## 一、自我审查（代码审查结论）

### 1.1 mTLS 缺口更正（T0386 误判）
原 T0386 将 4 处 mtls 消费点标为"直接赋值无 `<0` 校验"，实际查证赋值后已紧跟 `if (<0) 返回错误`：
- `rdbcomm-main.c:569`、`dmsbtex/network.c:106`、`libobk/lib/sbt/libobk.c:71`、`oracleCmdTbl.c:39` 均已硬失败。
- 唯一真实缺口：`rdbcommd-main.c:263`（初始化器直接赋值，无 `<0` 检查）。

### 1.2 rdb_auto_init 缺陷（用户指出 + fs-backup 遗漏）
`rdb_auto_init`（`__attribute__((constructor))`）是生产代码里**唯一** `init_config` 调用点。
两处硬伤：①构造函数无法向 main 返回错误，解析失败（非 ENOENT）静默吞掉；②静态库链接时若 `.o` 未被引用可能被丢弃，配置根本不加载。

**遗漏发现（fs-backup / rpc）**：`init_config` 加载的 `g_param_table` 被两类聚合函数消费：
- `rpc_init_config`（`rpc/rpc-config.cpp:147`）：内部直接 `sec_get_bool/sec_get_str`，**不调 `init_config`**，依赖 constructor。下游入口：`rpc/main.cpp:365`、`rpc/rpc-client.cpp:639`、**fs-backup `fsdeamon/main.cpp:305` 与 `fsclient/main.cpp:540`（经 `set_rpc_init_config`）**、以及所有 `rpc/tests/*`（`set_rpc_init_config`）。
- 三个 TLS config init：`dmsbtex/network.c:sbt_tls_config_init`、`libobk/lib/sbt/libobk.c:sbt_client_tls_config_init`、`oracleCmdTbl.c:sbt_server_tls_config_init`。

若仅按"4 个 main"移除 constructor，fs-backup 与 rpc 全家会读空 `g_param_table`。

### 1.3 入口策略（Do 阶段对原聚合点策略的关键修正）
 原"聚合点策略"（在 `rpc_init_config` / `*_tls_config_init` 内部调 `init_config`）**已撤销**：聚合函数内部 init 与既有测试契约冲突——
 `rpc_config_test` 的 `init_fills_sec_switches_from_store` 先 `parse_config(path)` 再调 `rpc_init_config`，若聚合函数内再 `init_config(NULL)`，会重加载默认路径覆盖测试配置致断言失败；
 且 `init_config` 必须保持"每次强制重加载"语义（否则破坏 `rdb_config_test` 的多次 `init_config` 调用）。

 **最终策略：仅在最外层入口调用 `init_config`**（一处加载，下游聚合函数只读 `g_param_table`），覆盖全部消费方：
 - `rdbcomm/rdbcommd-main.c`、`rdbcomm/rdbcomm-main.c`：main 开头（rdbcommd 另含 mtls 硬失败）。
 - `dmsbtex/main.c`：main 开头（覆盖 `sbt_tls_config_init` 与 `sbt.c` 内调用）。
 - `fs-backup/fsdeamon/main.cpp`、`fs-backup/fsclient/main.cpp`：在 `set_rpc_init_config` 之前。
 - `rpc/main.cpp`、`rpc/rpc-client.cpp`：在 `rpc_init_config` 之前。
 - `libobk/lib/sbt/libobk.c`：`sbtinit2` 与 `sbtinit` 开头（Oracle SBT 库入口）。
 - `libobk/main.c`（`FileTransferAgent` 独立 CLI）：在 `sbt_server_tls_config_init` 之前。
 - `libs/tests/param_registry_test.c`：main 开头（移除 constructor 后显式加载）。
 - 移除 `rdb_auto_init` constructor。

 ### 1.4 幂等与失败语义
 - `init_config` 幂等（同文件重复解析无副作用），但入口策略下各入口各加载一次，无重复覆盖。
 - 失败语义：入口 `init_config` 返回非 0（非 ENOENT）即 `return EXIT_FAILURE` / `return -1`（库入口），fail-closed 传播；库不 `exit`。
 - `param_registry_test.c` 测试环境 ENOENT 合法，忽略错误。

## 二、详细修改计划

### 2.1 `libs/rdb-config.c`（移除 constructor）
删除文件末尾：
```c
__attribute__((constructor)) static void rdb_auto_init(void)
{
	char err[256];
	init_config(NULL, err, sizeof(err));
}
```

### 2.2 `rpc/rpc-config.cpp`：`rpc_init_config` 聚合点（**已撤销**）
 Do 阶段验证发现：在 `rpc_init_config` 内部加 `init_config` 会与 `rpc_config_test` 的"先 `parse_config` 再调 `rpc_init_config`"契约冲突（重加载默认路径覆盖测试配置，致 `init_fills_sec_switches_from_store` 断言失败）。
 改为在**入口**（`rpc/main.cpp`、`rpc/rpc-client.cpp`、`fs-backup` 两 main）调用，见 2.7。

 ### 2.3 三个 TLS config init 聚合点（**已撤销**）
 同理，在 `sbt_tls_config_init` / `sbt_client_tls_config_init` / `sbt_server_tls_config_init` 内部加 `init_config` 会与"先 `parse_config` 再调"的测试契约冲突。
 改为在**入口**（`dmsbtex/main.c`、`libobk` 库/CLI 入口）调用，见 2.7。

### 2.4 `rdbcomm/rdbcommd-main.c`（init + mtls 硬失败）
a) 初始化器 `.mtls_enabled = sec_get_bool(PARAM_RDBCOMMD_MTLS_ENABLED),` → `.mtls_enabled = 0,`
b) `main` 第一行后插入：
```c
	{
		char err[256];
		if (init_config(NULL, err, sizeof err) != 0) {
			fprintf(stderr, "rdbcommd: rdb-config load failed: %s\n", err);
			return EXIT_FAILURE;
		}
	}
```
c) 在 `server_opts.audit_enabled` 检查块之后插入：
```c
	/* D2/T0388：mtls 开关与 audit/auth 一致，非法值启动期硬失败 */
	int mtls_en = sec_get_bool(PARAM_RDBCOMMD_MTLS_ENABLED);
	if (mtls_en < 0) {
		fprintf(stderr,
			"rdbcommd: invalid %s value (expect \"0\"/\"1\")\n",
			RDBCOMMD_MTLS_ENABLE_ENV);
		return EXIT_FAILURE;
	}
	opts.mtls_enabled = mtls_en;
```

### 2.5 `rdbcomm/rdbcomm-main.c`（仅 init；mtls 已硬失败）
`main` 开头插入（与 rdbcommd 同形，`rdbcomm: ` 前缀）：
```c
	{
		char err[256];
		if (init_config(NULL, err, sizeof err) != 0) {
			fprintf(stderr, "rdbcomm: rdb-config load failed: %s\n", err);
			return EXIT_FAILURE;
		}
	}
```
> mtls 已在 580 行 `if (opts.copts.mtls_enabled < 0) return EXIT_FAILURE;`，无需再改。

### 2.6 `libs/tests/param_registry_test.c`（修复对 constructor 的依赖）
 `main(void)` 开头插入：
 ```c
 	char err[256];
 	init_config(NULL, err, sizeof err); /* 移除 constructor 后显式加载；测试环境 ENOENT 合法 */
 ```

 ### 2.7 `init_config` 入口落点（实际实施的全部显式调用）
 - `libs/rdb-config.c`：移除 `rdb_auto_init` constructor（2.1）。
 - `rdbcomm/rdbcommd-main.c`：main 开头 init（硬失败）+ mtls 硬失败块（2.4）。
 - `rdbcomm/rdbcomm-main.c`：main 开头 init（2.5）。
 - `libs/tests/param_registry_test.c`：main 开头 init（2.6）。
 - `dmsbtex/main.c`：main 开头 init（覆盖 `sbt_tls_config_init` 与 `sbt.c` 内调用）。
 - `fs-backup/fsdeamon/main.cpp`、`fs-backup/fsclient/main.cpp`：`set_rpc_init_config` 之前 init。
 - `rpc/main.cpp`、`rpc/rpc-client.cpp`：`rpc_init_config` 之前 init。
 - `libobk/lib/sbt/libobk.c`：`sbtinit2` / `sbtinit` 开头 init（Oracle SBT 库入口）。
 - `libobk/main.c`（`FileTransferAgent`）：`sbt_server_tls_config_init` 之前 init。

## 三、测试计划
- **单元（必过）**：`param_registry_test`（补 init 后不读空）、`rdb_config_test`（已显式）。
- **RPC/fs-backup（经聚合点自动加载）**：`rpc/tests/*`（`set_rpc_init_config` 经 `rpc_init_config` 内部 init）、fs-backup 现有测试。
- **集成（受既有 `-Werror=stringop-truncation` 阻断时走局部编译/手动验证并文档化）**：
  - 非法 rdb.conf（损坏 ini）→ 各 main 启动失败、rpc_init_config 返回失败。
  - `RDBCOMMD_MTLS_ENABLE=2` 启动 rdbcommd → 退出码非 0。
  - 合法 `0/1` 与无配置文件（ENOENT）→ 行为不变。
- **回归**：`sec_get_bool_fail_closed` 等既有用例不受影响。

## 四、向后兼容 / 风险
- 合法 `0/1` 与 ENOENT（无配置）：行为完全不变。
- 非法 mTLS 开关 / 错误 rdb.conf（非 ENOENT）：从"静默当开启/静默吞掉"→"启动失败/初始化失败"（fail-closed 严格化，与 audit/auth 一致）。
- 范围：1 处移除 constructor + 约 10 处新增显式 init 入口（详见 2.7），多为 4~8 行；回归风险低。
- 不改动 `sec_get_bool` 契约、`init_config` 内部（ENOENT→0 保持）。
- C++ 调用点（`rpc-config.cpp`、fs-backup）需 `init_config` 经 `extern "C"` 可见（Do 阶段确认 include）。

## 五、Do 阶段执行顺序
1. 2.1 移除 constructor。
2. 2.2 `rpc_init_config` 聚合点（关键，覆盖 fs-backup/rpc）。
3. 2.3 三个 TLS config init 聚合点。
4. 2.4~2.5 `rdbcommd`（含 mtls 硬失败）、`rdbcomm` main。
5. 2.6 `param_registry_test` 修复。
6. 编译 + 测试回归（全量受阻则局部校验并文档化）。
7. 更新 `knowledge/rdb-config/audit-findings.md`（标 D2 已修复）、`optim-roadmap.md`（fail-closed 一致性项已实施）。
