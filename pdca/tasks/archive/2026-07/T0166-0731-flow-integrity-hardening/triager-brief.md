# Triage Brief — T0166

- **分类**: enhancement / development（PDCA 机制改进，Improvement Task）
- **需求**: 修复今天审查发现的 T0164 流程违规（plan→do 早于 final_confirmation、task.json 时间戳事后回填），并加固流程文件的时间线一致性校验，防止同类问题复发。**用户前提：所有修复必须先审核对 AI 是否真的有用、对 AI 是否友好，形式主义修复不做。**
- **查重**:
  - T0159（0801-pdca-self-optimization-loop，已归档）：已建立 Flow Issue Occurrence/Decision/Candidate/Effectiveness 六层闭环与 CLI（report-flow-issue.py 等），**但未覆盖**"流程文件被事后回填/时间线自相矛盾"的检测——本任务补齐该缺口，复用 T0159 的 occurrence 登记机制处置 T0164 违规
  - 无其他任务覆盖 transition 时间戳校验
- **事实核查（已实证，非询问）**:
  - T0164 `transition-receipts/plan-to-do.json` at=`16:47:04` < final_confirmation at=`17:15:00`（门禁违规 28 分钟）
  - T0164 `states.do`=16:47:04 > `states.plan`=17:15:00、`created`=17:00:00（时间线自相矛盾）
  - T0164 `task.json.bak`（转换快照）内含未来时间 17:15:00（回填痕迹）
  - T0164 `implement.jsonl` do 执行（17:10 读文件）早于确认 17:15
  - T0164 `meta.convergence` 为 record ID 占位符而非收敛条件
  - T0165 证据未登记（records/T0165-* 不存在）——属 T0165 自身 do 收尾，不在本任务范围，仅登记提示
  - `transition-phase.py` 当前仅校验"确认存在"，不校验"确认时间 ≤ 转换时间"；`pdca-doctor.py` 不检测时间线一致性
- **信息缺口（需 Grill）**: 校验强度（fail-closed 阻断转换 vs doctor 警告）、是否同时收紧 schema（convergence 占位符）、T0164 处置方式（登记 occurrence 即止 vs 要求 check 阶段向用户说明）
- **推荐下一步**: Plan 阶段逐项做"AI 价值 × AI 友好性"审核后请用户终审
