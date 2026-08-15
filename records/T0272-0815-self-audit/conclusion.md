# T0272 体系自我审查 — 结论

- 任务：T0272-0815-self-audit
- 日期：2026-08-15
- 阶段：check（产出本结论）

## 验收对照

| AC | 标准 | 结果 | 证据 |
|----|------|------|------|
| AC-1 | 新增 scripts/self-audit.py，JSON+Markdown 双输出 | Passed | ac1 |
| AC-2 | 报告覆盖四类异常（doctor/identity/seam/门禁）各含统计 | Passed | ac2 |
| AC-3 | 三级分级（阻断/数据完整性/噪音），可按严重度过滤 | Passed | ac3 |
| AC-4 | 根因分类（机制前遗留/外部项目/真缺陷），可过滤 | Passed | ac4 |
| AC-5 | 修复候选清单（依据+建议范围，不执行） | Passed | ac5 |
| AC-6 | 诊断可复现（两次运行 JSON 一致） | Passed | ac6 |
| AC-7 | 全量 4 既有失败保持非回归 | Passed | ac7 |

## 关键结果

### 健康度总览（78 项异常）

| 维度 | 计数 | 严重度 | 根因 |
|------|------|--------|------|
| id_collision | 23 | 阻断 | 主要 legacy（T01xx/T02xx 编号滥用） |
| record_mismatch | 20 | 数据完整性 | legacy（record 派生规则前任务） |
| seam | 10 | 数据完整性 | external-project 9 + real-defect 1 |
| schema | 8 | 数据完整性 | 混合（5 外部 + 3 legacy） |
| event_mismatch | 5 | 数据完整性 | legacy（flow-event 记录派生） |
| legacy_no_gate | 7 | 噪音 | 机制前任务 |
| exemption | 5 | 噪音 | 已豁免（T0271 修复） |

### 门禁覆盖率

- receipts 82.2%（125/152），verdict 80.9%，rejected receipts 10 条（拒收留痕机制持续计数）。

### 根因分布

- legacy 63（81%）：严格 schema/identity 机制上线前的存量任务
- external-project 9：round 系列外部项目 seam 契约缺失（测试在外部仓库）
- real-defect 6：5 个 0805/0806 外部项目 schema 违规 + 本任务 seam（自身未闭环时）

### 修复候选清单（不执行）

1. **[high] ID 撞车清理**：23 组 task_id 重复，identity 歧义影响可追溯性
2. **[medium] schema 一致性修复**：8 项 schema/时序不一致
3. **[medium] record 派生一致性修复**：20 项 meta.record 与派生规则不符
4. **[medium] seam 契约补齐**：10 项 seam 声明与实际测试不一致（外部项目需确认测试位置）

## 测试

- 全量：**265 passed / 4 failed**（4 失败为既有：2 harness + 2 doctor seam，非本次引入）
- 新增：test_self_audit.py 9 项全绿（结构/四类覆盖/分级/根因/门禁/候选/复现/报告渲染/task_id 解析）
- test_triage_brief 基线随新 brief 更新（93 个 brief / 57.0%）

## 遗留

- 修复候选清单待后续独立任务执行（ID 撞车清理优先级最高）
- T0263 观察窗未触发，保持独立
