---
schema: pdca.asset/v1
id: T0315-0818-rpc-net-protocol-cleanup
phase: check
source_ids: [reference-scan, xmake-build, xmake-full, implementation-diff]
---

## 上下文

本任务清理未被当前 RPC/rdbcomm 使用的 `libs/rpc-net-protocol.c/.h` 遗留实现，同时保留现行 RPC 业务协议和握手时间协议。

## 假设与结果

- AC-1：通过。删除后仓库中无 `rpc-net-protocol` 引用；`rpc-protocol` 和 `rpc-handshake` 的现行时间实现仍存在，见 `reference-scan`。
- AC-2：通过。`xmake build` 成功，`rpc-net` 仅编译现行 `rpc-handshake.c`、`common.c` 和 `rpc-net.c`，见 `xmake-build`。
- AC-3：通过。`xmake test -v` 通过 36/36，RPC 时间、rdbcomm 时间和真实工具集成测试均通过，见 `xmake-full`。
- AC-4：通过。`git diff --check` 通过，变更仅删除旧实现、移除无效 include、补齐 `rpc-net.c` 的显式系统头文件和调整构建清单，见 `implementation-diff`。

## 分析

首次编译在删除旧头文件后暴露出 `rpc-net.c` 依赖旧头文件间接提供 socket、IPv4 和字节序声明的问题。已将这些标准系统头文件显式加入 `rpc-net.c`，消除了隐式依赖；没有引入协议或运行时行为变化。

## 适用边界

结论覆盖当前仓库内代码和构建目标，不覆盖仓库外部直接链接旧 `msg_get_time_*` 符号的二进制。现行 C++ RPC 业务协议仍保留同名时间序列化函数，但它不属于已删除的 `libs/rpc-net-protocol` 实现。

## 下一轮建议

继续保持协议实现按模块唯一归属，新增公共协议函数前先执行仓库引用和构建目标扫描，避免再次形成重复序列化实现。

## Verdict

- proposed outcome: confirmed
- reason: 四项验收标准均有证据支持，构建和完整测试通过，且删除过程中发现的隐式头文件依赖已显式修复。
