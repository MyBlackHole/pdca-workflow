---
schema: pdca.asset/v1
id: T0343-0822-align-check-infra-baseline
phase: check
source_ids: [ev-ac1-style, ev-ac2-p1closure, ev-ac3-treemeta, ev-ac4-maketest, ev-ac5-dupctest]
---

## 上下文

T0343 源自 T0341 结论的"下一轮建议"：修复 4 类存量测试失败。Do 阶段逐层暴露后确认为**系统性脱节**（style_check 自 init 起从未完整执行，首条失配规则掩盖全部深层问题），经用户决策扩展范围至全量对齐 + 8 组克隆提取。提交 502ba25（171.1.0 → 171.1.1）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 失配仅 4 类、可快速校正 | 否——实际 22 处文件级 limit + 25 处锚点 + 3 处标记 + 4 处格式断言 + 8 组克隆 |
| 校正 limit 即恢复治理能力 | 成立——全部规则现可执行且有约束力（现实+5% 上取整） |
| 克隆提取可在 bugfix 内完成 | 成立——四类原语提取后 gate 12 行克隆清零 |
| make test / ctest 可达全绿 | 成立——历史首次 exit 0 / 120:120 |

## 分析

**逐条 AC 判定**：AC-1 style_check 全过 — PASS；AC-2 p1_closure — PASS；AC-3 tree_metadata — PASS；AC-4 make test exit 0 — PASS；AC-5 duplicate gate 清零 — PASS。

**关键发现**（方法论沉淀候选）：
1. **顺序短路型检查器的失配是分层的**——修一条才见下一条，预估工作量必须先做"跳过模式全量探测"。
2. **锚点错位三形态**：前向声明 vs 定义（同名同参前缀）、调用点 vs 定义点、相近函数名。自动修复必须强制"顶层定义+同名"双校验。
3. **条件行与消息行 limit 数字漂移**是历史失配的伴生信号（发现 2 例），统一校正时一并归一。
4. T0341 连带缺陷两处：VERSION 增量依赖缺失（82+4 条规则补前置）、observe 版本断言硬编码——跨任务变更的验收盲区在于"检查脚本自身的正确性"不在常规回归内。

## 适用边界

- limit 校正策略承认现状，超大文件分解（B 任务）仍是必要的结构性工作。
- write_fd_all 的 errno 保护对既有调用者是纯增强；新 helper 均为纯转发语义。
- tls_integration 在并行 ctest 下有一次偶发失败（重跑即过），疑资源竞争，非本任务引入但值得后续观察。

## 下一轮建议

1. B 任务（超大文件分解）立项时顺带评估剩余 7 个 8 行信息级克隆是否随拆分自然消解。
2. 观察 tls_integration 并行偶发失败，必要时隔离 TLS 端口/证书资源。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "5 条 AC 全部 PASS 且证据链完整;范围从 4 类演化为系统性对齐+克隆提取均经用户决策确认;make test/ctest/style_check/duplicate gate 四项历史首次或恢复全绿",
  "verdict_id": "T0343-check-v1",
  "at": "2026-08-22T09:20:00+08:00"
}
```
