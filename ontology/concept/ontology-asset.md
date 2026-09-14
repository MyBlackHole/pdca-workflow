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
dcterms_modified: '2026-09-14'
summary: ONTOLOGY-01：本体源是可检验语义，不是文件格式
---

# ONTOLOGY-01：本体源是可检验语义，不是文件格式

本体源应能识别对象、属性、关系、约束／不变量、实例适用性、来源和unknown。每个对象有稳定id、版本及固定字节；关系端点解析到对象；约束有可观察预期。允许Markdown、YAML或已有项目格式，不以扩展名判断专业性。

知识地图可作为资料，也可在满足上述条件后被采用为模型；仅有代码链接、章节和说明不自动达到模型要求。工作树是目标分解，还需要领域定义；两者分别交付。

领域模型统一登记在PDCA_ROOT/ontology/projects/<project>/works/<work>/<revision>，工作实例、映射和引用在集中records中固定。已有外部模型可明确采用实际位置及版本，不强行搬文件。公共库只读采用，获准Act才共享发布；任务草稿不能覆盖公共定义。规则、知识、模型和records虽在同一中心，写域仍分开，不自动使用latest。

模型必须对用户需求和事实负责。模型与投影互相一致却同样遗漏用户需求，仍不符合。未知主张留unknown；无适用实例等情形明确理由，不强行制造实例或PASS。
