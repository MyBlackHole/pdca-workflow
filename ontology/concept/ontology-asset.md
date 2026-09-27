---
schema: pdca.asset/v2
id: ontology:concept/ontology-asset
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: ONTOLOGY-01：定义什么才是可采用的本体语义源
---

# ONTOLOGY-01：本体语义源资格

ONTOLOGY-01 只回答：**一个定义/模型资产是否具备可定位、可比较、可检验的本体语义。**
它不负责检索、采用、修订、工作树投影或任务拆分。

一个可用 ontology definition/revision 至少应能固定：

- 稳定 definition/object identity；
- revision 与内容 digest/固定位置；
- objects/entities 与必要 attributes；
- semantic relations 及可解析端点；
- constraints / invariants 与可观察预期；
- applicable work/instance 或明确的不适用边界；
- requirement/source/provenance；
- unknown / unverified claims 与 limitation。

Markdown、YAML、数据库或项目已有格式都可以承载上述语义；文件扩展名、章节数量、代码链接或知识地图标题本身都不能证明“已经是模型”。

## 与生命周期链的边界

- REUSE-01：在获准来源中寻找符合本页要求的候选；
- ADOPT-01：把一个固定 revision 显式绑定为当前 work/task 输入；
- EVOLVE-01：从固定模型产生候选新 revision；
- TREE-01 / NODE-01：把已固定 ontology/work instance 投影成工作结构；
- DECOMP-01：从合格工作节点形成正式 task seed。

ONTOLOGY-01 不执行上述动作，也不把 reference 自动提升为当前模型。

项目模型可集中保存在 `PDCA_ROOT/ontology/projects/<project>/works/<work>/<revision>`，
也可显式引用获准的外部固定模型；位置不改变语义要求。规则、公共知识、项目模型和 task records
仍是不同写域，不能因为同处 PDCA_ROOT 就互相覆盖或默认采用 latest。
