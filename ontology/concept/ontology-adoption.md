---
schema: pdca.asset/v2
id: ontology:concept/ontology-adoption
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-27'
summary: ADOPT-01：把固定 ontology revision 显式绑定为当前输入
---

# ADOPT-01：Fixed input binding

ADOPT-01 只回答：**哪个固定 ontology definition/revision 被当前 work/task 正式采用，以及适用于什么范围。**
它不创建/修订 ontology，不改变 reference 生命周期，也不发布共享知识。

一次采用至少固定：

- source container / definition revision identity 与 payload/content digest；
- **adopted semantic units**：实际采用的 definition / relation definition / constraint / claim refs；
- adoption target：project/work/task/scene 中的具体对象；
- applicable requirements/claims；
- explicit exclusions：同一 source 中明确不采用的历史关系、validation recipe、local path 或其他 material claim；
- limitation / unknown / environment assumptions；
- adoption authorization/decision ref。

候选可以来自 REUSE-01 的 reference，也可以是项目 modeling 已固定的新 ontology revision。
无论来源为何，都必须绑定**具体 revision/content**，不能绑定“latest”“active”或会随库变化的别名。

## 采用不是验证或升级

采用只表示“这些被明确选择的固定 semantic units 现在是当前输入”：

- 不表示 source container 的全部 claims/relations/recipes 都被采用或已验证；
- 不使 reference 自动成为 normative rule；
- 不改变其他 task 已固定的 revision；
- 不因库出现新版本而自动升级；
- 不把旧 evidence/PASS 复制到新 revision。

source/container 缺失、digest 漂移、被采用 semantic unit 无法解析或适用条件不再成立时，停止依赖该输入的受影响动作并报告；
不能仅凭旧摘要或替代链接静默继续。

新 revision 是否产生由 EVOLVE-01 决定；采用后的 dependency/context 失效由 DEPENDENCY-01 / CONTEXT-01 消费。


## 落地而不新增 schema

ADOPT 不要求新建 adoption manifest。当前 task/work 的采用事实直接落到已有 task/assignment/baseline 的固定 definition/input refs；这些 refs 应能定位 adopted semantic units、source revision/digest、适用范围与 exclusions，并引用对应 authorization/decision。需要 provenance 时可由 ontology-revision 的 `adoption_ref` 指向该既有绑定；该字段只是下游采用指针，不使 proposed revision 自动变成 adopted input。
