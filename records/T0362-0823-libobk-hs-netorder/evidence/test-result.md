# 测试结果证据（T0362 / M5）

- 模块级：libobk_session_test —— PASS（覆盖 mTLS 真实往返 + 畸形/未知算法 fail-closed 拒绝路径；同架构 htons/ntohs 对称自洽）
- 全量回归：xmake test —— 100% tests passed, 0 failed out of 40（含 libobk_session_test、rdbcomm_handshake_session_test、tls_cert_test 等，无回归）

验收映射：AC-2（libobk_session_test 全用例 PASS）。
