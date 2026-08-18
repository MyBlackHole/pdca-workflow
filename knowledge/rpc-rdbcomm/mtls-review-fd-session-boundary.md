# RPC/rdbcomm mTLS 审查：连接对象必须携带传输状态

## 可复用结论

首阶段明文协商成功后，mTLS 的 `SSL*` 和读写函数必须与连接生命周期绑定。只返回裸 fd 的连接 API 无法表达 SSL 所有权，也无法保证后续应用帧继续走 `SSL_read/SSL_write`；如果保留这类 API，必须在 mTLS 协商结果下明确失败，不能让调用方误以为 fd 仍可直接收发。

RPC/rdbcomm 的审查应分别检查：

1. 首阶段三场景是否一致：时间响应后关闭、协商后升级并进入应用帧、未知帧返回明确错误。
2. 每个业务入口是否从连接对象取得 transport I/O，而不是重新按 fd 创建 plain I/O。
3. SSL cleanup 是否覆盖握手失败、业务初始化失败、正常关闭和服务端线程退出。
4. 单测通过不等于真实业务链路通过；至少需要真实进程的明文、mTLS、算法不匹配、证书缺失和失败不降级矩阵。

## 适用边界

本知识仅适用于首阶段协商后升级 TLS 的流式 TCP 协议；不替代具体证书、算法和上层配置文档。

## 来源

- `records/T0309-0818-mtls-implementation-review/conclusion.md`
- `records/T0309-0818-mtls-implementation-review/evidence/review-report.md`
