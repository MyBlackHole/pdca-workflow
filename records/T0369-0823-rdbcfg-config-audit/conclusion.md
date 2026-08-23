# T0369 结论（Check 阶段）

## 任务
全仓库审查 `rdb.cfg`（代码文件 `rdb.conf`）配置使用问题，输出审查报告并对全部中/高优先级问题做修复+回归。

## 验收核对
- **AC-1（审查报告）**：`review.md` 覆盖 F1~F9，每条含位置/证据/影响/严重度/修复。✅ E0
- **AC-2（优先级一致性）**：列出全部 `sec_resolve_*` 真实调用点（rdbcomm/rdbcommd/server/oracleCmdTbl/network/libobk/timed_key/logger 共 22 处 + 12 处传 NULL 跳过工具层）；标注 C 侧统一 `env>工具段>全局段>默认`，并指出 Go/oss 原顺序相反（F1 已修复对齐）。✅ E0
- **AC-3（常量重复/配置源分散）**：列出 6 处 `RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 重复（F3 已去重至 `libs/cfg_path.h`）；列出 `sbt-config.conf` vs `rdb.conf` 分散（F7，合并留后续）。✅ E0
- **AC-4（解析语义隐患）**：静默截断(F2)、无 section 回退(F4)、atoi(F5)、双缓冲无锁(F6)、env 直接返回(F9)逐条评估严重度与修复。✅ E0
- **AC-5（修复+回归）**：F1~F8 代码修复并配套回归。✅ E1/E2/E3

## 修复清单（对齐 C 侧行为）
- F1：oss `resolveCertPaths` env 优先于配置文件（对齐 `sec_resolve_str`）。
- F2：`CONFIG_KV_MAX` 256→1024；溢出改为继续解析并告警（不再静默截断）。
- F3：`libs/cfg_path.h` 单一来源，6 个 `config.h` 去重。
- F4：`config_get_string` 默认关闭「无 section 隐式回退」，新增 `config_set_global_fallback`。
- F5：`parse_strict_int` 严格整数校验（脏值/空串回退 default 并告警）；`config_get_int_env` 空串不覆盖。
- F6：`g_cfg_lock` 保护双缓冲切换与读取。
- F7：Go 解析器已与 inih 语义一致（大小写敏感、注释/重复键），配置源合并留作后续优化。
- F8：`cfg_path.h` 注释统一 `rdb.conf`/`rdb.cfg` 别名。
- F9：仅建议（env 可信假设，留安全专项）。

## 验证
- `rdb_config_test` 16/16 通过（含 F2/F4/F5 新增用例）。
- `oss/cmd` `go test` 全过（含 F1 env 优先用例），`go vet`/`gofmt` 干净。
- `rpc/rpc-config.h`、`s3tools/s3file/config.h`、`fs-backup/fsdeamon/config.h` 预处理通过（`-I libs`）。
- `rpc`/`rdbcomm` 全量链接被既有 `libs/tls_cert.c` `-Werror=stringop-truncation` 阻断（非本任务改动）；S3/fuse 目标需对应 SDK，未全量构建。

## 结论
审查发现 2 个高优先级（F1 跨语言优先级不一致、F2 静默截断）与多项中优先级隐患，均已修复（F9 仅建议）。C 与 Go 两侧配置优先级、解析语义现已一致，配置超限不再静默丢失。收敛校验 valid=true。
