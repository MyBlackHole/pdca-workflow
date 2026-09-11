---
schema: pdca.maintenance-regression-suite/v1
suite_id: formal-record-relations-v343
protocol_revision: 3.4.3
basis_ref: ../../examples/formal-records/expectations.md
subject_ref: ../../examples/formal-records/single-leaf
scope: candidate mutations with fixed independent basis; not AI executions or checker-mutation kills
cases:
- case_id: N01
  title: 门禁authority/observation缺失
  expected_code: gate_authority
- case_id: N02
  title: Check门禁错误绑定其他任务review
  expected_code: gate_subject_binding
- case_id: N03
  title: 门禁证据为悬空裸引用
  expected_code: gate_evidence
- case_id: N04
  title: 观测属于其他task/attempt
  expected_code: observation_identity
- case_id: N05
  title: 可见输入清单整体删除
  expected_code: visible_input_members
- case_id: N06
  title: 证据保留清单整体删除
  expected_code: evidence_members
- case_id: N07
  title: 容器身份共同改为其他work/tree/root
  expected_code: manifest_container_identity
- case_id: N08
  title: 根把自己列为父和孩子
  expected_code: hierarchy_self_cycle
- case_id: N09
  title: modeling交付与终态角色交换
  expected_code: manifest_role_type
- case_id: N10
  title: 约束映射local ID不存在
  expected_code: binding_local_constraints
- case_id: N11
  title: 显式宣称答案已暴露
  expected_code: declared_answer_exposure
- case_id: N12
  title: Check包phase写成plan
  expected_code: review_phase
- case_id: R13
  title: 仅缺一个观测引用
  expected_code: gate_observation_reference
- case_id: R14
  title: 元素级subject指向另一对象
  expected_code: gate_item_subject
- case_id: R15
  title: 权威ID拼写错误
  expected_code: gate_authority
- case_id: R16
  title: 观测run ID错配
  expected_code: observation_identity
- case_id: R17
  title: 观测有效case摘要错配
  expected_code: observation_case_digest
- case_id: R18
  title: 观测checker版本错配
  expected_code: observation_checker
- case_id: R19
  title: 观测可见输入版本错配
  expected_code: observation_visible_inputs
- case_id: R20
  title: 可见清单attempt不属于run
  expected_code: visible_input_identity
- case_id: R21
  title: 证据清单run不属于run
  expected_code: evidence_identity
- case_id: R22
  title: 保留观测但漏掉检查方法
  expected_code: evidence_members
- case_id: R23
  title: 可见清单成员重复
  expected_code: visible_input_members
- case_id: R24
  title: 树节点文件和tree-spec父子关系不一致
  expected_code: hierarchy_node_binding
- case_id: R25
  title: 层级树根不可达孤儿
  expected_code: hierarchy_unreachable
- case_id: R26
  title: 叶children声明未提供节点
  expected_code: hierarchy_missing_child
- case_id: R27
  title: 观测attempt使用布尔true
  expected_code: observation_identity
- case_id: C01
  title: 清单对象重排合法
  expected_code: null
- case_id: C02
  title: 允许的非授权扩展说明
  expected_code: null
- case_id: C03
  title: 合法额外可见输入不应拒绝
  expected_code: null
- case_id: C04
  title: 证据集合重排不改变成员含义
  expected_code: null
- case_id: C05
  title: 显式元素subject绑定当前gate
  expected_code: null
- case_id: C06
  title: 叶的空children合法
  expected_code: null
- case_id: C07
  title: 额外保留固定原始资料合法
  expected_code: null
- case_id: C08
  title: 当前观测的非授权备注合法
  expected_code: null
---

固定预期由维护套件提供，不从被审候选生成。每项在副本修改，重算关联摘要后执行；必须出现指定关系诊断，不能用无关解析/摘要失败替代。合法控制必须无诊断。实际变体、diff和输出保存在独立验证附件。
