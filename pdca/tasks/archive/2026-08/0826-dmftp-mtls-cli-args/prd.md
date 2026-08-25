# dm-ftp(dmsbtex) 支持 mtls/算法 CLI 参数

## 问题

dm-ftp（dmsbtex 部署名，xmake target "dm-ftp"）是 T3963 审查发现的覆盖面遗漏：aio-speedd/rdbcommd/FileTransferAgent 均已支持 `--mtls-enable`/`--tls-algorithm` CLI 参数（T0361/T3959），dm-ftp 仅剩 env(SBT_MTLS_ENABLE/SBT_TLS_ALGORITHM)/ini 入口。T3961 锁定语义已在 dmsbtex 协商层实现（cfg->algorithm != 0 过滤），但缺 CLI 配置入口使锁定能力在 dm-ftp 上不可用。

## 方案

复刻 T3959 FileTransferAgent 模式（两文件同构）：

1. **dmsbtex/main.c**：
   - 长选项 `{ "mtls-enable", required_argument, NULL, 1004 }`、`{ "tls-algorithm", required_argument, NULL, 1005 }`
   - `static int g_cli_mtls = -1; static const char *g_cli_algorithm = NULL;`
   - args_process：mtls 严格 strtol 全串 "0"/"1"；algorithm 白名单校验；非法 return -1
   - **main 检查 args_process 返回值**（当前被忽略且 default 分支 exit(0)——新参数非法值须非零退出）
   - sbt_tls_config_init 调用改 `( &tls_cfg, g_cli_mtls, g_cli_algorithm )`
   - usage 增加 TLS/mTLS 配置说明；启动后 InfoLog 输出 tls config 状态
2. **dmsbtex/network.c**：`sbt_tls_config_init(cfg, cli_mtls, cli_algorithm)`——sec_resolve_str default 已为 NULL（T3961），CLI 显式时覆盖 alg_name 并置 cfg->algorithm/name；cli_mtls>=0 覆盖 mtls_enabled。
3. **dmsbtex/test/session_test.c**：三处 `sbt_tls_config_init(&cfg)` 同步新签名 `(&cfg, -1, NULL)`。

## 用户故事

1. 作为运维，我希望 dm-ftp 与其他服务端一致地用 `--mtls-enable=1 --tls-algorithm=...` 单次启动启用/锁定算法。

## Seam 分析

### 声明的测试接缝

- seam: dmsbtex/test/session_test.c -> ../network.c

## 测试决策

- session_test 签名同步后回归；行为验证复刻 T3959 场景（--help 含新参数、非法值非零退出、CLI 覆盖 env 行为级证明）。

## 验收标准

- [ ] AC-1: 运行 `dm-ftp --help`，usage 含 --mtls-enable/--tls-algorithm 说明。
- [ ] AC-2: 运行 `--mtls-enable=2`、`--mtls-enable=abc`、`--tls-algorithm=TLS_BOGUS`，均非零退出并输出明确错误。
- [ ] AC-3: 行为级验证 CLI 优先级：env SBT_MTLS_ENABLE=0 + CLI --mtls-enable=1 + 无效证书目录 → 启动失败退出（prepare 失败）；无 CLI 对照 → 正常监听。env 非法算法 + CLI 合法 → 正常监听（算法覆盖生效）。
- [ ] AC-4: 不传新参数行为不变；dmsbtex_session_test 回归通过（ALL PASS）。
- [ ] AC-5: grep 确认 dmsbtex 无旧签名调用残留。

## 范围外

- cert-dir CLI；init_sbt_config 文件配置路径改造（SBT 客户端库模式独立）。
