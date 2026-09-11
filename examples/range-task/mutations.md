---
schema: pdca.mutation-suite/v3
example_only: true
execution_status: NOT_RUN
suite_ref: suite.md
mutants:
- mutant_id: STRICT_END
  change: 把length≤N−offset改为严格<，错误拒绝恰好到末尾
  expected_kill_case: RANGE-P03
  constraint_id: C_RANGE
  result: null
- mutant_id: MISSING_LOWER
  change: 跳过offset≥0检查，负起点用和判断可能被接受
  expected_kill_case: RANGE-D01
  constraint_id: C_DOMAIN
  result: null
- mutant_id: ZERO_LENGTH
  change: 允许length=0；非法空写入被采纳
  expected_kill_case: RANGE-D02
  constraint_id: C_DOMAIN
  result: null
- mutant_id: WRAP_ADD
  change: 以u64回绕的offset+length≤N代替合法范围条件
  expected_kill_case: RANGE-N06
  constraint_id: C_RANGE
  result: null
- mutant_id: COERCE_TYPES
  change: 把字符串或bool转整数后校验
  expected_kill_case: RANGE-T01
  constraint_id: C_TYPE
  result: null
- mutant_id: WRONG_PRIORITY
  change: 先检查N数值域，再检查其他参数类型
  expected_kill_case: RANGE-T09
  constraint_id: C_PRIORITY
  result: null
- mutant_id: ALWAYS_ALLOW
  change: 对所有输入返回OK，验证测试器不是只看输出存在
  expected_kill_case: RANGE-N03
  constraint_id: C_RANGE
  result: null
- mutant_id: ALWAYS_DENY
  change: 对所有输入返回E_BOUNDS，防止全拒绝也混成安全
  expected_kill_case: RANGE-P01
  constraint_id: C_RANGE
  result: null
- mutant_id: SIDE_EFFECT
  change: 返回完全正确，但修改哨兵/产生禁止写入
  expected_kill_case: RANGE-P01
  constraint_id: C_PURE
  result: null
- mutant_id: DEFAULT_MISSING_OFFSET
  change: 缺offset时静默补0再调用正确检查器
  expected_kill_case: RANGE-OMIT-OFFSET
  constraint_id: C_TYPE
  result: null
- mutant_id: READ_IO
  change: 返回正确但在被测窗口读取隔离临时文件；sentinel不变
  expected_kill_case: RANGE-P01
  constraint_id: C_PURE
  result: null
- mutant_id: ALLOC_N
  change: 返回正确但在隔离控制中按N申请存储；只用N=16，不用U64真的分配
  expected_kill_case: RANGE-P01
  constraint_id: C_PURE
  result: null
- mutant_id: WRITE_THEN_RESTORE
  change: 改写sentinel后恢复原字节，最终值相同但事件历史非空
  expected_kill_case: RANGE-P01
  constraint_id: C_PURE
  result: null
revision: '2'
observation_binding_ref: observation-binding.md
protocol_revision: 3.1.0
---

# 故意错误实现：检验测试是否能识别错误

每个变体只在隔离副本运行；原正确实现和固定expected不改。逐个保存mutant改动、有效构建、调用结果、失败断言及原始证据。

killed要求已执行且指定行为断言失败。编译失败、测试器异常、失去观测或超时且无判定依据都是invalid/error，不能写killed。survived必须修补测试盲区，再跑正确控制样本；不能直接把错误变体认定无关。

SIDE_EFFECT必须通过状态/事件观测识别；只比较返回allow/code的测试器会让它存活。这是本套件特意要求的检测器反例，不得省略。

变体运行中的fail是预期的“发现错误”，与正确实现必须全pass分开统计。实际状态均NOT_RUN；参考模型检查结果不替代真实业务实现测试。


## 四个新增负控制与返工

DEFAULT_MISSING_OFFSET：用真正缺键的OMIT_OFFSET运行；错误适配器会返回OK，正确实现返回E_TYPE。不得改用null输入充数。

READ_IO：建立只有测试夹具可访问的临时文件，已知错误实现读取后仍返回正确对象。要求读事件被识别；清理属于测试器窗口，不混入目标行为。无读监测时控制无效而非killed。

ALLOC_N：只在N=16等安全小容量控制中实际记录目标按N申请的事件，验证检测器；另以代码/分配调用路径和多个N验证规则不是简单“总内存大于阈值”。禁止真的执行U64容量分配，禁止OOM作为成功检测。原39例的大整数仅走正常检查函数。

WRITE_THEN_RESTORE：事件必须包含写入和恢复两次，最终sentinel仍等于初始值；仅做末态比较的错误oracle会survive，应被观测器验收反例发现。

四个控制都须分别跑正确控制（不误报）和错误控制（检出）。修补oracle后重新固定版本并重跑原9个控制及39例；模型局部观测结果不能替代真实语言的工具绑定。
