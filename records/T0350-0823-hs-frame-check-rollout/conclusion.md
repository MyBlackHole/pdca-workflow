---
schema: pdca.asset/v1
id: T0350-0823-hs-frame-check-rollout
phase: check
source_ids: ["frame-check", "regression"]
---

## 上下文

T0349 遗留建议：帧校验从 execute_shell_script 推广至剩余 recv 点（rpc-client.cpp:2760 nc 变体）。

## 假设与结果

- **AC-1** 全部 recv 点覆盖：`PASS` — frame-check 证据显示 :968 与 :2767 两处均有 MT_HANDSHAKE_RESP 校验，与 rpc_recv_io 调用点数一致。
- **AC-2** 无回归：`PASS` — mixed_mtls_integration 全用例 PASS。

## 分析

校验模式统一：recv 后解析前拦截握手错误帧，ErrorLog "server rejected" + error_no=-(result) + 断开。client 全部响应路径现已防御性覆盖。

## 适用边界

仅 client 消费侧；server 端防护由 handshake_done 分支承担。

## 下一轮建议

无遗留；后续新业务函数应沿用此校验模式。
