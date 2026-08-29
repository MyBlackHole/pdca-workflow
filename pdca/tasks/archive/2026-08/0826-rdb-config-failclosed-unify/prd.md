# 跟进 T0386：rdb config fail-closed 一致性

## 问题陈述
T0386 分析发现：全部 `mtls_enabled` 消费点对 `sec_get_bool` 的返回值**直接赋值、无 `<0` 校验**，而 `rdbcommd-main.c` 中 audit/auth 开关对非法 `-1` 采用**启动期硬失败**（`if (<0) return EXIT_FAILURE`）。二者行为不一致。当前 mTLS 的"直接赋值"因 C 中 `-1` 作真值而被当作"开启"，**对 mTLS 安全（fail-closed 开启）**，但依赖"-1 当真"的隐式巧合而非显式设计；若未来某消费点改为 `== 1` 精确比较会出错。本任务统一 mTLS 开关的非法值处理，消除隐式巧合、与 fail-closed � 安全哲学对齐。

## 初步事实（Triage 已查证）
- 5 处直接赋值（无 `<0` 校验）：
  - `rdbcomm/rdbcommd-main.c:263` `.mtls_enabled = sec_get_bool(PARAM_RDBCOMMD_MTLS_ENABLED)`
  - `rdbcomm/rdbcomm-main.c:569` `.mtls_enabled = sec_get_bool(PARAM_RDBCOMM_MTLS_ENABLED)`
  - `dmsbtex/network.c:106` `cfg->mtls_enabled = sec_get_bool(PARAM_SBT_MTLS_ENABLED)`
  - `libobk/lib/sbt/libobk.c:71` `ctx->tls_mtls_enabled = sec_get_bool(PARAM_SBT_MTLS_ENABLED)`
  - `libobk/lib/logic/oracleCmdTbl.c:39` `cfg->mtls_enabled = sec_get_bool(PARAM_SBT_MTLS_ENABLED)`
- 对照：`rdbcommd-main.c:271/279` audit/auth 有 `if (server_opts.x < 0) return EXIT_FAILURE` 硬失败。
- 鉴权/审计调用方（`timed_key.c:229`、`logger.c:121`）的 `-1` 处理已正确（fail-closed 维持开启）。

## 方案方向（已确认：B 实施-硬失败 + 显式 init_config 重构）
**自我审查发现（更正 T0386 误判）**：原 T0386 §4 表将 4 处库/客户端 mtls 消费点标为"直接赋值无 `<0` 校验"，实际查证其在 `sec_get_bool` 赋值后**已紧跟 `if (<0) 返回错误`**（rdbcomm:569 / dmsbtex:106 / libobk:71 / oracleCmdTbl:39 均已硬失败）。真实缺口仅 `rdbcommd-main.c:263` 一处 mtls 直接赋值无检查。

**本任务做两件事，统一为 fail-closed 硬失败模型**：

### (1) mTLS 开关：补 rdbcommd 一处硬失败
将 `rdbcommd-main.c` 初始化器中的 `.mtls_enabled = sec_get_bool(...)` 移到 main 体内并加 `<0` 硬失败（与同文件 audit/auth 一致）：
```c
int mtls_en = sec_get_bool(PARAM_RDBCOMMD_MTLS_ENABLED);
if (mtls_en < 0) {
    fprintf(stderr, "rdbcommd: invalid %s value (expect \"0\"/\"1\")\n",
            RDBCOMMD_MTLS_ENABLE_ENV);
    return EXIT_FAILURE;
}
opts.mtls_enabled = mtls_en;
```
其余 4 处已硬失败，无需改动。

### (2) 配置加载：移除 constructor，改为聚合点显式 init_config + 失败传播（B 重构）
`rdb_auto_init`（`__attribute__((constructor))`）是全局唯一 `init_config` 生产调用点，存在两处硬伤：①构造函数无法向 main 返回错误，只能静默吞掉解析失败；②静态库链接时若 `.o` 未被引用可能被丢弃，导致配置根本不加载。`init_config` 幂等（重复解析同文件无副作用）。

