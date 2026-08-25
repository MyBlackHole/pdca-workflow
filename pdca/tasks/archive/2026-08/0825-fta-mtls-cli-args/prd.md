# FileTransferAgent 支持 mtls/算法 CLI 参数

## 问题

FileTransferAgent（libobk/main.c，dm-ftp 传输代理服务端）的 mTLS 配置只能通过环境变量 `SBT_MTLS_ENABLE` / `SBT_TLS_ALGORITHM` 或 ini `[security]` 设置，缺少 CLI 参数。同仓库 aio-speedd、rdbcommd 均已支持 `--mtls-enable`/`--tls-algorithm` CLI 覆盖（CLI > env > 工具 ini > 全局 ini > 默认），运维无法在单次启动时覆盖配置。

## 现状与参考模式

- `sbt_server_tls_config_init()`（oracleCmdTbl.c:29）内部 sec_resolve_bool/sec_resolve_str 解析 env/ini，签名无 CLI 入口；仅 libobk/main.c 一处调用。
- rdbcommd 模式（rdbcommd-main.c）：getopt 严格校验（mtls 仅接受全串 "0"/"1"；algorithm 白名单两算法）后覆盖 opts 初值；CLI 存在则覆盖 sec_resolve 结果。
- main.c 中 args_process 先于 sbt_server_tls_config_init 执行，顺序已满足。

## 方案

1. **libobk/main.c**：
   - 长选项新增 `{ "mtls-enable", required_argument, NULL, 1004 }`、`{ "tls-algorithm", required_argument, NULL, 1005 }`
   - getopt case：mtls 严格 strtol 校验仅 "0"/"1"（非法报错退出）；algorithm 白名单（SM4_GCM_SM3/AES_256_GCM_SHA384）校验后暂存
   - usage() 增加 TLS/mTLS 配置说明（对齐 aio-speedd 文案风格）
   - init 成功后 InfoLog 输出 TLS 状态（mtls_enabled/algorithm/cert_dir）便于运维确认
2. **oracleCmdTbl.c/h**：`sbt_server_tls_config_init(libobk_tls_config_t *cfg, int cli_mtls, const char *cli_algorithm)`——cli_mtls=-1 表示未指定走 env/config；CLI 显式时覆盖解析值；fail-closed 检查保留。
3. cert_dir 维持 env/ini 层不变（用户需求范围为 mtls/算法参数）。

## 用户故事

1. 作为运维，我希望 FileTransferAgent 像 aio-speedd/rdbcommd 一样通过 `--mtls-enable=1 --tls-algorithm=...` 单次启动即启用指定算法的强制 mTLS。

## Seam 分析

### 声明的测试接缝

- seam: libobk/test/session_test.c -> ../lib/sbt/libobk.c
- seam: test/e2e_tool_scenarios.sh -> FileTransferAgent CLI 行为（新增 FTA 场景）

## 实现决策

- 不改协议帧、不改 sbt_session_server_prepare 及握手逻辑；仅配置入口扩展。
- CLI 非法值行为与 aio-speedd/rdbcommd 对齐：报错退出非零。

## 测试决策

- e2e 新增 FileTransferAgent 场景：--help 含新参数；--mtls-enable=2 与 --tls-algorithm=BOGUS 启动失败非零；--mtls-enable=1 + 有效证书目录启动成功且日志含 mTLS enabled。
- 回归：libobk_session_test 通过（sbt_server_tls_config_init 签名变更的编译验证）。

## 验收标准

- [ ] AC-1: 运行 `FileTransferAgent --help`，usage 含 --mtls-enable 与 --tls-algorithm 说明。
- [ ] AC-2: 运行 `FileTransferAgent --mtls-enable=2` 与 `--tls-algorithm=TLS_BOGUS`，均以非零退出并输出明确错误。
- [ ] AC-3: 运行 `RPC_TLS_CERT_DIR=<有效证书> FileTransferAgent --mtls-enable=1 --tls-algorithm=TLS_SM4_GCM_SM3`，启动成功且日志含 mTLS enabled 与所选算法。
- [ ] AC-4: 不传新参数时行为与现状一致（env/ini 分层生效）；libobk_session_test 回归通过。
- [ ] AC-5: grep 确认 mtls/algorithm 的 CLI 校验为严格白名单（0/1 与两个合法算法名），非法值无法进入配置层。

## 范围外

- cert-dir CLI 参数；协议帧变更；客户端侧（SBT 调用方）参数改造。
