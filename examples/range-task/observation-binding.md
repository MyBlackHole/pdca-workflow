---
schema: pdca.observation-binding/v1
binding_id: OBS-RANGE-v2
protocol_revision: 3.1.0
example_only: true
execution_status: NOT_RUN
suite_ref: suite.md
required_claims: [no_external_read, no_external_write, no_state_mutation, no_allocation_proportional_to_N]
required_controls: [SIDE_EFFECT, READ_IO, ALLOC_N, WRITE_THEN_RESTORE]
---

# C_PURE 的可观测性合同

## 作用域

被测对象为固定构建的check_request(request)及其实际调用的内部实现。窗口从调用入口到同步/异步完成；后台线程/子进程若属于目标，也必须纳入，否则覆盖unknown。允许测试器在窗口外读夹具、写日志、分配固定夹具；不能借“测试器开销”隐藏目标动作。

| 必需事实 | 必须固定的观测与断言 | 正/负控制 | 不足时 |
|---|---|---|---|
| 无外部读取 | 语言调用/I/O系统调用或受控依赖代理事件，实际工具身份及目标归属；窗口内目标读事件为零 | 纯控制无事件；READ_IO读隔离文件被检出 | 只有write trace则unknown |
| 无外部写入 | 文件/网络/设备及其他授权环境中相关输出的调用事件，窗口内目标写事件为零 | SIDE_EFFECT或隔离写控制被检出 | 快照相同不能证明没写 |
| 无状态修改 | 全部受保护状态的写事件与前后快照；不能只观察一个无关sentinel | WRITE_THEN_RESTORE被检出；纯控制不误报 | 覆盖不了可写对象则unknown |
| 不按N分配存储 | 分配调用的大小/调用位置/归属和资源基线；静态路径核查结合多N样本，证明没有容量相关申请 | ALLOC_N在安全N=16控制被识别；必要常量局部资源不误报 | RSS末态或OOM不是判据 |

## 真实任务Plan必填

固定语言、运行时、构建hash、实际函数入口，外部资源清单，进程/线程与异步完成边界；为每条必需事实填写工具名称/版本/调用步骤、可观察事件、盲区、负控制结果与原始证据。可组合代码审查、调用注入、系统跟踪和权限约束，必须说明各自证明什么。关键缺口不能写“隔离所以没有副作用”。

输入adapter属于被测路径：缺字段不能由测试器默认补值。原始预期不可变；观察脚本改变需新observer_revision/run，日志与断言一并保存。

## 执行和判定

1. 先准备并隔离夹具，固定观测窗口与状态基线。开启观测失败则blocked/error，不运行并假报通过。
2. 跑已知纯控制，再逐一跑四个指定坏控制，分别验证不误报与检出。只验证返回值的观测器必须被负控制判无效。
3. 对39例的最终目标构建执行完整断言。目标事件违例为fail；日志丢失、跟踪不可用、异常解析为error，事实无法确认记unknown，不可聚合为node_local_pass。
4. 先持久化事件/actual/版本，再由测试器清理；未知副作用不盲重试。清理结果单列。

## 参考验证边界

项目外的本次验证器可运行显式注入的事件代理、小额分配和临时文件读取，用于检验这些断言与负控制。它**没有**对任意业务代码实现通用系统调用/内存跟踪，也没有验证真实Agent宿主；不能把这种模型控制报告标为本模板的真实运行证据。
