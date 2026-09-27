---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# Ontology revision delta：记录格式

本契约只保存 EVOLVE-01 的 **M1 → M2 revision proposal / fixed revision provenance**。
它不表示当前 task 已采用 M2，也不生成 TREE/NODE/task seed。

## 示例

```markdown
---
schema: pdca.ontology-revision/v4
protocol_revision: 4.0.0-rc.5
task_id: null
attempt: null
definition_id: null
base_revision: null
proposed_revision: null
payload_ref: null
payload_digest: null
requirement_refs: []
source_refs: []
change_set: []
constraint_checks: []
unknown_claims: []
adoption_ref: null
---

# Ontology revision delta

`base_revision` 是固定 M1；首次 root modeling 可以真实为空。
`proposed_revision + payload_ref/digest + change_set` 固定 M2 candidate 与来源/requirement/constraint 检查。对 project ontology，`payload_ref` 作为该 revision 的唯一 **model root ref**：从它必须能够解析 ONTOLOGY-01 要求的 definitions、work instances、relations、constraints、requirement coverage、provenance 与 unknown；`payload_digest` 固定完整 revision payload，而不只是 root 文件字节。

Modeling Act 固定 M2 后，这份记录可以作为 revision provenance；但其他 task 是否采用该 revision 仍由 ADOPT-01
通过既有 task/assignment/baseline refs 明确绑定。`adoption_ref` 只允许指向这样的下游采用事实，
不是“字段非空即可自动 adopted”的开关。

definition revision 与 work node/tree/task identity 分开；TREE/NODE/DECOMP 分别处理结构投影、节点资格与 task seed。
```
