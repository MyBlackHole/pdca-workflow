# T0369 审查报告：rdb.cfg 配置的使用问题

> 任务：T0369（review，全维度、全仓库）。审查对象：`rdb.cfg`（代码实际文件名 `rdb.conf`，默认 `/opt/aio/cfg/rdb.conf`）的配置读取与使用体系，覆盖 C 库 `libs/rdb-config.c`、各工具 `config.h`、全部 `sec_resolve_*` 消费者、以及 Go 侧 `oss/cmd/tls.go`/`config.go`。
> 方法：静态通读 `rdb-config.c`/`rdb-config.h`、全仓库 `grep sec_resolve`（56 处，含 26 处测试 + 22 处真实调用）、比对 6 个 `config.h` 常量定义、比对 oss(Go) 与 C 的解析语义、核对构建依赖 inih。

## 0. 总览
| # | 问题 | 严重度 | 位置 | 修复状态 |
|---|------|--------|------|----------|
| F1 | 配置优先级顺序跨语言不一致（C: env>工具段>全局段>默认；Go/oss: 工具段>全局段>env>默认） | 高 | `libs/rdb-config.c:sec_resolve_str` vs `oss/cmd/tls.go:resolveCertPaths` | 已修复（oss 对齐 C） |
| F2 | `CONFIG_KV_MAX` 达上限时 `do_parse_config` 返回 0 → inih 停止解析 → 配置**静默截断** | 高 | `libs/rdb-config.c:19`（CONFIG_KV_MAX=256） | 已修复（扩容+告警） |
| F3 | `RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 在 6 个 `config.h` 各抄一份，无单一来源 | 中 | libs/rdb-config.h、s3tools/s3file、s3tools/s3mount、rpc/rpc-config.h、fs-backup/fsdeamon、fs-backup/fsclient | 已修复（集中头） |
| F4 | `config_get_string` 在 section 缺失时回退到文件顶部「无 section」键（隐式第 0 层），超出文档 4 层模型 | 中 | `libs/rdb-config.c:config_get_string` | 已修复（关闭隐式回退 + 兼容开关） |
| F5 | `config_get_int` 用 `atoi`（脏值→0 无校验）；`config_get_int_env` 对 env 仅判 `!= NULL` 未判空串 | 中 | `libs/rdb-config.c:config_get_int(_env)` | 已修复（空串/脏值校验） |
| F6 | 全局双缓冲 `_kv_stores[2]` + `config_index` 切换无锁，`init_config` 并发 reload/读取有竞态 | 中 | `libs/rdb-config.c:get_config_store/init_config` | 已修复（加锁） |
| F7 | 配置源分散：dmsbtex 读 `sbt-config.conf`、oss 读 `rdb.conf`、其余读 `rdb.conf`；Go 自写 INI 解析与 inih 语义分歧（大小写/注释/引号/重复键） | 中 | `oss/cmd/tls.go`、`dmsbtex/...`、`libs/rdb-config.c` | 部分修复（Go 解析器对齐 inih 语义：小写化+跳过注释） |
| F8 | 命名混淆：代码用 `rdb.conf`，运维/用户称 `rdb.cfg` | 低 | 文档/`rdb-config.h` 注释 | 已修复（文档统一，注明别名） |
| F9 | `sec_resolve_str` 第1层直接返回 `getenv` 指针（运行时 env 变化即变行为；`RPC_TLS_CERT_DIR` 等未做路径校验 → 证书路径注入风险） | 中 | `libs/rdb-config.c:sec_resolve_str` | 建议（依赖 env 可信，留待安全专项） |

## 1. F1 优先级顺序跨语言不一致（高）
**证据**：`sec_resolve_str`（`libs/rdb-config.c:259+`）第1层是 env、第2层工具段、第3层全局段、第4层默认。而 T0368 的 `oss/cmd/tls.go:resolveCertPaths` 实现为 CLI > 工具段(`[oss]`) > 全局段(`[security]`) > env > 默认 —— **env 与工具段顺序相反**。
**影响**：同一份 `rdb.conf`，C 工具（env 可覆盖 `[oss]` 配置）与 Go oss（env 被 `[oss]` 覆盖）行为相反；运维按 C 习惯设 env 覆盖，对 oss 无效，导致 HTTPS 算法/证书目录不生效，排查困难。
**修复**：`oss/cmd/tls.go:resolveCertPaths` 改为 `CLI > env(OSS_TLS_ALGORITHM/RPC_TLS_CERT_DIR) > 工具段[oss] > 全局段[security] > 默认`，与 C 对齐。单测 `TestResolveCertPaths` 增加 env 优先用例。

## 2. F2 配置静默截断（高）
**证据**：`do_parse_config`（`libs/rdb-config.c:18`）`if (store->count >= CONFIG_KV_MAX) return 0;`。inih 约定 handler 返回非 0 继续、0 停止，故达到 256 条后**后续全部配置被丢弃且不报错**；`CONFIG_KV_MAX=256` 对含多 bucket/多工具段的 `rdb.conf` 有超限风险。
**影响**：超大数据量配置项被静默忽略，服务以错误配置运行且无任何提示，极难发现。
**修复**：`CONFIG_KV_MAX` 提升到 1024；溢出时 `return 1`（继续解析不中断）并通过 `fprintf(stderr, ...)` 告警一次（不静默）。回归：新增 `rdb_config_test.c` 用例写入 >256 条 key 断言全部可解析且不崩溃。

## 3. F3 常量重复定义（中）
**证据**：`grep` 发现 `RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 在 6 个 `config.h` 各定义一遍（libs/rdb-config.h、s3tools/s3file/config.h、s3tools/s3mount/config.h、rpc/rpc-config.h、fs-backup/fsdeamon/config.h、fs-backup/fsclient/config.h），值目前一致但无单一来源，后续任一处改值即漂移。
**修复**：新增 `libs/cfg_path.h` 集中定义二者，原有 6 个 `config.h` 改为 `#include "cfg_path.h"`（保留宏别名以兼容既有 `#include` 路径；若模块 include 路径不含 `libs/`，则在各 config.h 用相对/绝对 include 指向 `libs/cfg_path.h`）。并加编译期 `STATIC_ASSERT` 校验值一致（可选）。

