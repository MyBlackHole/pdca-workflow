# 链接级 mTLS/握手测试模式与测试证书 CN 约束

## 背景
T0352 将三项目握手测试从 fork+execl 工具二进制形式迁移为链接级形式，
并重建了因 CN 含空格而无法通过校验的测试证书体系。

## 约束一：测试证书 CN 必须匹配 ca_cn 白名单
`tls_cert_ca_cn_valid` 仅允许 `[A-Za-z0-9._-]`。CN 用于
`cert_dir/<ca_cn>/host.*` 路径推导，含空格会导致客户端
tls_cert_init_client 必败（服务端 get_ca_cn 提取后下发，客户端校验拒绝）。
生成脚本：openssl genpkey -algorithm ed25519 / ecparam -name SM2；
CN 用 ED25519_Test_CA、SM2_Test_CA 这类下划线风格。

## 约束二：TEST_CERT_DIR 必须编译期注入绝对路径
链接级测试若依赖相对路径 fallback，在 xmake test 运行环境（cwd 非
项目根）必败。统一用 add_defines("TEST_CERT_DIR=\"" .. path.join(
os.projectdir(), "libs", "tests", "certs") .. "\"")。

## 链接级握手测试模式（替代 fork+execl 工具二进制）
- socketpair 直连双方；fork 子进程承载服务端决策树（隔离 g_rpc_config
  等全局状态），父进程跑客户端协商。
- 服务端决策树须忠实复刻产品实现分支（强制/按需 mTLS、ERR_MTLS_REQUIRED/
  ERR_CA_CN、真实 tls_cert_server_handshake 升级），负路径断言错误码。
- main 入口 signal(SIGPIPE, SIG_IGN)：对端早闭后的 SSL 写入不应误杀子进程。
- 业务往返帧（如 GET_TIME→RESP 固定值）验证升级后链路可达，防止"只测协商
  不测通道"。
- 注意协议豁免语义：GET_TIME 在强制 mTLS 下仍放行，验证"拒绝明文业务"须用
  非 time 类型帧。

## 已否决形式
fork+execl 工具二进制 E2E（端口/环境脆弱、无法覆盖内部接缝、存量假失败）
不再新增；既有此类测试按机会成本逐步迁移为链接级。
