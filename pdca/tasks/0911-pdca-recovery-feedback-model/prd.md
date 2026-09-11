# 建模 PDCA 恢复与反馈

## 目标

闭合判定之后的失败恢复、效果反馈和下一轮 Plan 回流关系。

## 验收标准

- [ ] AC-1（回链父 AC-6）: rejected/partial 明确关联恢复动作、人工升级或后续任务。
- [ ] AC-2（回链父 AC-6）: confirmed 明确关联效果反馈，缺少遥测时必须为 `unknown`。
- [ ] AC-3（回链父 AC-2）: 恢复和反馈回流下一轮 Plan，但不形成单任务转换环。

## 关联本体节点

`ontology:concept/pdca-recovery`
`ontology:concept/pdca-feedback`

## 拆分映射

- 恢复与反馈 -> ontology:concept/pdca-recovery
