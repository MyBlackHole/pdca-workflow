# Triage Brief — T0167

- **分类**: enhancement / development（PDCA 机制改进，Improvement Task）
- **需求**: 四项 PDCA 工作流 AI 可用性优化（A 确认 CLI / B guidance 字段 / C 证据安全替换 / D PRD 早期校验），全部基于今天实际操作暴露的 AI 不友好实证，先审核对 AI 工作流的提升再实施
- **查重**:
  - T0166（已归档）：时间线一致性校验（门禁 fail-closed + doctor 体检）——本任务的 B/D 是其延伸（错误消息更可执行、校验更早期），A 直接消除时间戳编造根源，无重复
  - T0159（已归档）：flow issue 六层闭环——C 的 superseded 审计模式与其不可变原则一致，无重复
  - 无既有 append-confirmation/replace-evidence/guidance 实现
- **事实核查（已实证）**:
  - A: 今天 T0166 登记 final_confirmation 时 AI（本会话）手写 at=20:25:00，真实 20:21:23，已修正——AI 手写时间戳必然出错
  - B: ACCEPTANCE_CRITERIA_MISSING 消息仅"must contain Markdown checkboxes"，T0165 PRD 修复猜了 2 轮；SCHEMA_INVALID 仅 schema 报错
  - C: 今天 convergence-map 内容错误时 register-evidence 拒绝重复 id，被迫手工删 manifest 行重登，绕过不可变约束
  - D: T0165 PRD 用 `### AC-x` 标题式，do 收尾 validate-convergence 才报 ACCEPTANCE_CRITERIA_MISSING，返工发生在最晚点
  - 无其他机制覆盖上述四点
- **信息缺口（需 Grill）**: 四项范围是否全做、guidance 字段的 schema 变更影响、replace-evidence 的 superseded 保留策略
- **推荐下一步**: 逐项完成 AI 工作流提升论证（现状→痛点→改进→提升度量）后请用户终审
