---
schema: pdca.asset/v1
id: T0346-0822-rpc-hs-err-exit-code
phase: check
source_ids: ["unit-quad", "tool-integration", "static-scan"]
---

## 上下文

T0344 交付后遗留：client 收 `HS_ERR_MTLS_REQUIRED` 帧误按业务响应解析致 exit 0，掩盖 server 拒绝；且证书异常可观察性不足、测试曾用 /tmp 自建证书违反项目资产约束。

## 假设与结果

- **AC-1** client 语义化失败：`PASS` — tool-integration 实测 server1+client0+`-c true` exit 252（非0）
- **AC-2** 错误信息可见：`PASS` — client 日志输出 `server rejected: handshake error result=0x8004`
- **AC-3** 无回归：`PASS` — plain/mixed/forced 三象限 + tls_cert_test 8 用例全绿
- **AC-4** 项目内证书：`PASS` — static-scan grep keygen/--out = 0，client 前缀残留 = 0（sm2_client.* 与 client-001/002 已删）

## 分析

- 帧校验位于 execute_shell_script recv 后、解析前，错误码透传 -(hs.result) 经 shell 低8位呈现为 252
- 可观察性双层补齐：client 调用点输出 cert_dir/algorithm/ca_cn 实际值；tls_cert.c 握手失败输出 verify_result 错误串与对端 subject/issuer（仅诊断分支，行为零变化）

## 适用边界

- 校验覆盖 execute_shell_script；其余业务函数（download/upload 等）recv 点可按同模式后续推广

## 下一轮建议

- 其余业务函数 recv 点的帧类型校验推广可另起小任务批量处理
