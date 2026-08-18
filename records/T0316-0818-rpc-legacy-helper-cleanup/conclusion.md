---
schema: pdca.asset/v1
id: T0316-0818-rpc-legacy-helper-cleanup
phase: check
source_ids: [helper-scan, xmake-build, xmake-full, implementation-diff]
---

## 上下文

本任务在 T0315 清理旧协议文件后，继续处理 `libs/rpc-net.c` 中未使用的旧收发辅助函数，以及 `libs/tls_keygen.c` 中实际调用函数上的无效 `unused` 属性。

## 假设与结果

- AC-1：通过。`libs/rpc-net.c` 的本地 `rpc_recv/rpc_send` 已删除；RPC 和 fs-backup 中仍使用的公共实现未改动，见 `helper-scan` 和 `implementation-diff`。
- AC-2：通过。`libs/tls_keygen.c` 中实际调用的 usage 和子命令函数已移除 `unused` 属性，函数逻辑未改变，见 `helper-scan`。
- AC-3：通过。`xmake build` 成功，`xmake test -v` 通过 36/36，见 `xmake-build` 和 `xmake-full`。
- AC-4：通过。`git diff --check` 通过；公共 `tls_cert_verify_is_local` 及其头文件声明保留，见 `helper-scan` 和 `implementation-diff`。

## 分析

删除范围只涉及无调用的内部旧函数和错误标注，不改变现行 TLS session I/O、RPC/rdbcomm 协议、CLI 或公共收发 API。完整真实工具测试验证了 RPC、rdbcomm、时间和 mTLS 路径未回归。

## 适用边界

调用关系结论覆盖当前仓库源码；仓库外部对 `tls_cert_verify_is_local` 的依赖无法由源码证明，因此本任务保留该公共 API，不将“无内部调用”解释为可安全删除。

## 下一轮建议

如需删除 `tls_cert_verify_is_local`，应单独建立 ABI 影响评估任务；后续可将“公共 API 无内部调用”的扫描纳入发布前兼容性检查。

## Verdict

- proposed outcome: confirmed
- reason: 四项验收标准均有证据支持，构建和完整测试通过，公共 ABI 边界已明确保留。
