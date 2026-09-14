---
schema: pdca.asset/v2
id: ontology:process/flow-act
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.11
summary: Act：交付、失败返工与知识处置
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-14'
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
  - ontology:concept/ontology-evolution
  - ontology:concept/ontology-adoption
  - ontology:concept/task-decomposition
---

# Act：交付、失败返工与知识处置

## 适用、输入与动作


当前phase=act且Check→Act合法；读取LEARN-01、REWORK-01、SCENE-01与GATE-01。

1. 按 [LEARN 有界经验](../concept/pdca-continuous-improvement.md#learn-bounded-experience)记录知识处置、适用条件与证据；无新增知识可no_new_knowledge，失败反例可形成候选，不为归档强制造本体。
2. 输出当前节点固定交付包、delivery_usable及限制；建模交付子seed，执行交付实际产物，审查交付subject_conformance。错误/partial实现不冒充父可用输入；按VERDICT-01本地验收即可正常归档，不等待祖先回归，相关工作issue仍可开放。
3. 对缺陷记录最小复现、原失败版本、根因/不确定性、影响集合与回归要求；申请同节点相应场景的新attempt、新Agent。旧任务不能代后继执行其Plan。
4. 发布事件交给宿主更新树清单；任务自身不得同时改共享索引或父任务状态。失效传播按REWORK-01，后继未测试前不能宣称修复已完成。
5. 核对请求已处理、未知副作用已解释、产物和证据可恢复；满足GATE-01并确认无抢先停止事件后写第四回执/最终快照，再交回写权和资源；不能先撤掉自身记录权限导致无法落盘。

输出固定交付、知识处置、issue/后继引用与归档回执。候选未发布不等于必须一直阻塞；明确candidate_only即可按规则处理。不得重开归档或抹除失败。

Act期间真实取消仍按CONTROL-01停止而非强行归档；提出后继引用不是批准后继写入。

## 交付与发布不是同一个事件

当前节点交付包含固定definition_refs、有效契约、reuse-decision/adoption行和待发布候选引用；宿主按ADOPT-01登记采用。共享本体发布事件执行EVOLVE-01：候选的独立审查/明确授权/base检查完成才提交，不能因为任务completed就提升head。当前库采用索引未知处写coverage_incomplete，不宣称全库迁移完成。

## 知识去向与局部结束

交付包关联definition_artifact、当前实例、decomposition、suite、REUSE决定与knowledge_obligations。existing_reuse不新造文件；shared_required/deferred指向独立候选和具名接续责任，实际入库引用EVOLVE回执，不移动运行日志。节点本地正常归档可以早于库发布，但工作级知识义务保持未完成。

只有已固定的节点/seed/交付由宿主装配树视图。root Agent不独占全树后续写入，也不批准子阶段。终态回执在固定交付之后，外部索引关联两者，不回填交付文件制造摘要环。

正常第四边与交付完成后，使用独立[archive-receipt](../../templates/archive-receipt.md)记录实际交回/结清；不能把task.md的archive字符串当独立终态。返工issue绑定旧写权结清和新授权，后继产物使用新路径，不覆盖旧版本。
