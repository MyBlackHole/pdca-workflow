---
schema: pdca.asset/v1
id: ontology:pattern/link-level-mtls-test-pattern
type: pattern
layer: Knowledge
status: active
summary: 链接级 mTLS/握手测试模式与测试证书 CN 约束
source_task: T0352
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/tls-test-harness]
attributes:
  - name: applicability
    desc: 将握手测试从 fork+execl 工具二进制迁移为链接级形式
    constraint: ""
    testable_signal: socketpair+fork 决策树复刻、SIGPIPE 忽略、CN 白名单 [A-Za-z0-9._-] 校验通过
---

# 链接级 mTLS/握手测试模式与测试证书 CN 约束
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

## 跨项目帧对接的链接级验证要点（T0353 补充）
- 伪服务端回帧必须显式 htonl 转网络序后 memcpy（主机序直拷会导致
  对端 ntohl 校验必败）；>4 字节字段用 htonl 组合实现 htonll。
- rpc 项目 time 豁免语义：MT_GET_TIME(0x111A) 帧不受强制 mTLS 约束，
  验证"拒绝明文业务"须用其他 MT_ 类型帧；GET_TIME_RESP 为
  msg_base_resp + uint64(be64) 共 20 字节，uiResult 服务端未赋值不可强校验。
- 协议枚举弃位保值：移除某个 op/result 时保留原枚举数值空洞，
  避免重排改变线上字节。

## 按需握手决策树（T0354 补充，rpc 对齐版）
服务端在业务循环内处理 HANDSHAKE 帧，行为矩阵：
| server\\client | 明文直连 | 协商(want) |
|---|---|---|
| mtls=0+证书可用 | 明文业务 | OK_MTLS 按需升级 |
| mtls=0+证书不可用 | 明文业务 | ERR_MTLS_UNAVAILABLE 拒绝（不允许降级） |
| mtls=1 | 拒绝明文业务帧 | 强制 OK_MTLS 升级 |
要点：
- 证书 ctx 由 cert_dir 可用性驱动构建（mtls_enabled 仅控制强制语义）；
  非强制下构建失败降级明文服务并告警（F3）。
- 客户端收到任何非 OK_MTLS 一律失败断开（客户端侧同样无降级容忍）。
- 协商载荷用项目自身帧头封装（type/cmd/cmdId 新增 HANDSHAKE 常量），
  不再使用独立裸帧格式；AIOH 裸帧已废弃。
- 线程栈缓冲警惕大常量：TCP_PACKAGE_SIZE(64M) 类尺寸必须堆分配。
