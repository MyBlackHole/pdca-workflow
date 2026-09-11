---
schema: pdca.maintenance-contract/v1
suite_id: formal-records-342
revision: 1.0.0
authority_refs:
- CONTRACT-01
- TREE-01
- SCENE-01
- GATE-01
- TRANSITION-01
- CASE-01
- DEPENDENCY-01
subject_ref: ../../examples/formal-records/single-leaf/index.md
basis_ref: ../../examples/formal-records/expectations.md
test_layer: structural_relational
case_count: 43
semantic_result: NOT_RUN
host_result: NOT_RUN
---

# 正式记录结构与关系的对抗回归

独立维护附件formal_challenges.py实现下列精确材料变更；每例使用同一固定basis，重算候选引用摘要后运行未修改的检查方法。必须出现指定关系/字段诊断，不能靠无关解析或摘要错误代替。合法近邻不得误拒绝。此处为输入扰动案例，不汇总成“击杀错误检查器”。

| ID | 实际注入 | 必须观察 |
|---|---|---|
| FR01 | 删除整项graph_check清单对象 | manifest_required_roles |
| FR02 | 删除全部节点绑定 | manifest_nodes |
| FR03 | 候选清单和绑定同步删除场景 | manifest_scenes |
| FR04 | 清空案例oracle但字段存在 | field_contract |
| FR05 | 图回执明确cyclic不能放行 | graph_result |
| FR06 | 删除全部图顶点 | graph_vertices |
| FR07 | 节点自身身份与binding不符 | node_identity |
| FR08 | 四份记录同时缺身份 | field_contract |
| FR09 | Plan响应/决策改成Check | confirmation_edge |
| FR10 | 第二条边使用不同基线 | baseline_drift |
| FR11 | attempt用bool冒充整数 | field_contract |
| FR12 | 本地来源案例映射清空 | binding_constraints |
| FR13 | suite同时删除ME14及其必需标记 | case_coverage |
| FR14 | 声明必需案例为可选 | case_required |
| FR15 | 重复清单对象ID | duplicate_object_id |
| FR16 | 重复case结果 | duplicate_case_result |
| FR17 | 终态冒用旧attempt | identity |
| FR18 | 第四条转换边类型错误 | chain_edge |
| FR19 | 首条链前驱不为空 | chain_previous |
| FR20 | 确认决策未消费 | field_enum |
| FR21 | source oracle被本地改写 | binding_semantic_override |
| FR22 | 删除门禁必需谓词 | gate_predicate_coverage |
| FR23 | 图新增真实长环 | graph_algorithm |
| FR24 | 图端点不存在 | graph_algorithm |
| FR25 | 图回执统计与实际不符 | graph_counts |
| FR26 | 图必需边被删，仍然无环 | graph_required_edges |
| FR27 | 删除实际run案例但交付声称局部通过 | run_coverage |
| FR28 | run的有效案例身份错配 | run_case_identity |
| FR29 | 观察来自旧产物 | observation_binding |
| FR30 | 检查包改成另一任务的run | review_run |
| FR31 | fixture交付谎称可用于生产 | fixture_delivery_claim |
| FR32 | 正常归档串接另一任务交付 | archive_delivery |
| FR33 | 正式request使用旧简化字段 | unknown_record_fields |
| FR34 | 物理删除必需正式终态文件 | object_missing |
| FR35 | 空白task身份不等于有效ID | field_contract |
| FR36 | 归档链核验列出空回执集合 | archive_chain_members |
| FC01 | 清单对象重排合法 | 结构/关系通过 |
| FC02 | 无关正文说明不影响结构 | 结构/关系通过 |
| FC03 | 叶children为空合法 | 结构/关系通过 |
| FC04 | 非必需草稿字段null允许 | 结构/关系通过 |
| FC05 | task可选扩展说明不改变契约 | 结构/关系通过 |
| FR37 | 固定基线下图重排仍需新确认 | basis_baseline |
| FR38 | 删除真实固定引用的依赖声明 | manifest_dependency_coverage |

FR37专门区分：无环算法对边枚举顺序不敏感；已经确认的图字节重排却改变基线引用，不能不经新确认直接沿用。测试夹具初次将二者混为一个“合法全链正例”，该错误期望及修正记录保存在维护附件，不削弱基线检查来迎合它。
