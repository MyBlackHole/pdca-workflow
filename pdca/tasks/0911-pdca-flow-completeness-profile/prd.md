# 建模 PDCA 流程完整性规范

## 目标

建立可机器判定的完整性问题集，并冻结新 Python 实现的本体输入边界。

## 验收标准

- [ ] AC-1（回链父 AC-7）: 问题集覆盖构件、关系、职责、契约、闭环五类完整性。
- [ ] AC-2（回链父 AC-8）: 每个完整性问题都有确定性 `testable_signal`。
- [ ] AC-3（回链父 AC-9）: 输出实现必须消费的节点、字段、关系和失败语义清单。
- [ ] AC-4（回链父 AC-8）: `ontology-validate` 通过且无新增孤岛。

## 依赖

依赖 T2171、T2172、T2173 完成后聚合。

## 关联本体节点

`ontology:process/pdca-flow-model`

## 拆分映射

- 完整性规范 -> ontology:concept/pdca-task
