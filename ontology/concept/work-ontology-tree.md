---
schema: pdca.asset/v2
id: ontology:concept/work-ontology-tree
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: TREE-01：用户确认目标组成树
---

# TREE-01：用户确认目标组成树

工作使用根节点、直接组成关系与稳定node_id。每个节点有独立职责、输入输出和可验收义务；从根向叶建模，每个新孩子由自己的Agent评估是否进一步分解。父只提出seed，不替孩子完成建模，不为每个文件／操作机械创建节点。

节点种子固定后报告给用户；用户选择要启动的具名孩子。父本地完整PDCA不等待后代或整树冻结，避免循环等待；其交付不能声称孩子已实现。

最终树清单列完整节点集合、组成边、定义版本、各场景AC与必需性、未决问题。检查根唯一、父关系、无组成环、无失踪节点和目标覆盖；用户对具体清单作冻结确认。冻结只是允许据此规划，不自动启动projection。

树不是全部知识图：领域关系可多样，组成关系需明确。不能只生成调度树而不建立被研究领域的本体对象。需求是原始判断依据，本体不成为无需核验的真理。

旧树／旧确认保存；改变目标或节点义务产生候选新版本与影响说明，用户明确采用，不静默减少必需节点或场景。
