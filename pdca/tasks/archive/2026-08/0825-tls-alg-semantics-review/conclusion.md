---
schema: pdca.asset/v1
id: T3960-0825-tls-alg-semantics-review
phase: check
source_ids: [review-report]
---

## 上下文

用户提问"服务端设置 tls-algorithm 后是否代表只支持此算法"。四模块协商层+证书层代码审查完成（review-report.md）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| tls-algorithm 构成服务端算法白名单 | 不成立：协商层仅校验客户端算法合法性，配置值不参与 |
| 服务端实际支持集由证书部署决定 | 成立：tls_cert_build_server_profiles 固定双算法 profile |

## 分析

- **AC-1** ✅ 四模块协商层代码位置全部引用（rpc-server.cpp/rpc-protocol.cpp:208、rdbcomm/server.c:497、dmsbtex/network.c:198、oracleCmdTbl.c:92）（review-report）
- **AC-2** ✅ 证书层双 profile 事实（tls_cert.c:361-401 行号）+ 风险提示 + 单算法锁定改进建议齐备（review-report）

Grill：结论是否受配置算法在客户端侧用途影响？——不影响服务端结论；客户端侧配置仍为发起偏好，语义一致。

## 适用边界

结论基于当前代码（T0357/T0358 白名单语义实现后）；若未来实施单算法锁定需重新审查。

## 下一轮建议

- 单算法锁定需求出现时立项：协商层配置过滤 + e2e 错配断言。

verdict: {"outcome": "confirmed", "reason": "审查结论经用户确认：tls-algorithm 为协商偏好非白名单，归档", "verdict_id": "T3960-check-v1", "at": "2026-08-25T15:07:30+08:00"}
