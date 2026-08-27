# Triage Brief — T3988 服务端 mTLS 启用且指定算法时算法对应证书异常应启动失败

## 分类与查重
- 类型：**bug（fail-closed 不完整）**，scenario_type=bugfix。
- 关联任务：
  - **T3987**（已归档）：收口"mTLS 启用 + 证书目录/证书缺失 → 启动失败"。本任务是其**精细化扩展**——进一步要求"mTLS 启用**且指定算法**时，该算法自身的证书异常也必须启动失败，而非被另一算法的证书兜底成功"。
  - **T3961**：tls_algorithm 无默认值、算法锁与非法算法名 fail-closed（解析层）。本任务在**启动期证书加载层**补齐同语义。
  - **T0390**：双算法链"尽力收集、单算法失败降级跳过"——正是本任务要绕过的兜底语义（仅在指定算法时）。
- 查重：无重复 open task；archive 中 T3987 仅覆盖"目录/证书缺失"，未覆盖"指定算法但仅该算法证书异常"。

## Claim 验证（代码事实，非询问）
- `libs/tls_cert.h:57-62`：`tls_cert_server_options_t` **仅含 `mtls_enabled` 与 `cert_dir`**，无 `algorithm` 字段；注释"内部自动构建 SM4+AES 双算法链"。
- `libs/tls_cert.c:638-700` `tls_cert_init_server`：`tls_cert_build_server_profiles` 硬编码生成 SM4+AES 两个 profile（与文件是否存在无关，见 `:384-416`），循环加载时单算法 `slot_create` 失败仅 `continue` 跳过（`:669-692`，注释 T0390"不连坐其他算法"），全部失败才整体失败。
  - 推论：指定 SM4 但 SM4 文件缺失、AES 文件存在 → init_server 仍整体 `TLS_CERT_OK`（AES slot 成功）→ **不启动失败**。❌ 违反新需求。
- 四服务端均已有算法配置（值格式 `TLS_SM4_GCM_SM3`/`TLS_AES_256_GCM_SHA384`，与 `libs/common.h:15-16` 常量一致），但**均未把 algorithm 传入 init_server**：
  - rdbcommd `server_options.algorithm_name`（`rdbcomm/server.h:24`）+ CLI `--tls-algorithm`（`:33`）。
  - aio-speedd `g_rpc_config->tls_algorithm[128]`（`rpc/rpc-config.h:29`）。
  - dm-ftp `dmsbtex_tls_config_t.algorithm_name`（`dmsbtex/network.c:156`）；`sbt_session_server_prepare` 仅设 `mtls_enabled`+`cert_dir`（`:371-382`）。
  - sbt `libobk_tls_config_t.algorithm_name`；`sbt_session_server_prepare` 同构（`:194-204`）。

## 根因
服务端证书加载层 `tls_cert_init_server` 不接受"指定算法"，恒走双算法链且对单算法失败降级跳过；故"指定算法 + 该算法证书异常"被另一算法的成功兜底，未触发启动失败。

## 任务骨架
- 范围：libs 证书加载层增加"指定算法 → 仅加载该算法、失败即整体失败"分支；四服务端将各自算法配置传入启动期 TLS 准备。
- 不改动：客户端握手、`tls_cert_init_server` 未指定算法时的双算法链兼容语义、国密后端、算法白名单解析（T3961）。
- 验收：四服务端在"指定算法 + 该算法证书异常"时启动失败；未指定算法时保持双算法链兼容不回归。
