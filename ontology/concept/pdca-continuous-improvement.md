---
schema: pdca.asset/v2
id: ontology:concept/pdca-continuous-improvement
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: LEARN-01：把已有 evidence 提炼为可复用知识 candidate，不自动发布或采用
---

# LEARN-01：Evidence → Learning candidate

LEARN-01 只回答：**已有 task evidence 中是否存在值得保留的可复用经验，以及这个 learning candidate 的适用边界是什么。**
它不改变原 verdict，不自动写项目上下文/共享 ontology，也不让其他 task 自动采用。

## Learning candidate

候选至少保留：

- source task/attempt/subject/version；
- environment / preconditions；
- 支持 evidence 与 counterevidence；
- 可复用的具体 claim/heuristic；
- applicability / non-applicability；
- unknown / limitation；
- invalidation / re-evaluation condition。

一次成功、单一环境、一个 reviewer 共识都不能自动升级成普遍规律；
建议、经验和 normative constraint 分开。

没有足够新知识时不生成 candidate；不为了“四阶段完整”强造经验或写 `none` 文件。

## Persist / publish / reuse 分开

- **仅本次 Act 报告**：可以把 candidate 作为结果中的说明，不产生额外知识库写入；
- **局部持久化**：只有当前 Act 明确批准具体对象/路径/写域时才写；
- **共享 reference 发布**：只有 Act 明确批准共享发布，且真实写入成功后，才成为 REUSE-01 可检索的 reference candidate；
- **其他 task 使用**：即使已共享发布，也必须由该 task 的 REUSE → ADOPT 明确绑定，不能自动注入。

LEARN 不创建新的 ontology revision；若经验实质要求修改模型，进入 EVOLVE-01 candidate。
也不因为学到“下次应做什么”自动创建 task/attempt/scene；后续工作仍由 DECOMP/SCHED/REWORK/TASK 等相应规则产生候选。
