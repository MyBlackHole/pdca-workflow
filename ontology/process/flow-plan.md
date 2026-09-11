---
schema: pdca.asset/v2
id: ontology:process/flow-plan
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.9
summary: Plan：固定当前节点目标与单元测试
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/process
  relates_to:
  - ontology:concept/pdca-gate
  - ontology:concept/pdca-transition
  - ontology:concept/pdca-task
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
  - ontology:process/work-scenarios
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/work-dependency-graph
  - ontology:concept/ontology-reuse
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
---

# Plan：固定当前节点目标与单元测试

## 适用、输入与动作


当前phase=plan，TASK-01真实绑定已建立。读取当前节点/seed、SCENE-01、CONTRACT-01、TEST-01与CONFIRM-01；按CONTEXT-01控制输入。

1. 核对树节点、场景、attempt、已授权图版本与调度就绪。按CAP-01检查派发时控制/等待策略；任何有副作用的Plan探测先经RESOURCE-01授权/准入。建模从当前节点向直接孩子定义seed；实现从孩子已交付产物组合；审查固定被审release。不能把别的目标节点并入本任务。
2. 明确四字段契约、全部必须AC、输入输出/状态/副作用、写域与适用约束；外部事实附claim-review，blocked资料不进入验收基线。
3. 固定suite和CASE-01案例：每约束正例、反例、适用边界、组合/故障与错误实现样本，oracle独立且可运行。补齐环境与清理、run记录方式、回归策略、有限修复预算。
4. 内部动作可分步骤；建模评估拆分时按 [DECOMP 可独立拒收见证](../concept/task-decomposition.md#decomp-rejection-witness)明确产物、oracle和失败边界，记录到既有decomposition。读文件/测试调用不自动成为任务；真实节点仍各有完整PDCA，由SCHED-01调度。
5. 冻结基线、套件和授权范围，提出真实Plan确认；同对象已有答案直接引用，不重复索取。
6. 核对图检查仍匹配、业务资源取得、能力真实可用和当前请求的consumed/confirmed；再按GATE-01/TRANSITION-01进入Do。

输出固定基线、任务套件、真实确认与转换。缺目标/案例/oracle/能力时留Plan并明确问题，不提前改业务实现。示例和模板不得填成已执行。

用户在Plan取消或已授权期限到期按CONTROL-01安全停止，保留Plan为最后phase，不强求虚构后续阶段。

## 建模决策入口

modeling在上述第2步前执行REUSE-01检索/适用比对并写reuse-decision：reuse/local_extension/revise_shared/create四选一，不强制新造本体。其他scene读取已冻结决定与definition_refs，不“顺便升级”。baseline按CONTRACT-01的pdca.baseline/v3.4固定相关输入和adoption检查范围；空检索必须区分确无候选与搜索失败。

## 建模入口的额外交付承诺

按 NODE-01 分开 protocol baseline、subject snapshot 与业务定义；保存原始用户目标，不能用草稿目录描述替代目标。REUSE-01分别决定实例新建和知识复用，固定 knowledge_disposition 及必需发布范围。DECOMP-01 的评估方法/正反例在本次通用建模 suite 中固定；最终 leaf/composite 结论由 Do 生成，不提前强迫孩子叶化。

正式 Plan→Do 只要求当前任务已固定的通用建模验收和真实准入，不要求未来产物已存在；也不允许以 draft、暂无整树冻结或“不需要等待”为由免除真实绑定和 Plan 确认。

## 当前操作索引

采用[通用建模入口](../../tests/modeling-entry/suite.md)的本地绑定，固定原目标/父seed，不以将生成的NODE回写oracle。使用[基线](../../templates/baseline.md)和[gate-check](../../templates/gate-check.md)完成逐项证据核验；派发许可不代替Plan确认，失败保留在当前边界。读写集合、工作累计预算及全必需回归成本在确认对象中明确。
