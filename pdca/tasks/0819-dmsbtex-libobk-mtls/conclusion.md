# T0328 Check 结论

## 检查范围

基于提交 `2b5341ef`、Do 阶段 evidence、构建输出、`sbt_transport_test` 和真实 dm-ftp/FileTransferAgent 进程探测结果复核 dmsbtex、libobk 的 mTLS transport 接入。

## 双轴审查

### 标准轴

- Blocking：0。代码已集中封装 SSL 读写和连接清理；dmsbtex 网络层及 libobk Oracle 协议层未保留独立裸 `send/recv` 调用。
- Warning：`sbt_transport` 使用全局 fd→SSL 表，适配旧 fd ABI，但连接数量和并发生命周期仍需要真实服务进程回归观察。
- Info：当前 mTLS 是连接建立即 TLS 握手，尚未实现旧 PRD 中额外的明文能力协商头。

### 规范轴

- 已满足：复用现有 `tls_cert`；开启后握手失败不回退明文；mTLS 后协议 I/O 走 transport；dmsbtex、libobk 及服务端目标可构建。
- 已满足：独立 transport 测试、两组真实服务端握手和 dmsbtex/libobk 外部 ABI 测试均已通过。
- 已满足：缺少客户端证书收到 `certificate required`；SM2/classic CA 不匹配导致 dmsbtex 客户端非零失败；两组 mTLS 关闭业务回归均通过。

## 验收标准判定

| AC | 判定 | 证据/限制 |
|---|---|---|
| AC-1 | 通过 | dmsbtex 外部 ABI 测试通过，真实备份业务帧成功 |
| AC-2 | 通过 | libobk 外部 ABI 测试通过，真实备份业务帧成功 |
| AC-3 | 通过 | transport fork 测试通过，静态检查显示协议层调用 transport wrapper |
| AC-4 | 通过 | 缺客户端证书、证书不匹配均非零失败且无业务成功 |
| AC-5 | 通过 | dmsbtex、libobk 两条 mTLS 关闭业务 ABI 回归均退出 0 |
| AC-6 | 通过 | 四个目标及测试目标构建通过，`git diff --check` 通过 |

## 结论

结论为 **成立（confirmed）**。两条 SBT 链路的真实外部 ABI、双向 mTLS 握手、业务帧收发、证书缺失/不匹配失败和 mTLS 关闭明文回归均已验证通过。

## 风险与后续

1. 使用全局 fd→SSL 映射保持旧 ABI，必须通过并发连接和异常退出测试确认没有悬挂条目或 fd 复用误绑定。
2. 当前未实现额外明文协商头；若要求同端口在单连接内动态决定模式，需要另立协议兼容设计和测试。
3. 后续应补充缺 CA、缺客户端证书、证书不匹配、mTLS 关闭和真实业务帧的自动化脚本。
