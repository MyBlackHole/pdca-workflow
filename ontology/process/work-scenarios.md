---
schema: pdca.asset/v2
id: ontology:process/work-scenarios
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-14'
summary: SCENE-01：本体源—投影—符合性，场景间也等用户
scene_ids:
- ontology_modeling
- ontology_projection
- ontology_conformance_verification
scene_start_policy: explicit_user_operation
---

# SCENE-01：本体源—投影—符合性，场景间也等用户

三个场景固定为ontology_modeling、ontology_projection、ontology_conformance_verification。每个场景的每个正式节点都是独立任务，自己的Agent执行四阶段；不能用三个场景冒充Plan/Do/Check。

## ontology_modeling

输入用户确认目标、固定事实来源与复用定义。Do建立领域本体源及工作实例：对象id、属性语义、关系端点／含义、约束与不变量、适用实例或理由、来源和未知。保存在集中PDCA_ROOT/ontology/projects/<project>/works/<work>/<revision>或明确采用的已有模型位置，不以任务日志、七份知识文档或只含调度节点的树自动替代。

Check对照原需求、定义与来源验证覆盖和约束，既检查结构也检查语义；没有模型就记录缺失，不能重解释场景名使其通过。模型可以Markdown+frontmatter，不强制YAML文件或专用生成器。复用也要有固定定义、采用依据和实际实例。

Act在批准范围内固定model release／节点seed及场景覆盖；本地完成、整树冻结和知识发布分开。提出后续任务建议，**不自动启动孩子或projection**。

## ontology_projection

输入固定且获准采用的模型版本、工作目标与投影规则。Do生成代码、文档、配置或其他真实实体；记录每项需求／模型对象／约束对应哪个目标位置、如何映射和如何验证。可由Agent写，也可工具生成；必须忠实映射，不禁止合理人工写作。

Check既检查source→target遗漏，也检查target→source无依据增加，并运行所需业务测试。仅有目标文件而没有模型源／映射不足以称投影完成；纯hash和链接不证明行为。

Act固定目标release和映射，未运行verification仍标not_run，不自动进入第三场景。

## ontology_conformance_verification

用户显式启动新的独立审查任务，读取原需求、同版本模型、固定投影及实际证据。分别判断需求→模型、模型→投影、产物→行为；不允许错误模型与错误投影互相证明。

审查Agent不修改被审业务产物或oracle。Plan固定验证问题和标准；Do实施检查并产生报告；本任务Check核验这些检查是否实际发生、覆盖是否足够以及结论是否被证据支持，不递归再建审查Agent。Check报告pass/fail/unknown及证据和反证；原始命令失败不等于对象失败，未检查不等于通过。Act由用户选择接受、仅归档或提出返工／发布；真实违例不能被认可消息覆盖。

## 覆盖与依赖

N节点首次完整三场景需要3N任务覆盖；未获准或未运行明确not_run，不自动创建来凑数量。内部节点要验证实际组合。失败任务可诚实收尾，不能让delivery_usable=true掩盖模型／产物缺失。每次启动既需要输入ready，也需要具体用户操作。
