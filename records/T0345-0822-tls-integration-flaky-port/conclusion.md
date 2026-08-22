---
schema: pdca.asset/v1
id: T0345-0822-tls-integration-flaky-port
phase: check
source_ids: [ev-ac1-repro, ev-ac2-truncation, ev-ac3-exclusions, ev-ac4-localization, ev-ac5-followup, ev-ac6-stress]
---

## 上下文

T0345 源自 T0343 遗留观察：tls_integration 在 ctest 中偶发失败一次。原始假设为端口/证书资源竞争。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 端口协作锁/TIME_WAIT 竞争 | **证伪**——plain_exec 同端口机制 15/15 稳定；失败与端口无关 |
| 证书路径冲突 | **证伪**——全部资产位于唯一 mktemp 目录 |
| agent 接收侧丢数据 | **证伪**——DIAG 显示 EOF 到达时队列残留=0，close 无丢弃 |
| **client Reactor 发送侧提前 EOF** | **证实**——DIAGRX client eof sent=61440（应发 32MiB）时 agent received 同步短少 |

## 分析

截断本质：TLS exec 数据面 stdin 流偶发短少 8KB~1.9MB（随机量级）。定位链：复现率约 10-30%（循环 tls_integration）→ plain 对照排除共通层 → 双端计数对照锁定 client Reactor 发送侧 → 疑点集中于 client_exec_reactor.cpp 的 credit 流控状态机（WINDOW_UPDATE 与 stdin 泵唤醒的竞态导致提前进入 EOF 路径）。

**根因修复超出本周期范围**，经用户决策分拆：跟进任务 T0347（parent=T0345）承接修复。本任务产出：
1. 复现脚本 tests/tls_exec_stress.sh（≤5 轮稳定复现，保留现场日志）
2. 完整排除清单与双端计数诊断方法（printf 打点已撤除，可按 T0345 记录快速重加）
3. 定位结论：client Reactor 发送侧 credit 流控竞态

## 失败原因（partial）

产品数据面竞态根因未在本周期内修复——credit 流控状态机的修复需要 per-channel 关联的诊断设施与受控压测台，属独立重构性调试工作。

## 适用边界

- 复现依赖本机 loopback TLS + 32MiB exec 场景；其他流量形态未验证。
- 截断仅偶发（~10-30%），单次通过不能证明修复有效——验收必须以压力循环为准。

## 下一轮建议（T0347 输入）

1. 给 client_exec_reactor 加 channel-id 关联的结构化日志替代 printf。
2. 重点审查 WINDOW_UPDATE 到达时的 stdin 泵唤醒路径与 `stdin_credit` 刷新时序（sent=61440≈初始 credit 量级，疑第二窗口更新丢失后泵误判流终结）。
3. TSan/压测台：以 tls_exec_stress.sh 为基线做受控并发压测。

## verdict

```json
{
  "outcome": "partial",
  "reason": "复现固化+排除清单+发送侧定位三项达成(AC全PASS);根因修复分拆至T0347;结论性质为partial",
  "verdict_id": "T0345-check-v1",
  "at": "2026-08-22T11:00:00+08:00"
}
```
