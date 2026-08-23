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
- 构建环境：`libs/tls_cert.c:336-338` 触发 `-Werror=stringop-truncation`（strncpy 截断告警），阻断 `rpc`/`rdbcomm` 全量链接；该问题非 T0369 引入，需独立修复。

## 回归测试
- `libs/tests/rdb_config_test.c`：16/16（含 F2/F4/F5 用例）。
- `oss/cmd/oss_https_test.go`：`TestResolveCertPaths` 含 F1 env 优先用例。
