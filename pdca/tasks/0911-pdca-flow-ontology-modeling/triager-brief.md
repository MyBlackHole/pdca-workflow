# T2170 分诊摘要

- **category**: PDCA 流程本体建模
- **ontology_role**: `ontology_modeling`
- **summary**: 完成可独立驱动后续实现的 PDCA 流程本体，不在本任务重构 Python runtime。
- **current behavior**: 阶段、转换、门禁、证据和判定已有节点；执行契约、恢复、反馈已有初始节点，但完整性边界、机读规格和职责约束尚未闭合。
- **desired behavior**: 单一流程本体可完整回答任务如何创建、推进、准入、执行、取证、判定、处置、恢复和反馈，并能派生实现合约。
- **execution_contract**:
  - `work_product`: 完整 PDCA 流程本体及其机读完整性规范
  - `required_actions`: 盘点节点与关系；补齐缺失概念；定义不变量；定义完整性问题集；验证无悬空、无环、可测试
  - `constraints`: 只保留三种本体职责；不使用六场景分类；不构建新 Python runtime；不修改不可变记录
  - `testable_signal`: `ontology-validate` 通过，且完整性规范覆盖所有必需构件和关系
- **priority**: P0
- **risk**: 若只补文档而不形成机读规格，后续实现仍会重新硬编码流程语义。
- **recommended direction**: 以 `ontology:process/pdca-flow-model` 为聚合根，补齐组成节点、关系约束、执行契约和完整性问题集，再冻结实现输入边界。
