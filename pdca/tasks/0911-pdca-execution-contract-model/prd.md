# 建模 PDCA 执行契约

## 目标

使本体产出通过统一契约决定执行内容，并冻结后续实现需要消费的字段语义。

## 验收标准

- [ ] AC-1（回链父 AC-4）: 契约机读声明 `work_product`、`required_actions`、`constraints`、`testable_signal`。
- [ ] AC-2（回链父 AC-3）: 契约只关联三个本体职责，不含旧场景控制字段。
- [ ] AC-3（回链父 AC-9）: 明确 skill/tool 为适配器且不得扩大契约范围。

## 关联本体节点

`ontology:concept/pdca-execution-contract`

## 拆分映射

- 执行契约 -> ontology:concept/pdca-execution-contract
