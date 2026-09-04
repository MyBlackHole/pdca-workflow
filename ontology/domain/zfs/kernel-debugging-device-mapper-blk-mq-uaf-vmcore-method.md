---
schema: pdca.asset/v1
id: ontology:domain/kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method/1.0.0
summary: Device-mapper blk-mq UAF 的 vmcore—源码闭环方法
domain:
- ontology:domain/kernel-debugging
relations:
  specializes:
  - ontology:domain/kernel-debugging
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 kernel-debugging-device-mapper-blk-mq-uaf-vmmethod 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


---
schema: pdca.asset/v1
id: knowledge:kernel-debugging/device-mapper-blk-mq-uaf-vmcore-method
layer: knowledge
summary: 用 vmcore、DWARF 和源码生命周期闭合证明 device-mapper blk-mq 完成路径 UAF 的方法
tags: [linux-kernel, vmcore, crash, device-mapper, blk-mq, use-after-free]
scenarios: [research, debugging]
phases: [do, check, act]
applies_when:
  - request-based device-mapper blk-mq 路径在 I/O 完成或 suspend/reload 并发附近崩溃
  - 需要把 crash 现场逐层对应到指定版本源码
excludes_when:
  - 仅凭调用栈或日志时间相邻就要求认定根因
  - bio-based dm 路径或其他子系统尚未证明具有相同对象生命周期
source_ids:
  - records/T0144-0729-vmcore-source-revalidation/conclusion.md
confidence: high
status: active
---

# Device-mapper blk-mq UAF 的 vmcore—源码闭环方法

## 1. 适用边界

本方法用于分析 request-based device-mapper blk-mq 路径中，与
suspend/reload、旧 table 销毁和异步完成并发有关的悬空指针问题。

它不意味着所有 dm、NVMe 或 iSCSI 故障都属于同一 bug。是否同源必须重新证明：

1. 故障发生在相同的数据结构字段或等价访问上。
2. 请求持有的 target 确实来自已经退出当前映射的旧 table。
3. 旧对象已经进入释放路径。
4. 新请求能够越过 suspend 隔离边界。

## 2. 证据闭环顺序

### 2.1 从机器指令确定真正的非法访问

不要只看符号名或 C 源码行。应同时取得：

- RIP 附近反汇编；
- 通用寄存器；
- fault virtual address；
- DWARF 结构字段偏移；
- 对应 C 表达式。

先根据指令计算有效地址，再用 DWARF 验证该地址属于哪个结构字段。这样可以区分：

- 结构体本身为空；
- 结构体有效但成员为空；
- 结构体地址已经释放；
- 调试行号只落在附近语句。

### 2.2 用页表状态区分 NULL 与已释放地址

对可疑指针同时执行：

- 直接内存读取；
- `vtop` 或等价页表遍历；
- 必要时查看相邻地址和分配几何。

非零地址且页表不存在，结合其过去所属的 vmalloc/vfree 区域，可以支持
“对象曾经存在、现已解除映射”的判断。单独的读取失败不能证明 UAF，还必须补齐对象身份和释放路径。

### 2.3 区分三种设备身份

dm/multipath 分析至少要分开记录：

1. 崩溃请求保存的历史 target 和 clone；
2. vmcore 时刻 mapped device 的当前 table；
3. 故障 I/O 实际完成所经过的底层设备。

`dm-19` 的当前 table 只能说明转储时刻的映射，不能单独恢复请求提交时的旧 table。
实际完成设备应从 request/clone 的对象链反查，不能由当前 multipath 路径列表替代。

### 2.4 证明对象属于旧 table

推荐组合以下证据：

- 请求上下文中保存的 `dm_target *`；
- 当前 mapped device/table/target 的地址；
- target 数组的分配起点、元素大小和地址范围；
- reload/swap 前后 table 地址差异；
- 可疑 target 不属于当前 table、却符合旧 target 分配几何。

“不属于当前 table”只排除当前对象；要认定旧 table，还需和 table 交换、销毁路径相连。

### 2.5 闭合释放生命周期

沿指定内核版本源码确认：

1. 请求在何处保存 target 引用；
2. table 在何处从 mapped device 中交换；
3. suspend 如何停止新 I/O 并等待旧 I/O；
4. 旧 table/target 最终在何处释放；
5. 异步完成回调在何处再次解引用保存的 target。

只有“保存旧引用 → 旧对象释放 → 完成路径再次解引用”三段均有证据，才能把 page fault 提升为 completion-path UAF。

## 3. 并发保护为什么必须位于 queue_rq 开头

对 request-based dm blk-mq，suspend 协议依赖两个动作：

1. 阻止新的请求取得 live table/target 并向下派发；
2. 等待已经在途的请求排空，然后才能释放旧 table。

因此 `DMF_BLOCK_IO_FOR_SUSPEND` 检查必须发生在所有危险操作之前，包括：

- 启动 request；
- 取得 live table；
- 保存 target；
- 创建 clone；
- 向底层设备派发。

若置位时立即返回可重试状态，blk-mq 会保留并在恢复后重新调度请求。此时请求尚未取得旧
table 的 target，suspend 等待的在途集合不会被新的派发重新扩张。等既有 I/O 排空后释放旧
table，恢复阶段的新请求再取得新 table，从而切断悬空引用的产生路径。

仅在完成路径增加 NULL 检查不能修复此问题：已释放地址通常非 NULL，而且在完成阶段才检查
无法恢复已被破坏的生命周期协议。

## 4. 判断上游补丁是否与现场 bug 同源

补丁相似不等于已经证明有效。应依次验证：

1. 子系统、I/O 模式和入口函数相同；
2. 补丁描述的并发窗口与 vmcore 恢复出的生命周期一致；
3. 补丁检查的状态位正是 suspend 协议使用的隔离状态；
4. guard 位于所有 target 获取和派发动作之前；
5. 返回语义会重试请求，而不是丢失或错误完成；
6. 回移植后结构字段、锁和返回码语义仍与目标内核一致。

静态检查可以证明故障路径被切断，但不能替代运行验证。目标版本仍需完成构建、启动、
suspend/reload 并发压测以及修复前后的 A/B 对比。

## 5. 外部触发因素的证明门槛

iSCSI、multipath 抖动或管理面 reload 与崩溃时间接近，只能列为候选背景。认定触发需要完整链：

1. 明确外部事件；
2. 证明事件作用到故障 mapped device；
3. 证明它导致 suspend/reload 或等价状态变化；
4. 证明请求在该窗口越过隔离边界；
5. 证明该请求最终进入 faulting completion。

任一中间环节缺失，都应标为 `inconclusive`，不能把时间相关性升级为直接因果。

## 6. 推荐执行记录格式

每条 crash 命令都记录：

- 目的：要验证哪个假设；
- 命令：可重复执行的原始输入；
- 输出：未经改写的关键结果；
- 解释：结果支持或排除什么；
- 边界：它不能证明什么；
- 下一步：为何继续执行下一条命令。

关键结论至少做一次新的独立 crash 会话复跑，并比较 RIP、寄存器、字段偏移、页表状态、旧新
target 身份和实际底层设备。两次会话一致可证明分析可重复，但仍不等于修复已通过运行验证。

## 7. 结论分层

最终报告应明确区分：

- 已证实事实：由 vmcore、DWARF 或源码直接支撑；
- 高置信推断：多条独立证据唯一指向，但缺少直接事件记录；
- 开放分支：外部触发者、间接 iSCSI 关系、回移植运行效果等尚未闭合部分。

这种分层可以让根因成立，同时避免对证据边界之外的事件作过度声明。
