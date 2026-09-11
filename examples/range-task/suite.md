---
schema: pdca.test-suite/v3
example_only: true
execution_status: NOT_RUN
suite_id: RANGE-v2
revision: '2'
node_id: B1
scene: ontology_projection
contract_ref: node.md
case_refs:
- cases/P01.md
- cases/P02.md
- cases/P03.md
- cases/P04.md
- cases/P05.md
- cases/P06.md
- cases/P07.md
- cases/P08.md
- cases/P09.md
- cases/N01.md
- cases/N02.md
- cases/N03.md
- cases/N04.md
- cases/N05.md
- cases/N06.md
- cases/N07.md
- cases/D01.md
- cases/D02.md
- cases/D03.md
- cases/D04.md
- cases/D05.md
- cases/D06.md
- cases/D07.md
- cases/D08.md
- cases/D09.md
- cases/T01.md
- cases/T02.md
- cases/T03.md
- cases/T04.md
- cases/T05.md
- cases/T06.md
- cases/T07.md
- cases/T08.md
- cases/T09.md
- cases/T10.md
- cases/T11.md
- cases/OMIT_N.md
- cases/OMIT_OFFSET.md
- cases/OMIT_LENGTH.md
required_cases:
- RANGE-P01
- RANGE-P02
- RANGE-P03
- RANGE-P04
- RANGE-P05
- RANGE-P06
- RANGE-P07
- RANGE-P08
- RANGE-P09
- RANGE-N01
- RANGE-N02
- RANGE-N03
- RANGE-N04
- RANGE-N05
- RANGE-N06
- RANGE-N07
- RANGE-D01
- RANGE-D02
- RANGE-D03
- RANGE-D04
- RANGE-D05
- RANGE-D06
- RANGE-D07
- RANGE-D08
- RANGE-D09
- RANGE-T01
- RANGE-T02
- RANGE-T03
- RANGE-T04
- RANGE-T05
- RANGE-T06
- RANGE-T07
- RANGE-T08
- RANGE-T09
- RANGE-T10
- RANGE-T11
- RANGE-OMIT-N
- RANGE-OMIT-OFFSET
- RANGE-OMIT-LENGTH
mutation_refs:
- mutations.md
coverage:
- constraint_id: C_TYPE
  positive_cases:
  - RANGE-P01
  - RANGE-P02
  - RANGE-P03
  negative_cases:
  - RANGE-T01
  - RANGE-T02
  - RANGE-T03
  - RANGE-T04
  - RANGE-T05
  - RANGE-T06
  - RANGE-T07
  - RANGE-T08
  - RANGE-T09
  - RANGE-T10
  - RANGE-T11
  - RANGE-OMIT-N
  - RANGE-OMIT-OFFSET
  - RANGE-OMIT-LENGTH
- constraint_id: C_DOMAIN
  positive_cases:
  - RANGE-P01
  - RANGE-P06
  - RANGE-P07
  - RANGE-P08
  negative_cases:
  - RANGE-D01
  - RANGE-D02
  - RANGE-D03
  - RANGE-D04
  - RANGE-D05
  - RANGE-D06
  - RANGE-D07
  - RANGE-D08
  - RANGE-D09
- constraint_id: C_RANGE
  positive_cases:
  - RANGE-P01
  - RANGE-P02
  - RANGE-P03
  - RANGE-P04
  - RANGE-P05
  - RANGE-P06
  - RANGE-P07
  - RANGE-P08
  - RANGE-P09
  negative_cases:
  - RANGE-N01
  - RANGE-N02
  - RANGE-N03
  - RANGE-N04
  - RANGE-N05
  - RANGE-N06
  - RANGE-N07
- constraint_id: C_PRIORITY
  positive_cases:
  - RANGE-P01
  - RANGE-P02
  - RANGE-P03
  negative_cases:
  - RANGE-D07
  - RANGE-D08
  - RANGE-T04
  - RANGE-T09
  - RANGE-OMIT-N
  - RANGE-OMIT-OFFSET
  - RANGE-OMIT-LENGTH
