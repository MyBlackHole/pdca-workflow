---
schema: pdca.asset/v2
id: ontology:concept/pdca-verdict
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: VERDICT-01：只聚合 evidence，不把执行成功混成对象符合
---

# VERDICT-01：Evidence → Verdict

VERDICT-01 只回答：**如何把当前固定 subject 的必需 evidence 聚合为 task Check 结论。**
它不执行测试、不产生 evidence、不决定用户下一步授权。

## AC aggregation

每个必需 AC 使用 EVIDENCE-01 的 `pass/fail/unknown/not_run`，并保留 evidence refs：

- 任一必需 AC 有确定 fail，subject_conformance 不能 PASS；
- 任一必需 AC 为 unknown/not_run，不能用多数 PASS 覆盖，整体保持相应不确定；
- 只有当前 subject 的全部必需 AC 有足够 evidence 且无阻断反证，才能得到 conformance PASS；
- 可选维护建议不能伪装成必需 AC fail。

新的 subject/version 不能复用旧 verdict；必须重新聚合对新 subject 仍有效的 evidence。

## 四个维度分开

- **task_execution**：这个 PDCA task/run 是否按自身流程完成；
- **subject_conformance**：被审对象是否符合固定 AC/oracle；
- **delivery_usable**：最终交付是否在当前明确处置/限制下可用；
- **scene_coverage**：model / implement / verify 哪些真的运行并有据。

正确发现 fail 的 Check/Verify task 可以 task_execution=completed，同时 subject_conformance=fail。
task archived 也不等于整个 work 或所有 scene 已完成。

用户风险接受、失败归档或发布处置不能改写 evidence/subject_conformance；
具体处置由 Act 记录，未运行的 scene 保持 not_run。

工作级整体完成需要固定节点集合、必需 scene coverage、组合/依赖符合及无阻断 unknown；
不能由单个 task verdict 推导整个 work PASS。
