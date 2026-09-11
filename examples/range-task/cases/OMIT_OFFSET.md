---
schema: pdca.test-case/v3
example_only: true
execution_status: NOT_RUN
case_id: RANGE-OMIT-OFFSET
revision: '2'
node_id: B1
scene: ontology_projection
suite_ref: ../suite.md
constraint_ids:
- C_TYPE
- C_PRIORITY
- C_PURE
ac_ids:
- AC-C_TYPE
- AC-C_PRIORITY
- AC-C_PURE
category: missing_field
required: true
preconditions:
  contract: ../node.md
  environment: isolated_range_checker
  initial_state: A5 repeated 16 octets in a separate sentinel; no external resources
  observation_binding: ../observation-binding.md
inputs:
  N: 16
  length: 1
action: 不做补值/类型规范化，将inputs原样作为映射传入已绑定check_request(request)一次；按OBS-RANGE-v2捕获返回、异常和事件。
expected:
  return:
    allow: false
    code: E_TYPE
  state: sentinel byte-identical; complete trace has no target external read/write, mutation or allocation proportional
    to N
  exception: none
forbidden:
- wrong result or extra return fields
- uncaught exception
- implicit conversion or missing-field default
- sentinel mutation including write-then-restore
- target external read/write
- storage allocation proportional to N
oracle:
  source: ../node.md#合同
  method: 返回对象精确等于expected.return且无异常；依OBS-RANGE-v2检查完整观测覆盖和事件历史、前后状态、分配轨迹。缺观测为error/blocked，不是pass；expected不得从实现生成。
  priority: C_TYPE then C_DOMAIN then C_RANGE
observation:
- actual return and exception
- before/after sentinel and ordered mutation history
- target-window external read/write trace
- allocation events and resource-baseline classification
- observer positive/negative controls and completeness
- build/environment/implementation/case versions
failure_signature: 期望E_TYPE；allow/code不符是行为fail；构建/测试器/观测失败是error而非正确拒绝。
cleanup: 先固定run和原始观测，再销毁隔离对象；任何未明外部副作用保持blocked，不重复调用。
kills:
- DEFAULT_MISSING_OFFSET
regression_issue: T-02
purpose: 区分真正省略字段offset与显式null，禁止隐式默认值。
rationale: 原36案例全部含三个键，本例必须保留缺键形状，不能通过调用参数展开后自动补值。
reproducibility:
  seed: none; deterministic fixture
  sequence: one isolated call; reset before each case
  observer_ref: ../observation-binding.md
protocol_revision: 3.1.0
---

# RANGE-OMIT-OFFSET：省略字段offset

inputs中确实不含`offset`键；不是`offset: null`。预期返回`{allow:false,code:E_TYPE}`，无未捕获异常和禁止副作用。测试器不得自行补齐映射。

先验证三个字段齐全的P01可被接受，再验证此例被规定拒绝。缺offset自动补0的绑定层对OMIT_OFFSET必须失败；不允许用内部函数“少实参抛异常”代替这个公开接口测试。

返工：保留旧适配器返回和请求字节；先在旧缺陷适配器复现，再修正确认字段存在的顺序；对最终新实现执行全部39例及必需负控制。真实业务执行仍NOT_RUN。
