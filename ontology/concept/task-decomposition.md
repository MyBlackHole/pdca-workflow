---
schema: pdca.asset/v2
id: ontology:concept/task-decomposition
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.4
dcterms_modified: '2026-09-27'
summary: DECOMP-01：从合格固定 work node 产生正式 task seed
---

# DECOMP-01：Node → Task seed

DECOMP-01 只回答：**哪些已经固定且满足 NODE-01 的 work node，可以形成供用户选择的正式 task seed。**
它不创造 ontology/node、不选择完整 context、不创建 Agent，也不执行 task。

## Preconditions

普通 task seed 必须回指：

- fixed ontology revision；
- fixed tree revision / node_id；
- NODE-01 已满足的 node contract；
- parent composition ref；
- 必要 dependency refs；
- 当前 scene 与 scene-specific AC/input 要求。

尚未固定的 M2 candidate、未冻结 tree、只有 relation 但不满足 NODE qualification 的对象，都不能被 DECOMP 预先包装成正式 task。

## Seed output

DECOMP 只产生：

- node/work/scene identity；
- responsibility；
- fixed I/O 与 AC/oracle refs；
- parent/composition refs；
- dependency refs；
- initial scope/context selection 的输入锚点；
- 为什么它是独立 task 的 qualification evidence。

CONTEXT-01 随后根据这些锚点选择 minimum sufficient assignment refs；
TASK-01 定义 task/attempt 身份；用户明确选择后，agent-dispatch 才创建 fresh Agent。

seed ready 不等于 task 已创建，不产生 Plan 或未来 phase 授权。

## 与 modeling / Work Unit 的边界

modeling Do 可以通过 EVOLVE/TREE/NODE 形成新的 node candidate 与 qualification evidence，
但 DECOMP 只消费**已固定**的 node/tree revision，不把草稿 candidate 直接派发。

Do-only Work Unit 不是 DECOMP 对象。它没有新 node_id/ontology responsibility，只按 CONTRACT-01
组织现有 task Do 内的局部执行。文件数、LOC、工时、token、并行度、Agent 数量/置信度、
单个命令或测试步骤都不能单独产生正式 task seed。
