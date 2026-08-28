# Triage Brief — 0828-libobk-so-mtls-test

- **category**: enhancement
- **scenario_type**: development
- **summary**: 开发一个独立程序，验证 libobk 共享库（.so）的 mTLS 功能是否正常工作
- **current behavior**: 现有 `libobk/test/session_test.c` 已通过 xmake `libobk_session_test` 目标以链接级方式覆盖 mTLS 握手（真实往返、fail-closed、算法锁定、证书错配等）；知识库 `link-level-mtls-test-pattern.md` 已明确否决 fork+execl 工具二进制 E2E 形式，并规定链接级 socketpair 为首选测试模式。
- **desired behavior**: 用户希望有一个"程序"专门验证 libobk .so 的 mTLS 是否正常；具体形态（独立二进制 / dlopen 加载 .so / 扩展现有测试）、范围与证书来源待澄清。
- **key interfaces**: libobk 公开 mTLS 会话 API（client/server 握手准备、握手执行、会话读写）；共享库导出符号；TLS 证书上下文初始化接口。
- **acceptance criteria**: 运行验证程序针对 libobk .so，得到明确可 grep 的 pass/fail 信号（mTLS 握手成功且双向收发 OK / 失败路径被正确拒绝）。
- **out of scope**: 不修改 libobk 生产代码 mTLS 实现（纯测试产物）；不改动证书加载/握手协议/算法 profile 模型。
- **information gaps**: 程序具体形态、验证范围（smoke / 完整矩阵）、证书来源、主要使用场景（随手工具 / CI 回归）。
- **dedup results**: 与 `0820-tls-session-integration-test`（AC-2 已含 libobk 会话 mTLS 测试）、知识库 `link-level-mtls-test-pattern.md` 概念相关；非重复任务，但覆盖面与现有 session_test 重叠，需明确本任务的增量价值（独立程序 / 验证 .so 产物被外部加载）。
- **recommended next steps**: Grill 用户确定程序形态、验证范围与证书来源后，合成完整 PRD 与声明测试接缝，走 P6 终审。
