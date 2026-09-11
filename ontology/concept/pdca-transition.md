---
schema: pdca.asset/v2
id: ontology:concept/pdca-transition
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.2
summary: 单阶段转换、回执与幂等
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-gate
  - ontology:concept/pdca-recovery
  - ontology:concept/runtime-transition-coordinator
  - ontology:entity/transition-plan-do
  - ontology:entity/transition-do-check
  - ontology:entity/transition-check-act
  - ontology:entity/transition-act-archive
  - ontology:concept/task-control
  - ontology:concept/resource-ownership
  - ontology:concept/pdca-phase-status
transition_protocol:
  receipt_key:
  - task_id
  - sequence
  sequence_allocator: bound_task_writer_from_fixed_edge
  edge_sequence:
    plan_to_do: 1
    do_to_check: 2
    check_to_act: 3
    act_to_archive: 4
  control_events_share_sequence: false
  business_operations_share_sequence: false
  conflicting_receipt: block_preserve_both
---

# 固定阶段序号、回执与业务幂等分离

## TRANSITION-01：只有四条正常边

每个transition个体的transition_spec给出from/to/gate_id/sequence；本节点定义唯一编号协议。由当前task的合法记录写入者（绑定Agent）按固定表产生编号，不使用全项目自增计数，也不拿文件mtime决定顺序。

| sequence | from | to | gate_id |
|---|---|---|---|
| 1 | plan | do | plan_to_do |
| 2 | do | check | do_to_check |
| 3 | check | act | check_to_act |
| 4 | act | archive | act_to_archive |

回执唯一键为(task_id,sequence)，task_id唯一绑定work/tree/node/scene/attempt。新attempt可以从1开始，不与旧任务去重；同task序号固定对应一条边，失败门禁核验只作诊断，不占编号。control事件使用CONTROL-01的event_id/control_revision；业务调用使用RESOURCE-01的operation_id，三者不混用。

## 提交协议

1. 读取task固定协议版本、当前phase、最后完整链、基线/输入包、可信control视图和实际记录写权。必须不是stopping/interrupted，合法Agent身份与owner一致。
2. 按GATE-01核对当前边；Plan/Check确认引用真实request-decision，不把普通消息当已消费批准；固定不可变输入清单并计算摘要。
3. 构造`transitions/<sequence>-<from>-<to>.md`：task/attempt、固定边、previous_receipt_digest（首条为null）、baseline_digest、inputs_digest与输入清单、gate/confirmation_decision/test/result引用、actor、writer_grant、observed_control_revision、状态矩阵版本。签名或可信来源是宿主事实，哈希不是身份凭证。
4. 在真实记录所有权/准入边界复核control_revision未被停止/撤权事件替代，提交完整回执并重读，再更新task快照的phase/last_transition。要求硬保证时同一宿主原子边界验证控制资格和提交；没有这种能力只允许已确认合作式隔离范围，不把读两次称为CAS。回执commit_receipt_ref记录实际可用保证和限制。
5. 归档前业务动作已停止且无未知未决副作用；序号4持久化后task=archive/completed，当前Agent完成最后快照更新并停止记录写入。宿主取得交回证据再封存、释放槽/资源，不能在第四回执生成前先收走记录写权造成无法归档。

同key同有效内容（边、task/attempt、基线、输入、前驱和已提交actor等）重复返回原回执，不重新分配编号。后来重试调用的临时时间/当前控制版本不改变原已提交内容；同key不同有效内容必须冲突。旧actor即使知道新task的seq也无权提交；任意已有回执不能授权新的业务动作。

## 竞争、部分写与恢复

取消先于提交的可信顺序使下一条边无效；提交已完成而取消随后到达，则保留该合法边并停止于新phase。无法证明顺序时blocked，不用Agent时间戳猜合法性。若序号4已合法提交，迟到取消只记录，不重开archive。

完整回执而快照旧：RECOVERY-01重建快照，不重放业务。截断回执不算完成边，不覆盖原异常；先隔离partial文件并核查是否有外部提交事实，再由合法写入者在同固定序号记录有来源的修复回执/异常链。缺前驱、分叉或未知写者阻断，不能自动挑最新。

记录链不是跨文件原子事务或exactly-once。没有阶段回执不代表业务未执行；非幂等结果未知先查目标operation状态，不能据sequence重新调用。

## 摘要链完整性与正常终态

除首条`previous_receipt_digest=null`外，前驱、基线、输入清单均须有可解析固定对象与实际摘要，提交前重读核验。`inputs_digest`绑定显式输入清单文件，不能在自己的字节中计算自哈希；gate-check在转换前固定，其摘要由本回执记录。

正常完成以[archive-receipt](../../templates/archive-receipt.md)独立绑定合法第四边、delivery、身份、记录写权交回和实际资源结清。该回执由取得写权的宿主记录，不倒写进先前delivery；异常终止仍使用termination，不补四条正常边。哈希与结构核验不能认证宿主事件或把历史缺回执变成合法结束。


<a id="transition-chain-binding"></a>
## TRANSITION-01 · 链级核验而非独立四个快照

每条固定回执与同一原基线、实际输入清单和合法前驱绑定；四边身份不漂移，sequence 与合法 from/to/gate_id 一致。第1/3边分别使用 Plan/Check 对应对象、kind、phase、request、response 和唯一消费决策，不跨阶段复用。run、Check package、delivery、终态中的实际 artifact 与输入版本连续匹配。合法拒绝结论可完成 PDCA；不能据此声称被审对象合格。

控制/资源资格需在真实提交边界重新检查：取消先于提交应阻断；已合法第四边之后取消不能复活旧任务。纯事件模型只验证这种顺序关系，不证明真实并发或强排他。
