# T0457 报告：扩展 ontology_fragment 强制范围

## 变更
- `scripts/ontology_gate.py:23-35` 在 `ONTOLOGY_FRAGMENT_MISSING` 中加入 `scenario_type` 与 `ontology_exempt` 指引，`guidance` 明确可执行修复
- `ontology/concept/pdca-gate-do.md` 将适用范围从 development/bugfix 扩展为全部 scenario_type，明确豁免需显式声明
- 行为未变（原已对全部 scenario 阻塞），本次使文档、提示、测试与行为一致，完成“默认启用”闭环

## 验证
- research/design/review/documentation 在 do 缺 fragment 时均阻塞，exempt 时放行
- 非 do 阶段不阻塞
- ontology-validate OK, islands 0
- 新增 6 用例全部通过
