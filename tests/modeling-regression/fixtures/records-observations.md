---
schema: pdca.records-observation-fixture/v1
fixture_only: true
source_archive: records.tar(2).gz
source_archive_sha256: 551d3c5ed67a0591da9ee741072692c512951c9c4e406e9337fc6b0c816f65fb
source_markdown_files: 24
checks:
  manifest_tree_digest: 3405e26ee429663ccb6047923f56f36a80ef656fdd2bf6b11eeed47e4d3acf77
  actual_tree_digest: 5ee3171439a9b30c11807637e0e5e2d7813a5b1753365d5fdd235d7f104b0801
  digest_mismatch: true
  future_suite_placeholders: 10
  local_scope_attempt_mismatch:
    reuse_attempt: 2
    capability_attempt: 1
excerpts:
- source: works/ontology-conformance-review-20260912/trees/v0.1-candidate/nodes/scope-evidence-adoption.md
  sha256: f1a16947ba4dbe65710683dc06c210b80aecbab1e86135816afd01815899d67c
  line_start: 344
  text: "- 复杂度与拆分终止理由：叶无孩子，不再拆分；禁令边界以 ONTOLOGY-01 两节与\n  NODE-01 事实段为界，若后续整树确认要求增减禁令项，按 TREE-01 以本节点新\n  attempt\
    \ 或父新 attempt 处理，不在本任务内擅自扩大。"
- source: works/ontology-conformance-review-20260912/trees/v0.1-candidate/nodes/root-review-scope.md
  sha256: 5533c3d833996db6d1d59ac928990cf9a7784d5f0f3aa179c51446ed3dd52105
  line_start: 285
  text: "    无此类断言→案例 pass（拒绝了错误模式）。\n  - M-N2（反例，RC-03/RC-07）：若 quarantined 资料被用作 oracle，或复制模板示例\n    expected\
    \ 为 actual→必须 fail。本次实际观测：无→pass。"
- source: works/ontology-conformance-review-20260912/trees/v0.1-candidate/capability-check.md
  sha256: fb995b08852b85de859b1b6bc3570de841316035ba9ae68f4da603456aec3850
  line_start: 88
  text: "  在本任务中均不执行，与授权范围（不做冻结）一致，故 Plan→Do 可放行于\n  draft 草稿写域；解除 blocked 需新证据，本文件不伪造恢复。"
- source: works/ontology-conformance-review-20260912/trees/v0.1-candidate/reuse-decision.md
  sha256: a40f2c3bd650564583ce5a7fef8c69c8da5eee32ad194c89ebb8b8bbf0c63f37
  line_start: 17
  text: '- records/

    queries:

    - qid: Q1'
---

# 真实records派生的只读负例

本文件仅摘录本轮实际上传包的少量原文及机械事实，不包含原用户消息、真实Agent/授权的证明。原包未改；不把其失败材料复制为新的活动records。

可以实际重算的事实：manifest固定的旧tree摘要与当前tree.md不匹配；五节点未来两场景共有十个未定义占位；同一节点reuse与capability的attempt不同。它们分别对应K14/K17/K19。

“叶无孩子，所以不再拆分”和“当前无此断言，所以反例已通过”作为K07/K18的错误理由来源；摘录不是一个完整语义检测器。真实宿主任务是否发生不由本文件推断。原确认存在性与真实性必须向实际来源核验，不编造反证。