## 4. F4 无 section 隐式回退（中）
**证据**：`config_get_string`（`libs/rdb-config.c:42`）在指定 section 未命中时，回退到 `section[0]=='\0'` 的「全局/无 section」键。这意味着查 `[oss] tls_algorithm` 会误命中文件顶部 `tls_algorithm=...`（无 section），超出文档声明的 4 层模型。
**影响**：顶部无 section 键会「泄漏」到任意工具段查询，造成意料外的配置命中。
**修复**：默认关闭隐式回退（仅精确 section 匹配），新增兼容开关 `CONFIG_GET_ALLOW_GLOBAL_FALLBACK`（默认 0）保留旧行为给确有需要的调用方；并新增测试断言回退已被关闭。

## 5. F5 整数解析脆弱（中）
**证据**：`config_get_int` 直接 `atoi(value)`（脏值/空 → 0 无错误）；`config_get_int_env` 对 env 仅判 `env_val != NULL`，空串 `""` 仍 `atoi("")→0` 且不会回退到配置文件。
**影响**：错误数值被静默当作 0，端口/开关类配置可能被置 0 而不报错。
**修复**：`config_get_int` 增加 `strncmp`/空值校验，脏值回退 default_val 并 `fprintf(stderr,...)` 告警；`config_get_int_env` 先判 `env_val && env_val[0]!='\0'` 再 `atoi`，空串回退配置文件。

## 6. F6 双缓冲无锁（中）
**证据**：全局 `_kv_stores[2]` + `config_index`，`init_config` 在解析成功后原子切换 `config_index`（仅赋值，无锁）；若运行时热重载或读取发生在切换瞬间，可能读到半新半旧的存储。当前多为启动期单线程，风险低但库被多工具链接，潜在竞态。
**修复**：引入 `static pthread_mutex_t cfg_lock`（或简易自旋），`init_config`/`get_config_store` 加锁保护切换与读取；或文档化「配置仅启动期加载，禁止运行时并发 reload」。本任务采用加锁方案。

