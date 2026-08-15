# PRD — 体系自我审查：健康度诊断与问题分级

## 问题陈述

PDCA 体系经 7 轮元审查（T0265-T0271）后，仍存在系统性健康度信号，但无单一聚合视图：

- **doctor 一致性**：doctor 全量 15 个任务中 8 个 inconsistent，SCHEMA_INVALID 30 处为主（另见 STATE_TIME_ORDER、CONFIRMATION_AFTER_PLAN_TO_DO、STATE_TIMESTAMP_MISSING）
- **identity 有效性**：23 组 task_id 撞车（跨 2-3 个任务目录），identity.valid=False
- **seam 契约**：9 个任务的声明的测试接缝与实际测试不一致（测试文件缺失）
- **门禁覆盖率**：T0270 已审计（receipts 81.2%/verdict 79.2%/convergence 95.5%/final_conf 84.4%），T0271 修复后 gate_incomplete=0，但需纳入聚合视图
- T0263 观察窗未触发（无真实新任务），本轮不关联

## 目标

产出一份可复现、可分级、可追溯的体系健康度诊断报告，覆盖四类异常，按三级严重度分级，区分根因（机制前遗留 / 外部项目 / 真缺陷），输出修复候选清单（不执行）。

## 用户故事

- 作为流程负责人，我想一次运行得到体系全部健康度信号的聚合视图，以便判断"体系是否健康、哪些问题需要优先处理"。
- 作为后续任务发起者，我想拿到按严重度和根因分类的问题清单与修复候选建议，以便直接立项。

## 验收标准

- [ ] AC-1: 新增 `scripts/self-audit.py`，全量扫描产出健康度报告（JSON+Markdown 双输出）
- [ ] AC-2: 报告覆盖四类异常：doctor 一致性、identity 撞车、seam 契约、门禁覆盖率，各含数量统计
- [ ] AC-3: 每个异常按三级分级（阻断门禁/数据完整性/仅统计噪音），报告可按严重度过滤
- [ ] AC-4: 报告按根因分类（机制前遗留/外部项目/真缺陷），各类可过滤
- [ ] AC-5: 报告输出修复候选清单（每项含依据与建议任务范围，不执行）
- [ ] AC-6: 诊断脚本可复现：同一输入两次运行结果一致
- [ ] AC-7: 全量测试 4 既有失败保持非回归

## 实现/测试决策

- research 场景：诊断脚本为只读分析，不改变任何任务/记录数据
- 复用既有子模块：audit-gate-compliance.py（门禁/归档/豁免）、pdca-doctor.py（schema 一致性）、seam_contract.py（测试接缝），self-audit.py 聚合其输出
- 严重度映射规则固化于脚本：
  - 阻断门禁：真违规候选（gate_incomplete 非豁免）、identity 撞车（有歧义）
  - 数据完整性：schema 不一致、STATE_TIME_ORDER、seam 契约缺失
  - 仅统计噪音：机制前 legacy 无门禁记录、已豁免任务
- 复现性测试：同一根目录两次运行 JSON 输出 digest 一致

## 测试接缝

### 声明的测试接缝
- seam: tests/test_self_audit.py -> scripts/self-audit.py

## 范围外

- 不修复任何异常（修复另立任务，本任务只出候选清单）
- 不提前触发 T0263 观察窗
- 不改动权威流程文件与既有审计脚本逻辑

## 备注

- 报告存 records/T0272-0815-self-audit/health-audit.md（JSON 输出同目录）
- 复用既有脚本时只做只读调用，不修改其行为
