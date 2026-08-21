## 标准轴

- Blocking: 0。
- 编译使用 `-Wall -Werror` 通过；`git diff --check` 通过。
- 连接状态通过显式 `rpc_hs_session_t *` 传递，没有新增全局 fd 映射或 transport mutex。
- Warning: dmsbtex 与 libobk 各自保留一份 session 协商辅助函数，后续可抽取共享 SBT 适配层，但当前不影响正确性。

## 规范轴

- Blocking: 0。
- dmsbtex/libobk 客户端和服务端均接入 session；业务帧格式保持原有实现。
- `rpc_hs_session_init_plain/init_tls/cleanup` 被复用，mTLS 协商后业务读写统一使用 session 回调。
- 公开 SBT 业务入口未改变；Oracle 内部网络辅助接口改为显式接收 session，避免裸 fd 绕过 TLS。
- 测试接缝已注册到 xmake，新增 plain session 收发测试并复用 RPC handshake 测试。
