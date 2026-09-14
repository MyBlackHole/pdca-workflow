---
schema: pdca.asset/v2
id: ontology:concept/work-node-contract
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: NODE-01：定义与实例必须真实存在
---

# NODE-01：定义与实例必须真实存在

modeling节点交付同时涵盖领域定义和工作实例：稳定定义id/revision、属性语义（类型／单位／范围）、关系端点及含义、约束／不变量、适用实例或明确不适用理由、来源与unknown；工作实例绑定node_id和各场景义务。

允许Markdown+结构化frontmatter，不按扩展名判是否本体。每个主张能定位到内容与来源；路径／列表标题不足以表达关系和约束。复用既有定义需固定版本、比对适用性并保存采用记录；无需为了“有新文件”复制同一模型。

每节点记录直接子seed或leaf理由、输入/输出、验收标准及方法；每个孩子独立评估，不固定深度或默认无限展开。没有可独立拒收的部分时保留为节点内部步骤。

modeling完成时交付清单必须列实际本体源和工作实例、内容摘要、验证范围与缺项；任务日志和计划不能代替模型。后续projection与verification按同一固定定义工作，未运行明确not_run。
