# Review — design与review回写与生产机制双轴审查

## Standards轴（对照本体契约与编码标准）
- 判定：通过，有Warning1项，无Blocking。`flow-do E/F`的`type/relations`合法，`ontology-validate OK`，`graph islands:0`。
- Warning：`flow-do.md:82-92` E/F只写`design.md/review.md+register-evidence`，无`本体沉淀`字样，与`skill-research.md:73-84`显式沉淀决策不对称，易误读为无回写。依据：`ontology/process/flow-do.md:82-92`对照`ontology/domain/pdca/skill-research.md:73-84`。
- 核验：`python3 scripts/ontology-validate.py --ontology-dir ontology`返回OK；`python3 scripts/ontology_graph.py --root ontology --format summary`返回islands:0。

## Spec轴（对照PRD与用户严格标准）
- PRD AC-1双轴报告：已产本报告，Standards/Spec各有判定（review.md）。
- PRD AC-2回写缺口定位：按用户`Do无即缺口`严格标准，判定为文档缺口非机制断裂。机制上`flow-act.md:34`全任务强制回写，`pdca_core.py:448-451`拒收无`ontology:`的archive，`design`实例`0831-ontology-instance-reference-modeling`已回写`pattern`，故闭环存在；缺的是Do内前向指针。依据：`ontology/process/flow-act.md:34`、`scripts/pdca_core.py:448-451`。
- PRD AC-3证据登记：待登记本报告+convergence-map，`validate-convergence valid:true`后进Check。
- 新增诉求：`research`强制网络查询已补查`lean.org/pdca`与`ResearchGate 349440276`，记本轴发现+改进候选，不直改`skill-research`。依据：`skill-web-research.md:58`现为可选，`flow-act.md`改进须另起任务。

## 分级
- Blocking 0：无安全/数据丢失/规范缺失致闭环断裂
- Warning 1：Do内无沉淀前向指针，建议E/F各加一句指向Act回写
- Info 1：research强制URL门禁待另起改进任务实施
