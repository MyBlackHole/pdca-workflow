---
schema: pdca.asset/v1
id: T3958-0825-rpc-net-time-test-fix
phase: check
source_ids: [ac1-test-pass, ac1-test-log, ac2-frame-protocol, ac3-e2e-matrix]
---

## 上下文

用户恢复 libs/rpc-net.c 为原实现（4B htonl 长度前缀 + body 分帧，与 rpc 模块 rpc_send_io/rpc_recv_io 及真实服务端一致）后，rpc_net_time_test 失败（伪服务端按旧无前缀协议编写）。修复仅动测试侧，实现零改动（commit 0035b492）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 测试按 4B 前缀协议收发即可匹配恢复后的实现 | 成立：PASS exit=0 |
| 响应体必须按结构体真实布局（含对齐 padding，sizeof=24）构造 | 成立：硬编码 20B 时 timestamp 错位断言失败，改用 sizeof+offsetof 后通过 |
| 恢复实现与真实服务端兼容（timed_net_key 链路） | 成立：e2e 场景矩阵 17/17 |

## 分析

- **AC-1** ✅ xmake run -D rpc_net_time_test 输出 PASS、exit=0；正路径×2（含大时间戳字节序往返）+ 负路径×1 全过（ac1-test-log）
- **AC-2** ✅ 伪服务端 MSG_WAITALL 全量收 4B 前缀（校验==8）+ body 校验 uiMT/uiLEN；响应 htonl(sizeof(resp)) 前缀 + offsetof 布局填充；无直读直写残留（ac2-frame-protocol）
- **AC-3** ✅ e2e 场景矩阵 17/17 通过，含 keygen/timed-key 链路场景，证明恢复实现与 aio-speedd 真实交互正常（ac3-e2e-matrix）

Grill 追问：
1. 为何不保留"错误 mt 必拒"用例？→ 恢复后的 rpc_get_time 仅校验 uiResult 不校验响应 uiMT，该语义在实现中不存在；测试必须反映真实行为契约。如需强化应另立实现任务。
2. 对齐问题是否影响线上？→ 服务端与客户端均以 sizeof(msg_get_time_resp_t)=24 收发同构字节流，padding 一致无歧义；测试此前硬编码 20B 才是偏差。

## 适用边界

适用于 libs/rpc-net.c 当前分帧协议；若未来引入响应 uiMT 白名单校验，负路径需同步补"错误 mt 类型"场景。结构体布局变更（加字段/pack）时本测试会因长度校验失败而红——这是期望的保护行为。

## 下一轮建议

- 可选强化任务：rpc_get_time 增加 uiMT==MT_GET_TIME_RESP 校验（拒绝非预期响应类型），届时同步扩展测试。

verdict: {"outcome": "confirmed", "reason": "三项 AC 全过：测试 PASS、协议收发合规、e2e 兼容性证明成立", "verdict_id": "T3958-check-v1", "at": "2026-08-25T14:29:00+08:00"}
