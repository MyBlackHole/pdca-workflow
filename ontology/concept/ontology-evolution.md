---
schema: pdca.asset/v2
id: ontology:concept/ontology-evolution
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: EVOLVE-01：修订候选不覆盖已批准源
---

# EVOLVE-01：修订候选不覆盖已批准源

## 内部细化与职责变更

以本任务已批准的目标、非目标、对外 I/O、共享不变量、AC/oracle、资源与读写域为边界，
不是以“是否出现新实体”判断越界。候选变化先记录原版本、对象/约束、动机、影响、兼容性和未知；
无法确认仍在原边界内时保留 unknown，停止受影响的变更并询问，不自行认定为内部细化。

| 变化 | 当前允许的处理 |
|---|---|
| 已授权职责内补充内部实体、属性、关系或约束，不改变上述边界 | 在已批准的 modeling Do 和模型草稿写域内继续细化；不为每个新实体另开建模任务或重复审批 |
| 建模中发现原职责内可独立交付、拒收的组成部分 | 按 [DECOMP-01](task-decomposition.md) 形成模型/child seed 候选；不转移既有责任、不修改已冻结工作树，也不自动创建子任务 |
| 改变目标、外部接口、共享不变量、AC/oracle、既有责任分配，或需要扩大资源/读写域 | 停止受影响动作，报告差量和影响后等待用户决定；目标/oracle 改变仍按新 attempt 处理，旧确认不适用 |

modeling 的范围内细化是原任务的产出，不是修改其固定输入。首次根建模仍受 TASK-01 的 bootstrap 边界约束。
这不授权在 Plan/Check/Act 中实施 modeling Do，也不授权发布、切换场景或继续下一阶段。
例如 Storage 在原持久化承诺内增加 PrivateIndex 是候选内部细化；把“成功即持久化”改成
“成功仅进入内存队列”改变了对外承诺，不能以实现细节为名继续。

## 实现、验证中发现遗漏

Implement/Verify 可以按 [CONTEXT-01](../process/select-task-subgraph.md) 在获准读域核实事实，
并在获准记录写域报告遗漏、反证与修订建议；不得借核验顺便编写/采用新模型、修补被审对象或放宽 oracle。
需要改变模型或授权边界的实施动作停止，安全且已获准的只读核验可继续；确证违例为 fail，
证据不足为 unknown/not_run，不能因为“模型没写”就把原始需求的遗漏判为通过。
修订建议只是当前报告，不自动启动新的 modeling、子任务或场景。

## 输入、候选输出与采用

沿用 [ontology-revision](../contracts/record-shapes/ontology-revision.md) 的
`base_revision`、`proposed_revision`、`change_set`、`payload_ref`、`payload_digest` 和 `adoption_ref`，不新增 schema。
Model 消费固定 M1，modeling Do 在获准草稿位置产出候选 M2；首次根建模没有 M1 时如实保持空，
不虚构基线。不覆盖 M1、原 baseline/assignment 或旧证据；M2 作为本次产出交给后续 Check，
并由用户批准相应 Act 固定交付，而不是反过来充当本次执行的原始授权依据。

M2 出现不自动改变任何活动任务的采用版本。后续 Implement/Verify 按
[ADOPT-01](ontology-adoption.md) 的明确授权采用固定版本；同一 node 的身份不表示不同 revision 可互换。
旧 PASS 不自动成为 M2 的 PASS。仍采用 M1 的任务是否能继续，取决于 M1 在其范围内是否仍然适用，
不是取决于是否出现新版本；发现影响正确性的错误时记录影响并停止受影响动作，按 DEPENDENCY-01
处理相关映射和证据的失效。与该变化无关且依据仍有效的任务不因候选产生而被全局阻断。

共享库发布仅在明确获准写域与处置中进行，保留原版本、冲突依据、最终审查及真实发布结果。
发布失败不改历史为成功。候选、项目采用与全局发布是三个动作，不自动链式执行。
