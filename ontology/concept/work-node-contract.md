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
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: NODE-01：工作节点是本体对象/关系在当前工作的可验收实例
---

# NODE-01：工作节点是本体对象/关系在当前工作的可验收实例

正式 work node 不能只是一段任务描述。它必须绑定固定 ontology revision 中的领域定义和当前 work instance，
并能说明本节点与父节点、依赖节点以及目标实体之间的语义关系。

## 节点最小语义

每个节点至少固定：

- `node_id`；
- ontology object / work instance ref；
- ontology revision；
- responsibility：本节点独立负责什么；
- inputs / outputs；
- relation endpoints：与父、依赖或被组合对象的必要关系；
- constraints / invariants；
- acceptance criteria / oracle；
- scene obligations：model / implement / verify 哪些是必需、哪些 not_run；
- child seeds 或 leaf 理由；
- unknown 与来源。

路径、目录、列表标题、文件数量或 Agent 自述不能替代上述语义。

## 正式任务资格

一个 ontology object/work instance 只有同时满足以下条件，才可成为正式任务节点：

1. 在当前目标中具有明确且独立的语义职责；
2. 输入/输出可以固定；
3. 相关 relation / constraint 可以定位；
4. 产物可以被独立拒收；
5. 存在独立验证边界；
6. 与父/兄弟的组合责任可以说明。

如果一个部分只有机械操作意义，例如“改三个函数”“新增一个测试文件”“运行一次命令”，
但没有独立 ontology responsibility，则保持为节点内部步骤或 Do-only Work Unit。

## 同一节点跨场景保持身份

同一个 `node_id` 在 model / implement / verify 三个场景中保持同一语义身份：

```text
node ontology meaning
        |
        +-- pdca-model      定义/固定该节点语义
        +-- pdca-implement  将同一节点投影到真实实体
        +-- pdca-verify     验证同一节点的需求->模型->实现->行为
```

scene task 可以不同，但不能在 implement/verify 中静默重定义节点职责。
模型根本缺失或错误时应停止并提出新的 modeling 工作，而不是在后续场景重新发明任务树。

## 上下文边界

节点定义也是上下文隔离的锚点。正式 task 只应得到该 node 所需的 ontology 子图、
固定父 seed、依赖交付、共享不变量和 scene 输入；不继承父/兄弟完整活动历史。

modeling 完成时交付清单必须列实际本体源、work instance、node/关系、内容摘要、验证范围与缺项。
任务日志和计划不能代替模型。
