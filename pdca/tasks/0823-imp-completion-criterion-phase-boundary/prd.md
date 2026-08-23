# 改进：completion-criterion 理论合入 writing-great-skills 与 phase-boundary 树入 handoff-work — PRD

## 来源

Improvement Candidate 来自 T0371 评估报告 E-2/E-3（短期层合并立项），improvement_source=T0371。

## 问题陈述

1. writing-great-skills 的"完成标准"节仅两行好/坏例，缺 premature completion 的防御机制理论与 demand 维度——44 个资产的步骤措辞因此缺少可依循的判据写法。
2. handoff-work 只管"怎么写交接"，不管"何时清窗/何时继续"——跨 session 任务（活跃目录 57 个）缺乏阶段边界卫生指引，长任务易在 degraded 推理区工作。

## 方案

documentation 场景，两处增补均避开 flow-do 主文件：

1. writing-great-skills：将"完成标准"节升级为 **completion criterion 杠杆节**——clarity 性质（防过早完成；防御顺序：先锐化边界→不可约模糊且观察到赶工时拆分隐藏后续步骤）+ demand 性质（措辞驱动 legwork；纯参考文档经"every X applied"式措辞携带穷尽性）；失败模式表同步。
2. handoff-work：新增 **阶段边界决策节**——五选项（继续/清窗/交接/子代理/压缩）按序问第一个 yes 获胜；一手源（信息全噪声大）/二手源（有损低噪空间大）交换表；mid-phase 永不做边界决策。PDCA 语境适配：边界指 PDCA 阶段内的会话工作块切换点。
3. pdca/skill-content-baseline.json 同步两文件新 baseline 并记录豁免 reason。

## 验收标准

- [ ] AC-1: writing-great-skills 含 completion criterion 杠杆节，明确 clarity/demand 双性质与两级防御顺序，失败模式表"过早完成"行指向该节
- [ ] AC-2: handoff-work 含五选项决策树节，含固定问序、一手/二手源交换逻辑、mid-phase 禁止决策三条要素
- [ ] AC-3: skill-content-baseline.json 两文件条目已更新且 python3 scripts/audit-skill-content.py 无 budget issue
- [ ] AC-4: 用新杠杆回审 grilling/tdd/register-evidence 三技能各产出 ≥1 条 before/after 措辞对照，登记为 evidence

## 范围外

- 不改 flow-do 主文件（P9 六路径 Done when 化属观察层，待试点证据）
- 不新增门禁脚本

## 备注

内容预算：预计 writing-great-skills +约600B、handoff-work +约900B，豁免 reason 引用本任务与 T0371 报告 E-2/E-3。