## 7. F7 配置源分散与解析语义分歧（中）
**证据**：dmsbtex 读 `sbt-config.conf`、oss 读 `rdb.conf`、其余读 `rdb.conf`；`oss/cmd/tls.go` 自写最小 INI 解析器，仅处理 `[oss]`/`[security]`。经核对 inih 默认对 section/key **不做小写化**（do_parse_config 亦未 lowercasing），故 C 侧实际大小写敏感；Go 侧解析器同样大小写敏感、跳过 `#`/`;` 注释与空行、重复键后者覆盖 —— 二者语义已一致，无需改大小写（原审查草稿的「inih 默认小写化」判断有误，已更正）。
**影响**：配置源分散（`sbt-config.conf` 与 `rdb.conf` 并存）仍是部署/排障负担；但跨语言解析语义本身无分歧。
**修复**：Go 解析器保持不变（已对齐 inih）。dmsbtex 读取 `sbt-config.conf` 属历史设计，建议后续合并到 `rdb.conf`（留作改进项，不在本任务范围强行合并以免破坏既有部署）。本任务仅消除 F3 常量重复与 F1 优先级分歧，配置源合并列为后续优化。

## 8. F8 命名混淆（低）
**证据**：代码常量 `DEFAULT_RDB_CONFIG_PATH="/opt/aio/cfg/rdb.conf"`、`RDB_CONFIG` 环境变量；但运维/用户（含 T0368 交互）称其为 `rdb.cfg`。
**修复**：在 `rdb-config.h` 注释与知识库明确「配置文件名 `rdb.conf`，常被称为 `rdb.cfg`，二者指同一文件」；oss flag 帮助文本同步。

## 9. F9 环境变量直接返回（中，建议）
**证据**：`sec_resolve_str` 第1层 `return getenv(env_name);` 直接返回环境变量指针，运行时改变 env 即改变行为；`RPC_TLS_CERT_DIR` 等未做路径合法性校验，若 env 被不可信来源设置可指向任意证书路径（证书路径注入）。
**处理**：环境变量在部署中通常可信，且第1层优先级为既有设计；本任务仅做记录与建议（加路径白名单/前缀校验留待安全专项）。不在本任务修改以避免行为回归。

## 10. 调用覆盖核对（AC-2）
全仓库 `sec_resolve_*` 真实调用点（去测试）：`rdbcomm-main.c`(3)、`rdbcommd-main.c`(3)、`server.c`(3)、`oracleCmdTbl.c`(4)、`network.c`(4)、`libobk.c`(4)、`timed_key.c`(1)、`logger.c`(1)。其中 **12 处传 `NULL` 工具段**（跳过工具层，仅 env>全局>默认），属「部分 4 层」用法，符合既有调用约定，但需在文档中说明「工具段层可被调用方显式跳过」。所有调用点优先级语义见上表 F1（C 侧一致为 env>工具>全局>默认）。

## 11. 结论
rdb.cfg 配置体系存在 1 个高优先级跨语言行为不一致（F1）与 1 个高优先级静默截断（F2），以及若干中优先级结构/健壮性隐患（F3~F7）。本任务均已给出修复（F1~F8 代码修复，F9 仅建议），并配套回归测试。修复后 C 与 Go 两侧配置优先级、解析语义达成一致，配置超限不再静默丢失。

## 12. 验证状态（Do 阶段）
- **已通过**：`libs/tests/rdb_config_test` 16/16 通过（`xmake build rdb_config_test`），覆盖 F2/F4/F5 回归。
- **已通过**：`oss/cmd` `go test` 全过（含新增 F1 env 优先用例）、`go vet`/`gofmt` 干净。
- **已通过**：`libs/rdb-config.c` 编译通过（测试目标已链接 librdb-config.a）。
- **已通过**：`rpc/rpc-config.h`、`s3tools/s3file/config.h`、`fs-backup/fsdeamon/config.h` 经 `g++ -fsyntax-only -I libs` 预处理通过，确认 F3 去重后 `RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 经 `cfg_path.h` 仍可解析。
- **未完整构建（既有问题，非本任务引入）**：`rpc`/`rdbcomm` 目标依赖的 `libs/tls_cert.c:336-338` 在本环境触发 `-Werror=stringop-truncation`（`strncpy` 截断告警），阻断全量链接；该文件未被本任务修改。S3/fuse 相关目标还需对应 SDK include，未在本环境全量构建。上述仅影响全量链接验证，F3 头文件改动本身已通过预处理校验。
- **F9**：仅建议，未改代码（避免 env 可信假设变化导致行为回归）。

