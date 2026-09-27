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
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: ADOPT-01：把固定 ontology revision 显式绑定为当前输入
---

# ADOPT-01：Fixed input binding

ADOPT-01 只回答：**哪个固定 ontology definition/revision 被当前 work/task 正式采用，以及适用于什么范围。**
它不创建/修订 ontology，不改变 reference 生命周期，也不发布共享知识。

一次采用至少固定：

- definition/revision identity；
- payload/content digest 与真实来源；
- adoption target：project/work/task/scene 中的具体对象；
- applicable requirements/claims；
- limitation / unknown / environment assumptions；
- adoption authorization/decision ref。

候选可以来自 REUSE-01 的 reference，也可以是项目 modeling 已固定的新 ontology revision。
无论来源为何，都必须绑定**具体 revision/content**，不能绑定“latest”“active”或会随库变化的别名。

## 采用不是验证或升级

采用只表示“这个固定定义现在是当前输入”：

- 不表示其全部 claims 已验证；
- 不使 reference 自动成为 normative rule；
- 不改变其他 task 已固定的 revision；
- 不因库出现新版本而自动升级；
- 不把旧 evidence/PASS 复制到新 revision。

源文件缺失、digest 漂移或适用条件不再成立时，停止依赖该输入的受影响动作并报告；
不能仅凭旧摘要或替代链接静默继续。

新 revision 是否产生由 EVOLVE-01 决定；采用后的 dependency/context 失效由 DEPENDENCY-01 / CONTEXT-01 消费。