- constraint_id: C_PURE
  positive_cases:
  - RANGE-P01
  - RANGE-P02
  - RANGE-P03
  - RANGE-P04
  - RANGE-P05
  - RANGE-P06
  - RANGE-P07
  - RANGE-P08
  - RANGE-P09
  negative_cases:
  - RANGE-N01
  - RANGE-N02
  - RANGE-N03
  - RANGE-N04
  - RANGE-N05
  - RANGE-N06
  - RANGE-N07
  - RANGE-D01
  - RANGE-D02
  - RANGE-D03
  - RANGE-D04
  - RANGE-D05
  - RANGE-D06
  - RANGE-D07
  - RANGE-D08
  - RANGE-D09
  - RANGE-T01
  - RANGE-T02
  - RANGE-T03
  - RANGE-T04
  - RANGE-T05
  - RANGE-T06
  - RANGE-T07
  - RANGE-T08
  - RANGE-T09
  - RANGE-T10
  - RANGE-T11
  - RANGE-OMIT-N
  - RANGE-OMIT-OFFSET
  - RANGE-OMIT-LENGTH
repair_budget:
  max_do_repair_iterations: 2
  max_same_signature_repeats: 2
  mandatory_regression: all 39 cases on final artifact; all 13 required mutation controls; current-node scope only
  on_exhaustion: finish honest failure Check/Act; new attempt/new agent
acceptance_scope: node_scene_artifact
observation_binding_ref: observation-binding.md
protocol_revision: 3.1.0
---

# 范围校验任务套件

39条必需案例的期望在各自文件中固定。正例的合法类型与错误优先级不触发分支，但仍验证不会误拒绝；所有正例也支持C_TYPE/C_PRIORITY允许路径（覆盖矩阵在下文明确）。每次run必须核对完整39例，不能只跑最近失败例。

## 额外覆盖说明

C_TYPE合法路径由P01/P02/P03代表；C_PRIORITY合法路径P01，以及D07/D08、T04/T09的复合错误优先级；C_PURE全部案例都有无副作用断言，并由mutations.md中SIDE_EFFECT、READ_IO、ALLOC_N、WRITE_THEN_RESTORE负控制验证观测器。节点组合/并发不适用于纯数值函数，B与R的组合另有任务测试，不宣称此suite验证持久化/并发安全。

## 固定公共环境

公开被测绑定为check_request(request)，inputs映射原样提交、不补缺失字段也不预先规范化；内部check(N,offset,length)仅是实现分层，不以语言调用异常代替公共返回合同；输出仅有allow和code。哨兵初始为16字节A5，允许执行的数学结果不读写哨兵。测试器按[观测绑定](observation-binding.md)观察目标窗口内的外部读写、动态分配、状态变更及恢复事件；纯参考模型的返回值核对不能证明业务代码没有I/O。

测试环境使用已知正确控制实现及已知错误变体，先确认oracle区分力，再测目标实现；所有大整数仅作值，不分配N大小存储。具体业务语言入口在真实任务Plan固定，此教学套件不谎称存在实际库API。

## 通过和停止

所有39例对同一artifact实际pass、无未解释error/flaky，mutation的要求满足，才可提出局部交付。示例预算是本教学任务值，不是所有任务的默认数值；真实任务必须明确确认自己的有限预算。

本文件及case中的NOT_RUN表示没有真实节点Agent执行。交付验证可能对独立参考模型求值，结果另见migration/VALIDATION.md，不覆盖这里的教学状态。


当前教学定义使用tree-2/node_revision=2；新增缺字段合同、案例正文与oracle变更不回写旧tree-1/RANGE-v1的证据。只有节点本地必需测试属于本套件，B/R的未来回归不阻塞B1完整PDCA和局部交付；工作issue和发布继续等待它们。
