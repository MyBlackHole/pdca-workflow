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

# VERDICT-01：Evidence → Check verdict；final delivery dimensions 保持分离

VERDICT-01 主要回答：**如何把当前固定 subject 的必需 evidence 聚合为 Check 的 AC 结果与 subject_conformance。**
它同时定义最终交付中几个维度为什么必须分开，但不让 Check 提前计算 Act/scene 才能确定的事实。
它不执行测试、不产生 evidence、不决定用户下一步授权。

## AC aggregation

每个必需 AC 使用 EVIDENCE-01 的 `pass/fail/unknown/not_run`，并保留 evidence refs：

- 任一必需 AC 有确定 fail，subject_conformance 不能 PASS；
- 任一必需 AC 为 unknown/not_run，不能用多数 PASS 覆盖，整体保持相应不确定；
- 只有当前 subject 的全部必需 AC 有足够 evidence 且无阻断反证，才能得到 conformance PASS；
- 可选维护建议不能伪装成必需 AC fail。

新的 subject/version 不能复用旧 verdict；必须重新聚合对新 subject 仍有效的 evidence。

## Check verdict 与最终交付维度分开

Check 当前直接聚合的只有：

- **acceptance_results**：逐 AC 的 pass/fail/unknown/not_run；
- **subject_conformance**：当前固定 subject 是否符合这些必需 AC/oracle。

最终 delivery 还会引用三个独立事实维度：

- **task_execution**：由 TRANSITION/STATE 的真实生命周期事实决定；
- **delivery_usable**：由完成后的具体 Act 处置、限制与真实发布/使用范围决定；
- **scene_coverage**：由 model / implement / verify 的实际 task/records 决定。

因此 Check 不应提前把“conformance PASS”写成 `delivery_usable=true`，也不能因为 verify 尚未运行就伪造 scene coverage。
正确发现 fail 的 Check/Verify task可以最终 task_execution=completed，同时 subject_conformance=fail。

用户风险接受、失败归档或发布处置不能改写 evidence/subject_conformance；
它们只影响后续 Act/delivery 事实，未运行的 scene 保持 not_run。

工作级整体完成需要固定节点集合、必需 scene coverage、组合/依赖符合及无阻断 unknown；
不能由单个 task verdict 推导整个 work PASS。
