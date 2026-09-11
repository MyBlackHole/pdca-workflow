# 可复用业务审查测试契约

这五份套件对应ontology中的四个工作实体与一个组成模式，每套15个固定结构样本，覆盖建模/执行/独立审查三个scene。它们提供输入、期望、判定依据与失败处置；不是已经运行的生产报告，actual均为空。组成模式有独立CP套件，并联合K系列控制；不能因为引用根suite就假称覆盖CP约束。

| 业务定义 | suite |
|---|---|
| 本体项目审查 | [project-review](project-review/suite.md) |
| 规则一致性审查 | [rule-consistency-review](rule-consistency-review/suite.md) |
| 资料主张核验 | [source-claim-review](source-claim-review/suite.md) |
| 单元测试资料审查 | [test-contract-review](test-contract-review/suite.md) |
| 角色组成模式 | [project-review-composition](project-review-composition/suite.md) |

执行器不能用facts字段自证实际资料正确；结构化参考模型只验证已声明谓词和已知负控制。实际审查必须对固定原文、版本、来源/观测逐项取证，并保存自己任务的actual。允许人工/AI语义步骤，但不允许只有“看起来专业”的oracle。

对应递归/入库案例见[modeling-regression](../modeling-regression/README.md)。保留通用PDCA控制、既有复用与测试规则，不新增自动运行框架。

3.4.1保留本目录旧结构样本原字节，避免把历史fixture改成新测试声称。真实原材料识别补在[records-regression](../records-regression/README.md)，采用时按CASE-01固定本地case绑定；没有绑定不得以“同来源语义”代替场景设计。
