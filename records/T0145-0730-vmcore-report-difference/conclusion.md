---
schema: pdca.asset/v1
id: T0145-0730-vmcore-report-difference
phase: check
source_ids:
  - report-difference-audit
  - report-a-process-ledger
  - report-review
  - convergence-map
---

## 上下文

本任务审计两份针对同一 shqddb2 内核 panic 的报告：

```text
/home/black/Downloads/vmcore_analysis_report.md
/home/black/Downloads/shqddb2内核崩溃根因分析报告v2.md
```

同时检查：

- 报告 A 的原始分析会话；
- 报告 A 原始生成文件与 Downloads 派生副本；
- T0144 两轮独立 crash transcript、模块 DWARF、源码映射和逻辑闭合审查；
- 目标 3.10.0-1160.83.1.el7 源码；
- Linux 上游补丁及 Red Hat 公开勘误/CVE 跟踪。

## 假设与结果

| 假设 | 结果 | 证据结论 |
|---|---|---|
| 两份报告只是写作详略不同 | 否定 | fault 对象、字段、分支、释放对象、设备路径和补丁均实质冲突 |
| 报告 A 成功运行过匹配 vmlinux 的 crash | 否定 | 原始会话显示 debuginfo 未安装，所有 crash 启动尝试失败 |
| 报告 A 的 RDI=tio、+8=tio->md | 否定 | T0144 反汇编 + DWARF 证明 R13=tio、RDI=tio->ti、+8=ti->type |
| 报告 A 的 clone=NULL、非 blk-mq | 否定 | crash 对象显示 clone 非 NULL，mapped device 使用 request-based blk-mq |
| 报告 A 的 request payload/tio UAF 生命周期成立 | 否定 | 目标源码在 `rq_completed()` 后才 `free_old_rq_tio()`，且现场未走该分支 |
| 报告 B 的 old dm_target completion UAF 成立 | 高置信成立 | 指令、DWARF、PTE、target 几何、table 生命周期和两轮复跑闭合 |
| 缺失 suspend guard 是代码级根因 | 高置信成立 | `dm_mq_queue_rq()` 缺少 flag 检查，上游 b4459b11e840 修复同一安全不变量 |
| iSCSI 是 faulting I/O 的直接路径 | 否定 | faulting clone 是 nvme38n1，dm-19 两条 path 均为 NVMe |
| iSCSI 间接促成 dm-19 reload | 未证实 | 缺少 iSCSI→multipathd→dm-19 ioctl/map 对象链 |
| 3.10.0-1160.88.1/119.1 已包含目标修复 | 未证实 | 报告未核验 SRPM；Red Hat 公开 RHSA/CVE 跟踪不支持确定断言 |

## 分析

### 为什么差异如此之大

差异源于证据等级和第一处分支判断，而非单纯观点不同。

报告 A 没有可用 debuginfo/正确源码，也没有成功启动 crash。它从 dmesg 中
取得真实的 panic、寄存器和日志文本后，搜索到同函数的另一个 UAF 提交
`61febef40bfe`，再反向把现场解释成：

```text
RDI=tio → +8=tio->md → clone=NULL → 非 MQ request payload UAF
→ iSCSI 全路径故障 → 61feb 修复
```

其中最早的寄存器变量映射没有反汇编或 DWARF 支持。该错误随后级联改变了
对象类型、释放路径、queue 模式、直接设备和补丁选择。

报告 B/T0144 从机器指令出发：

```text
R13+8 → RDI
RDI+8 → fault
```

模块 DWARF 证明 `dm_rq_target_io.ti` 位于 +8，运行时结构体证明 clone 非空。
因此实际表达式为：

```text
tio->ti->type
```

faulting `tio->ti` 不属于当前 table，却与 dm table 首 target 的
`vmalloc-base+0x40` 几何一致；当前同一 md 已有新 target，旧地址 PTE=0。
目标源码又连接：

```text
保存 md->immutable_target 到 tio->ti
→ suspend/reload 更换 table
→ destroy old table / vfree
→ completion 再次解引用 tio->ti
```

`dm_mq_queue_rq()` 缺少 `DMF_BLOCK_IO_FOR_SUSPEND` 检查，解释了 request
为什么可能越过 suspend 隔离。上游 b4459b11e840 在所有危险操作之前增加该
guard，与本次被破坏的安全不变量同源。

### 当前最可信根因

> 本次 panic 的直接原因是 `dm_softirq_done()` 完成路径解引用已失效的
> `tio->ti->type`。该 `tio->ti` 高置信属于 dm-19 的旧 table target，并在
> table swap 后随旧 table 销毁而解除映射。目标内核 request-based DM blk-mq
> 的 `dm_mq_queue_rq()` 缺少 suspend flag guard，使请求在 queue 隔离被外部
> 打破时可能保存旧 target 并跨越 table destroy。faulting clone 的直接路径
> 是 NVMe，不是 iSCSI。

### 两份报告总体判定

| 报告 | 判定 |
|---|---|
| 报告 A | 核心根因被反证；仅 panic/日志原始事实可复用，整体不应作为最终 RCA |
| 报告 B | 核心技术根因高可信；具体外部触发者、iSCSI 间接链和发行版修复版本仍需保留边界 |

报告 B 也有需要修订之处：

1. `PTE=0` 不能单独唯一证明 `vfree`；应表述为页表、对象几何和源码生命周期的
   组合高置信结论。
2. 具体执行外部 unquiesce 的动作没有从静态 vmcore 恢复。
3. 3.10 回移植的 API 应使用语义等价的 `BLK_MQ_RQ_QUEUE_BUSY`，且需运行验证。
4. 不应断言 119.1 已包含修复、升级后确定不会复发。

## 适用边界

- 已确认的是此次 request-based device-mapper blk-mq completion UAF，不泛化
  到所有 dm、NVMe 或 iSCSI 故障。
- old target 身份和 vfree 生命周期为多证据支持的高置信结论，不是历史
  destroy 调用栈的直接快照。
- 具体外部 unquiesce 来源无法由静态 vmcore 唯一恢复。
- iSCSI 直接路径已排除，间接触发保持 inconclusive。
- 上游 guard 的静态同源性已证明，但目标 3.10 回移植未构建、未 A/B 压测。
- RHEL z-stream 是否已回移植必须以实际 SRPM/反汇编或发行商支持答复为准。

## 下一轮建议

1. 将报告 A 标记为“早期假设稿，核心结论已被后续取证推翻”。
2. 修订报告 B 的 PTE/vfree 措辞和修复版本承诺。
3. 检查计划升级内核的实际 `dm_mq_queue_rq()`，确认存在语义等价 suspend guard。
4. 若继续查 iSCSI 间接关系，收集 multipathd debug、udev 和 DM ioctl 审计。
5. 如采用自维护回移植，在非生产环境执行 fio + dm reload/suspend/resume +
   `nr_requests`/queue 事件的补丁前后 A/B 压测。

## Check 建议判定

建议 verdict：

```text
confirmed
```

理由：PRD AC-1 至 AC-10 均有已登记证据覆盖，convergence validator 为
`valid: true`；差异成因、逐项判定、最可信根因和残余边界均已明确。发行版
修复版本未确认是报告审计发现的边界，不影响本任务“解释差异并裁定报告可信度”
的完成。
