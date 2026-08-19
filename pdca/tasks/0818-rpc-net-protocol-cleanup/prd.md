# 清理 rpc-net-protocol 遗留代码

## 问题陈述

`libs/rpc-net-protocol.c/.h` 保留了一套旧的时间消息序列化实现。当前仓库的 RPC 使用 `rpc/rpc-protocol.cpp/.h`，rdbcomm/RPC 首阶段时间操作使用 `libs/rpc-handshake.c/.h`，旧文件没有内部调用者却仍被构建和导出，造成重复协议定义与维护风险。

## 目标

删除旧的 `rpc-net-protocol` 文件及其构建入口和无效 include，确保现行 RPC/rdbcomm 时间能力、握手协议和所有测试不受影响。

## Seam 分析

### 声明的测试接缝

- seam: `libs/xmake.lua` -> `libs/rpc-net` 构建目标
- seam: `rpc/tests/*` -> `rpc/rpc-protocol.cpp`, `rpc/rpc-io.cpp`
- seam: `rdbcomm/tests/tool_integration.c` -> `rdbcomm/rdbcommd`, `libs/rpc-handshake.c`

## 验收标准

- [ ] AC-1: 删除后在仓库源码和构建配置范围执行 `rg 'rpc-net-protocol'` 得到 0 个旧文件引用，并确认 `rpc/rpc-protocol.cpp` 与 `libs/rpc-handshake.c` 的现行时间实现引用仍存在。
- [ ] AC-2: 执行 `xmake build`，结果为构建成功，`rpc-net` 目标不再编译旧源文件。
- [ ] AC-3: 执行 `xmake test`，所有测试通过，包含 RPC 时间、rdbcomm 时间和真实工具集成测试。
- [ ] AC-4: 执行 `git diff --check` 并检查变更，结果无空白错误、无协议文件误删，且旧文件已从版本库移除。

## 方案与取舍

- 删除 `libs/rpc-net-protocol.c/.h`，从 `libs/xmake.lua` 移除源文件，并删除 `libs/rpc-net.c` 中不再需要的 include。
- 保留 `rpc/rpc-protocol.cpp/.h`，因为 RPC 业务帧仍使用它；保留 `libs/rpc-handshake.c/.h`，因为 rdbcomm 与 RPC 的新时间/协商协议使用它。
- 不新增兼容转发层；旧符号无仓库内调用，保留它们会继续扩大重复协议面。

## 范围外

- 不修改 RPC/rdbcomm 协议字段、握手状态机或时间 API。
- 不修改第三方源码，不处理仓库外部二进制的历史 ABI 依赖。
