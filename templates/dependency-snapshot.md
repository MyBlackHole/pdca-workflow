---
schema: pdca.dependency-snapshot/v1
work_id: null
tree_revision: null
graph_revision: null
scope: null
parent_graph_ref: null
parent_graph_digest: null
vertices: []
edges: []
input_manifest_refs: []
producer_ref: null
protocol_revision: 3.4.10
---

# 不可变工作实例依赖图草稿

vertices含完整work/tree/node/scene或具名工作事件身份，edges为producer→consumer并记录边类型、来源节点/约束、artifact、required。不把weak relates_to/guides加入边。图本身不写自身摘要；检查回执引用图文件真实digest。

## 完整性

缺端点/来源、自环、重复身份、无生产者的输入不得通过。按场景导出组成前置并与显式输入联合检查；合法跨场景顺序不能压成无scene假环。candidate不等于已授权published图。
