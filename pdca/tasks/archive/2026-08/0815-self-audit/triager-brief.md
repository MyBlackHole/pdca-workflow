# Triage Brief — 0815-self-audit

- **category**: enhancement
- **scenario_type**: research
- **summary**: 对 PDCA 体系自身做一次健康度自我审查，汇总 doctor/identity/seam/契约类异常并分级，为后续修复任务提供依据。
- **current behavior**: 体系经过 7 轮元审查（T0265-T0271）后，仍有存量健康度信号：doctor 15 个任务中 8 个不一致（SCHEMA_INVALID 30 处等）、identity 23 组 ID 撞车、9 个任务的 seam 声明与实际测试不一致（测试文件缺失）、T0263 观察窗未触发。
- **desired behavior**: 产出可复现的体系健康度诊断报告，按严重度分级（阻断门禁 / 数据完整性 / 仅统计噪音），明确每类问题的根因分类（机制前遗留 / 外部项目 / 真缺陷），并给出修复候选建议。
- **key interfaces**: 任务元数据契约、身份唯一性、测试接缝契约、doctor 自检、审计/修复脚本家族。
- **acceptance criteria**:
  - 运行审计扫描得到体系健康度报告，含异常分类与严重度分级
  - 每个异常分类有数量统计与代表性样本
  - 报告区分"机制前遗留 / 外部项目 / 真缺陷"根因
  - 输出修复候选清单（可另立任务执行）
  - 全量测试保持 4 既有失败非回归
- **out of scope**: 直接修复任何异常（只诊断不修复，修复另立任务）；T0263 观察窗不因此任务提前触发。
- **information gaps**: 用户对"自我审查"的具体范围与深度期望；是否沿用既有审计脚本或需新诊断脚本。
- **dedup results**: 与 T0265-T0271 元审查系列无重复——本轮为全体系健康度聚合诊断，而非单一机制审计。
- **recommended next steps**: 确认范围后进入 Grill 澄清边界，然后写 PRD、Do 阶段实现诊断脚本并产出报告。
