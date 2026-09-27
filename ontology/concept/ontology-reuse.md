---
schema: pdca.asset/v2
id: ontology:concept/ontology-reuse
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-27'
summary: REUSE-01：检索和评估候选 reference，不把命中自动变成任务输入
---

# REUSE-01：Reference candidate discovery

REUSE-01 只回答：**当前目标是否有值得复用的固定候选定义，以及候选的来源/版本/适用性缺口是什么。**
搜索命中、相似标题、同领域或 `authority: reference` 都不等于已采用。

## 候选输出

只在当前获准项目/共享知识源中检索，候选至少固定：

- definition/reference id；
- revision / digest / 实际来源位置；
- provenance 与 claim verification 状态；
- 与当前 requirement/work 的拟适用部分；
- 已知限制、冲突和 unknown；
- 建议动作：reuse / local_extension / revise / create。

候选只进入“待评估材料”，不自动进入 assignment/baseline/model。
候选应尽量按 **semantic unit** 标识可复用范围，例如 definition、relation definition、constraint、claim；一个 reference file 只是来源容器，不默认表示其中所有正文、历史关系、validation recipe 或 local path 都应被采用。
只有 ADOPT-01 才能把选中的固定 candidate units 变成当前 work/task 输入。

不复制整个知识库，不导入候选的原会话/活动历史，也不因为资料更详细就让它覆盖当前 normative authority。
候选包含 retired rule 引用、unverified claim、environment-local path 或历史 task 结论时，必须把这些作为 limitation/unknown 暴露，不能随 candidate 一并升级成 current evidence。

## Reference lifecycle

本节只管理 `authority: reference` 资产作为**候选库条目**的可检索状态，不管理项目模型或已采用输入。

| reference 状态 | 候选语义 |
|---|---|
| active | 可作为新检索候选；仍需逐主张核对来源/版本/适用性 |
| archived | 保留历史正文，一般不作为新采用候选；恢复 active 需新的审查与获准修改 |
| retired | 仅保留兼容定位/指针；不能把指针当定义正文采用 |

active 不等于 verified/PASS；archived/retired 也不会自动迁移或撤销已经固定采用旧 revision 的 task。
原始来源缺失时如实标 unknown，不补造旧正文或证据。

去重/归档按对象语义、独立主张、来源、版本和实际用途判断，不按字数、年龄、引用次数或置信度阈值批量处置。
reference lifecycle 的修改需要对应知识库写域授权，并以新的 revision/可追溯 Git 变化保留旧状态事实；不能原地抹掉历史来源或让旧 task 引用随 status 变化。共享发布也不是 REUSE 的默认副作用。
