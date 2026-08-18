# 设计：清理 RPC 遗留辅助函数

## 分类

1. `libs/rpc-net.c::rpc_recv/rpc_send`：静态、无调用、旧原始 fd 长度帧实现，直接删除。
2. `libs/tls_keygen.c`：函数均有活动调用，仅移除误导性的 `__attribute__((unused))`，不改变函数逻辑。
3. `libs/tls_cert.c::tls_cert_verify_is_local`：公共头文件声明、无活动内部调用，暂不删除，避免未经确认破坏外部 ABI。

## 验证

使用 `rg` 检查调用关系和属性残留；运行 `xmake build`、`xmake test` 和 `git diff --check`。现行 session I/O、RPC/fs-backup 的非静态 `rpc_send/rpc_recv` 不在删除范围。