**重构策略（Do 阶段修正为入口策略）**：仅在**最外层入口**显式调用 `init_config`（一处加载，下游聚合函数只读 `g_param_table`）。原"聚合函数内部 init"方案在 Do 验证中被撤销——`rpc_config_test` 的 `init_fills_sec_switches_from_store` 先 `parse_config(path)` 再调 `rpc_init_config`，若聚合函数内再 `init_config(NULL)` 会重加载默认路径覆盖测试配置致断言失败；且 `init_config` 须保持"每次强制重加载"语义（否则破坏 `rdb_config_test` 多次调用）。
- **入口显式 `init_config` 落点**：`rdbcomm/rdbcommd-main.c`、`rdbcomm/rdbcomm-main.c`、`dmsbtex/main.c`、`fs-backup/fsdeamon/main.cpp`、`fs-backup/fsclient/main.cpp`（均在 `set_rpc_init_config`/`rpc_init_config` 之前）、`rpc/main.cpp`、`rpc/rpc-client.cpp`（均在 `rpc_init_config` 之前）、`libobk/lib/sbt/libobk.c` 的 `sbtinit`/`sbtinit2`（Oracle SBT 库入口）、`libobk/main.c`（`FileTransferAgent` 独立 CLI，在 `sbt_server_tls_config_init` 之前）。覆盖 rpc / fs-backup / dmsbtex / libobk / oracleCmdTbl 全部消费方。
- **`rdbcomm/rdbcommd-main.c` main 开头加 `init_config`**：失败 `return EXIT_FAILURE`。`rdbcomm-main.c` 同样处理。
- **测试**（`libs/tests/param_registry_test.c`）：其 main 从未显式调 `init_config`，依赖 constructor；移除后须补 `init_config(NULL, err, sizeof err)`。`rdb_config_test.c` 已显式调用，不受影响；rpc 测试各自经入口或自身 `parse_config` 加载。
- **移除** `libs/rdb-config.c` 的 `rdb_auto_init` constructor。
- 失败语义：入口 `init_config` 返回非 0（非 ENOENT）即 `return EXIT_FAILURE` / 库入口 `return -1`，fail-closed 传播；库不 `exit`。

合法 `0/1` 与 ENOENT 行为不变；非法 mTLS 开关与非法/错误配置（非 ENOENT）从"静默当开启/静默吞掉"改为"启动失败/初始化失败"，与 fail-closed 一致。

## 验收标准
- [ ] AC-1: 自我审查确认 4 处 mtls 消费点（rdbcomm:569、dmsbtex:106、libobk:71、oracleCmdTbl:39）已有 `<0` 硬失败；仅 `rdbcommd-main.c:263` 补上非法 `-1` 的硬失败（`return EXIT_FAILURE`），全局一致。
- [ ] AC-2: 移除 `libs/rdb-config.c` 的 `rdb_auto_init` constructor；`init_config` 不再有生产自动调用。
- [ ] AC-3: 入口策略——rpc 全家（rpc main / rpc-client / **fs-backup（fsdeamon、fsclient）**）在 `rpc_init_config` 之前显式 `init_config`（而非在 `rpc_init_config` 内部）；失败（非 ENOENT）`return EXIT_FAILURE` / 返回错误码。
- [ ] AC-4: 入口策略——`dmsbtex/main.c`、`libobk`（`sbtinit`/`sbtinit2` 库入口、`FileTransferAgent` CLI）在进入各自 TLS config init 之前显式 `init_config`，覆盖 dmsbtex/libobk/oracleCmdTbl。
- [ ] AC-5: `rdbcomm/rdbcommd-main.c` main 开头显式 `init_config`（`rdbcomm-main.c` 同），失败 `return EXIT_FAILURE`。
- [ ] AC-6: `param_registry_test.c` main 开头补 `init_config`，移除 constructor 后测试不读空配置（`rdb_config_test.c`、rpc 测试经入口/自身 parse 加载，不受影响）。
- [ ] AC-7: 合法 `0`/`1` 与 ENOENT 行为不变；非法 mTLS 开关（如 `"2"`）下 rdbcommd 启动失败；非法/错误 rdb.conf（非 ENOENT）下 main/聚合函数初始化失败。
- [ ] AC-8: 构建验证——rdbcomm/rdbcommd/dmsbtex/libobk/rpc/fs-backup 目标编译通过（既有 `-Werror=stringop-truncation` 阻断项不属本任务）；`param_registry_test` 与 `rdb_config_test` 全过。

## 声明的测试接缝
### 声明的测试接缝
- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c

## 范围外
- 不改 audit/auth 的硬失败模型（保持最严）。
- 不处理 Go(oss) 侧（背景）。
- 不动 `sec_get_bool` 自身契约（仍返回 -1 表示非法）。

## 备注
- 父任务：T0386（confirmed）。知识：`knowledge/rdb-config/optim-roadmap.md`、`knowledge/rdb-config/audit-findings.md`。
- development 场景，含测试接缝（P3.5）。
