---
schema: pdca.work-node/v3
example_only: true
state: example
work_id: EXAMPLE-BOUNDED-WRITE
tree_revision: tree-2
node_id: B1
node_revision: '2'
parent_node_id: B
children: []
definition_refs: []
test_suites:
  ontology_modeling: ../seven-node-work/scene-tests.md#建模样本
  ontology_projection: suite.md
  ontology_conformance_verification: ../seven-node-work/scene-tests.md#审查样本
protocol_revision: 3.1.0
---

# B1：范围校验实体

## 合同

目标：在不产生副作用的前提下，判断一个非空写区间是否完整位于给定容量中；不执行写入，不分配容量大小内存，不负责持久化、加密或并发。

公开被测边界为 check_request(request)，request是结构化映射，必须显式包含N、offset、length三个字段；字段省略或显式null均返回E_TYPE，但分别测试，不默认补值。合法形状后调用内部check(N,offset,length)。直接函数少实参的语言异常不属于公开合同，不能据此假称适配器已验证。

输入N、offset、length按数学整数解释，但类型必须是严格整数，布尔、小数、字符串、null、容器都不是允许整数。最大值U=18446744073709551615。

| 约束 | 规则/错误优先级 |
|---|---|
| C_TYPE | 首先检查三个必需字段存在，再检查三个参数全部严格整数，否则返回 `{allow:false,code:E_TYPE}`；不抛出未捕获异常、不隐式转换 |
| C_DOMAIN | 类型通过后要求1≤N≤U，0≤offset≤U，1≤length≤U；否则E_DOMAIN |
| C_RANGE | 域合法后要求offset≤N且length≤N−offset；否则E_BOUNDS；满足时返回 `{allow:true,code:OK}`。等于末尾合法；非空区间不允许offset=N |
| C_PRIORITY | 类型→数值域→区间，按以上顺序决定；不能因先做算术导致异常或不同错误类别 |
| C_PURE | 成败均不修改状态、不进行外部I/O、不分配N大小的存储，不返回多余对象字段 |

每约束为必须AC，同名AC-C_*。多种错误并存按既定优先级处理。实现可不同，但不能改变允许行为或返回协议；通过`offset+length`直接判断时必须证明不会溢出，示例安全条件用减法与前置判断。

## 交付

具名范围校验实现、固定版本、39例实际运行、错误变体区分结果、无副作用验证及限制。代码本身由真实任务在授权目标项目生成；本文不是已实施代码。

## 父节点接口

父B向B1提交完整结构化请求，只有得到OK才调用B2；B1拒绝必须阻止B2写入。这项跨节点属性由B的独立完整PDCA与组合测试验证，不能由本节点局部PASS推断。


## 观测与适用边界

C_PURE必须按[观测绑定](observation-binding.md)逐项观测；没有外部读写/分配事件并不由最终sentinel相同推出。未知观测阻断完整通过。实现可以使用不随N增长的必要常量级局部资源；禁止按容量N申请存储。具体资源基线、允许的测试器开销和采集覆盖须在真实任务Plan确定，不能把教学监测器当成任意语言代码的沙箱。
