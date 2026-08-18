# 清理 RPC 遗留辅助函数并移除无效 unused 属性

## 问题陈述

T0315 清理旧协议文件后，`libs/rpc-net.c` 仍有两个未使用的旧原始 fd 收发辅助函数；`libs/tls_keygen.c` 的多个实际调用函数带有误导性的 `unused` 属性。另有一个无活动调用的公共 TLS API，是否删除涉及外部 ABI，不应未经确认处理。

## 目标

删除确定无调用的内部辅助函数，清理实际使用函数上的无效属性，并明确保留公共 API 的 ABI 边界。

## Seam 分析

### 声明的测试接缝

- seam: `libs/rpc-net.c` -> `libs/rpc-handshake.c`
- seam: `libs/tls_keygen.c` -> `tls-keygen` 子命令测试/构建目标
- seam: `rpc/tests/*`, `rdbcomm/tests/tool_integration.c` -> 现行 RPC/rdbcomm I/O

## 验收标准

- [ ] AC-1: 执行调用关系扫描，`libs/rpc-net.c` 中的旧 `rpc_recv/rpc_send` 无定义和引用，且 RPC/fs-backup 中仍被使用的同名公共实现保持存在。
- [ ] AC-2: 执行属性扫描，`libs/tls_keygen.c` 中实际被调用的子命令函数和 usage 函数不再带 `__attribute__((unused))`，功能实现不变。
- [ ] AC-3: 执行 `xmake build` 和 `xmake test`，构建成功且全部测试通过。
- [ ] AC-4: 执行 `git diff --check`，结果通过；`tls_cert_verify_is_local` 公共 API 未被删除，并在结论中记录 ABI 边界。

## 方案与取舍

- 删除 `libs/rpc-net.c` 中的两个静态旧收发函数。
- 仅移除 `libs/tls_keygen.c` 中实际调用函数的无效 `unused` 属性，不删除任何 tls-keygen 子命令。
- 保留 `tls_cert_verify_is_local` 及其头文件声明，外部 ABI 依赖需要单独决策。

## 范围外

- 不删除 `rpc/rpc-io.cpp`、`fs-backup/public/rpc_io.c` 中仍被调用的 `rpc_send/rpc_recv`。
- 不修改协议、TLS 会话 I/O、CLI 参数或第三方代码。
