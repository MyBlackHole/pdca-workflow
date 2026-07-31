# T0145 两份 shqddb2 内核崩溃报告差异审计

## 调研目标

解释以下两份报告为何对同一次 panic 得出显著不同的根因，并判断各关键结论的
证据状态：

- 报告 A：`/home/black/Downloads/vmcore_analysis_report.md`
- 报告 B：`/home/black/Downloads/shqddb2内核崩溃根因分析报告v2.md`

判定标签：

- `supported`：证据足以支持；
- `refuted`：被更直接证据反驳；
- `inconclusive`：存在可能性，但证据不足。

## 结论先行

差异大的首要原因不是“两位分析者对同一套完整证据看法不同”，而是两份报告
实际使用了不同等级的证据：

- 报告 A 没有成功加载匹配 vmlinux/debuginfo，也没有成功进入 crash。它以
  dmesg/messages、寄存器文本、互联网中的相似 UAF 补丁和模型推理生成结论。
- 报告 B 的核心材料来自 T0144：两轮独立 crash、模块 DWARF、反汇编、结构体
  对象、页表、dm table、request/clone/gendisk 和正确源码的交叉验证。

因此报告 A 在最早的变量身份判断上就走错了分支：

```text
报告 A：RDI = tio；RDI+8 = tio->md；clone=NULL
报告 B：R13 = tio；RDI = tio->ti；RDI+8 = ti->type；clone!=NULL
```

一旦这里分叉，后面的“释放了什么对象、为何释放、是哪块设备、iSCSI 是否直接
相关、对应哪个补丁”都会整体分叉。

当前最可信结论是：

> CPU 137 在 `dm_softirq_done()` 内联的 `dm_done()` 路径执行
> `tio->ti->type` 解引用时，访问了已解除映射的旧 `dm_target`。高置信的
> 代码级根因是 request-based DM blk-mq 的 `dm_mq_queue_rq()` 缺少
> `DMF_BLOCK_IO_FOR_SUSPEND` 准入检查，使请求可能持有旧 target 跨越
> table swap/destroy。faulting clone 的实际底层设备为 NVMe；iSCSI 不是
> 直接 I/O 路径，其是否经 userspace/multipathd 间接促成 reload 仍未证实。

## 输入与完整性

| 输入 | SHA-256 | 角色 |
|---|---|---|
| 报告 A Downloads 副本 | `f087f00ae06379347d63462b0a4ee42f50ffb70ed52a9efeb56b6559147bc771` | 待审报告 |
| 报告 A 原始生成文件 | `7d383c55e2cf9b6b0d3c1d287930aac3f2c390d689f8db8bd5ca7ba5129eb99c` | 谱系比对 |
| 报告 A 原始会话 | `9b4a9c6c57e502b84fdf1c53563e3dc28526c686b38dd19ea9a6a3ee6925cb59` | 分析过程证据 |
| 报告 B | `c9642f9a8f6c9b49354c58704a3fc2aeff1e6c8e3580b285a4c318f3525655a0` | 待审报告 |
| T0144 crash 首轮 | `d5ff1d02fa95fbc723720d8941265eee59a3307b4434aa50942904c945050f0a` | 独立 crash transcript |
| T0144 crash 复跑 | `838b78c6e89b8046b35c9510bfc3ef17e2806a565e873d8fcdfde2c18b00dc9c` | 可重复性证据 |

报告 B 首页声明的 crash 会话 SHA-256 与 T0144 已登记的首轮 transcript 完全
相同，说明其核心 crash 输出具有可追溯来源。

## 方法

1. 审计报告 A 的完整会话，区分成功命令、失败命令、日志观察、网络类比资料和
   模型推断，见 [analysis-process-ledger.md](analysis-process-ledger.md)。
2. 对两份报告逐项建立“主张—证据—判定”矩阵。
3. 用 T0144 两轮 crash transcript、模块 DWARF 和不可变记录裁定运行时对象。
4. 用目标源码树
   [`dm-rq.c`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c)
   裁定具体控制流和对象释放顺序。
5. 对上游补丁与目标 3.10 API 做语义同源性检查。
6. 对发行商版本状态只接受发行商公开材料；包版本存在不等于包含目标回移植。

## 发现一：报告 A 没有完成 vmcore 交互分析

原始会话明确记录：

- 目标版本 kernel-debuginfo 未安装；
- 尝试错误版本 vmlinux，失败；
- 尝试目标版本 vmlinuz，文件不存在；
- 尝试自行解压，crash 报“不支持的文件格式”；
- 随后明确转为依赖 dmesg/messages。

会话没有产生 `dis`、`struct -o`、`vtop` 或 request/clone 设备遍历结果。

更重要的是，原始生成文件
[`/home/black/vmcore_analysis_report.md`](/home/black/vmcore_analysis_report.md)
末尾明确披露“未安装 kernel-debuginfo，本次基于 dmesg/messages 完成”，而
Downloads 副本删除了这条披露。两份文件并非同一字节版本。

这不表示报告 A 所有信息都无效。以下原始事实仍可保留：

- panic 位于 `dm_softirq_done+0x61`；
- CR2、RIP 和寄存器文本；
- CPU 137、softirq 调用栈；
- iSCSI/Actifio 日志事件存在。

但这些事实不足以单独决定寄存器对应哪个 C 变量、执行哪个内联分支或 faulting
request 的底层设备。

## 发现二：关键分歧矩阵

| # | 维度 | 报告 A | 报告 B / T0144 | 判定 |
|---|---|---|---|---|
| 1 | 取证基础 | 文本给出 crash 参考命令，正文写成确定结论 | 两轮 crash、哈希、DWARF、对象遍历 | A 的 crash 验证主张 `refuted`；B `supported`，高置信 |
| 2 | RDI 对象 | `RDI=tio` | `R13=tio`，`RDI=tio->ti` | A `refuted`；B `supported`，确定 |
| 3 | fault 字段 | `RDI+8=tio->md` | `RDI+8=ti->type` | A `refuted`；B `supported`，确定 |
| 4 | clone 状态 | `RBX=0 ⇒ clone=NULL` | `tio->clone=ffff9ff862cf9600`，与 R12 一致 | A `refuted`；B `supported`，确定 |
| 5 | queue 模式 | 非 blk-mq | `use_blk_mq=true`、MQ request-based | A `refuted`；B `supported`，确定 |
| 6 | 被释放对象 | request payload 中的 `tio`/SLAB | 旧 dm table 中的 `dm_target`/vmalloc | A `refuted`；B `supported`，高置信 |
| 7 | UAF 路径 | `clone==NULL → blk_end_request_all → rq_completed(tio->md)` | 保存旧 `tio->ti` → table swap/destroy → completion 解引用 | A `refuted`；B `supported`，高置信 |
| 8 | 直接底层设备 | iSCSI/Actifio 路径 | clone=`nvme38n1`；dm-19 两条 path 均为 NVMe | A `refuted`；B `supported`，确定 |
| 9 | iSCSI 角色 | 存储风暴是必要、直接诱因 | 事件存在；直接路径排除；间接链未闭合 | B 的分层判定 `supported` |
| 10 | 对应补丁 | `61febef40bfe` | `b4459b11e840` 与缺失 guard 同源 | A 补丁匹配 `refuted`；B 同源性 `supported`，高置信 |
| 11 | 外部 unquiesce | 归因于 iSCSI 全路径失败 | 必要机制成立，具体动作无法由静态 vmcore 唯一恢复 | 具体触发者 `inconclusive` |
| 12 | RHEL 修复版本 | 断言 88.1 首修、119.1 已修 | 正文一度谨慎，但整改表又断言 119.1 直接修复 | 两份报告均未证明；公开 Red Hat 跟踪与该断言不一致 |

## 发现三：fault 指令为什么只能支持报告 B

T0144 反汇编：

```text
dm_softirq_done+81:  mov 0x8(%r13),%rdi
dm_softirq_done+92:  test %rdi,%rdi
dm_softirq_done+97:  mov 0x8(%rdi),%rdx   ← fault
```

模块 DWARF：

```text
struct dm_rq_target_io {
    [0]  struct mapped_device *md;
    [8]  struct dm_target *ti;
    [16] struct request *orig;
    [24] struct request *clone;
}
```

现场对象：

```text
R13 = ffff9ff42a3f1a40 = tio
*(R13+8) = tio->ti = ffffbd16abacc040 = RDI
*(RDI+8) = ti->type → CR2 ffffbd16abacc048
tio->clone = ffff9ff862cf9600 = R12
```

所以 `RDI` 不是 `tio`，`RBX=0` 也不能被直接命名为 `clone`。报告 A 是在没有
反汇编变量追踪的情况下，把 fault 时寄存器按想象中的源码变量命名。

原始报告 A 在
[`vmcore_analysis_report.md:56`](/home/black/Downloads/vmcore_analysis_report.md:56)
至第 59 行作出上述错误映射；报告 B 在
[`shqddb2内核崩溃根因分析报告v2.md:247`](</home/black/Downloads/shqddb2内核崩溃根因分析报告v2.md:247>)
以后给出反汇编、DWARF 和寄存器闭环。

## 发现四：报告 A 的 clone-null 生命周期被目标源码直接反驳

报告 A 使用的伪代码声称：

```text
blk_end_request_all(rq, ...)
→ request 连同 tio 立即释放
→ rq_completed(tio->md, ...) 再访问 tio
```

但目标 RHEL 3.10 源码实际为：

```c
if (!rq->q->mq_ops) {
        blk_end_request_all(rq, tio->error);
        rq_completed(tio->md, rw, false);
        free_old_rq_tio(tio);
}
```

见
[`dm-rq.c:401`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:401)。
非 MQ 的 `tio` 来自独立 mempool，并由 `free_old_rq_tio()` 显式释放，见
[`dm-rq.c:112`](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c:112)。
在本目标源码中，释放发生在 `rq_completed()` 之后，不是之前。

即便不看 T0144 的 clone 对象，这一点也足以反驳报告 A 对目标版本
`clone == NULL` 分支的释放顺序描述。

## 发现五：报告 A 为什么会选中错误补丁

`61febef40bfe` 的标题和报告 A 的初始印象高度相似：

```text
dm-rq: don't dereference request payload after ending request
```

它讨论的也是 `dm_softirq_done()`、UAF 和非 blk-mq。会话在不能运行 crash 后
搜索到它，随后发生了“先选补丁、再把现场套入补丁”的反向论证：

1. 从函数名和 UAF 类型找到相似提交；
2. 假定 `clone==NULL`；
3. 把 `RBX=0` 命名为 clone；
4. 把 `RDI` 命名为 tio；
5. 再把 iSCSI 日志串成进入该分支的故事。

而 T0144 是从 fault 指令出发，直到最后才对照补丁。它识别的
`b4459b11e840` 修复的是另一安全不变量：DM suspend 时 blk-mq queue_rq 必须
拒绝并重排队请求。上游补丁说明也明确提到 elevator 切换、更新
`nr_requests` 等外部 unquiesce 事件，以及 dm-mpath suspend/resume 压力。

## 发现六：iSCSI 被错误升级为直接根因

报告 A 观察到真实的 iSCSI/Actifio 事件，但缺少两个关键连接：

1. 这些事件是否作用于 faulting dm 设备；
2. faulting request 的实际 clone 发往哪个底层设备。

T0144 恢复出：

```text
orig request:  dm-19
clone request: nvme38n1
dm-19 paths:   nvme37n1, nvme38n1
```

因此 iSCSI 不在本次 faulting I/O 的直接路径。报告 B 对此的最终分层是正确的：

- iSCSI 事件存在：`supported`；
- iSCSI 是直接 I/O 路径：`refuted`；
- iSCSI uevent 经 multipathd 全局 reconfigure 间接促成 dm-19 reload：
  `inconclusive`。

时间邻近只能生成候选假设，不能替代
`iSCSI → udev/multipathd → dm-19 reload ioctl → 竞态窗口 → faulting request`
的对象链。

## 发现七：报告 B 更可信，但不是每句话都已证明

### 已闭合

- fault 指令为 `mov 0x8(%rdi),%rdx`；
- RDI 是 `tio->ti`，fault 字段为 `ti->type`；
- clone 非 NULL，路径为 blk-mq；
- fault 指针 PTE=0；
- 同一 md 当前 target 已变化；
- fault/current target 均符合 `highs+0x40` 分配几何；
- old table 的目标源码销毁路径最终 `vfree(t->highs)`；
- `dm_mq_queue_rq()` 保存 target 裸指针且缺少 suspend flag guard；
- faulting clone 为 NVMe，iSCSI 不是直接路径。

### 应降低措辞强度

1. **PTE=0 本身不能单独证明“只能是 vfree”**。报告 B 第 386–394 行把
   `PTE=0 → vfree` 写得过于绝对。严谨结论来自 PTE、对象来源、`+0x40`
   几何、当前新 target 和目标源码 destroy 路径的组合，置信度为高，而不是
   单条页表证据的唯一演绎。
2. **具体外部 unquiesce 动作未恢复**。可以确认缺失 guard 是代码级安全
   不变量缺口，但不能说现场一定由 elevator、`nr_requests` 或 iSCSI 触发。
3. **回移植运行效果未验证**。上游补丁在新 API 返回
   `BLK_STS_RESOURCE`；目标 3.10 语义等价返回应为
   `BLK_MQ_RQ_QUEUE_BUSY`，仍需构建和 A/B 压测。
4. **“3.10.0-1160.119.1 已直接修复”未被证明**。报告 B 第 846–853 行
   本来使用“可能、如需精确确认”的谨慎措辞，但第 951 行又升级为确定断言。

## 发现八：RHEL 修复版本声明需要撤回

报告 A 声称：

- `3.10.0-1160.88.1` 是首个包含修复的版本；
- `3.10.0-1160.119.1` 已包含修复。

报告 B 的整改表也声称 119.1 直接修复该缺陷。

公开的一手资料不能支持该断言：

- [RHSA-2023:1091](https://access.redhat.com/errata/RHSA-2023:1091) 确实交付
  `3.10.0-1160.88.1`，但其公开 Bug Fix 列表没有该 device-mapper suspend
  guard；不能因为版本号更高就推定包含。
- [Red Hat Bug 2282917 / CVE-2021-47498](https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2021-47498)
  在公开页面中仍显示 `NEW`，并列出的 fixed versions 是 `kernel 5.14.14,
  kernel 5.15`，没有列 RHEL 7 的 3.10 z-stream。

因此当前判定为：

```text
“88.1 首修”             refuted/unsupported
“119.1 已含该 guard”     inconclusive，且与公开跟踪状态不一致
```

安全做法是检查目标发行商 SRPM 中 `dm_mq_queue_rq()` 的实际代码，或向 Red Hat
支持提交 commit/CVE 号确认；在此之前不能承诺“重启到 119.1 即确定不会复发”。

## 为什么差异会扩大成两个完全不同的故事

### 1. 输入证据等级不同

日志只能告诉“在哪里崩、有哪些寄存器和附近事件”；crash+DWARF 才能回答
“寄存器是什么对象、字段偏移是什么、request 指向哪个设备”。报告 A 越过了
这个边界。

### 2. 第一处分支判断错误产生级联

`RDI=tio` 与 `RDI=tio->ti` 只差一层指针，但会改变：

- fault 字段：`md` vs `type`；
- 被释放对象：tio vs dm_target；
- allocator：slab/mempool vs vmalloc；
- 释放函数：end_request vs dm_table_destroy/vfree；
- 补丁：61feb vs b4459；
- queue 路径：非 MQ vs MQ。

### 3. 相似补丁造成锚定

同一函数名、同为 UAF、同有 `dead...` 值，使 61feb 看起来“非常像”。没有
反汇编和对象恢复时，模型容易把相似 bug 当成同一个 bug。

### 4. 时间相关性被升级为对象因果

iSCSI 日志很显眼，而 NVMe clone 身份只有对象遍历才能看到。报告 A 因此把最
显眼的外部事件选为直接触发者。

### 5. 来源环境与事故对象混淆

报告 A 把远端分析机当前主机名 `nbusvr103` 写成事故主机，并把文件日期/当前
机器信息混入事故时间线；报告 B 使用 messages 与 vmcore 交叉恢复
`shqddb2`。这说明 A 混合了“保存 vmcore 的机器当前状态”和“vmcore 所代表的
崩溃系统状态”。

### 6. 限制说明在派生副本中被删除

原始 A 明确说明没有 debuginfo；Downloads 版本删除该说明，却保留 crash
参考命令。读者看到的文档因此显得比实际分析过程更有证据基础。

### 7. 报告 B 实际上是后续独立复核产物

它不是对 A 做简单润色，而是重新执行了取证并主动证伪 A 的分支。证据新增量
足以改变根因，而不仅是改变表述。

## 两份报告的总体 verdict

### 报告 A

| 层级 | verdict | 说明 |
|---|---|---|
| panic 位置、CPU、softirq 栈 | `supported` | 来自 dmesg 原始文本 |
| “属于某种 UAF” | `supported`，中等 | 非零悬垂地址/PTE 与后续复核一致 |
| RDI/tio、clone-null、非 MQ、tio payload UAF | `refuted` | 被反汇编、DWARF、对象和目标源码反驳 |
| iSCSI 直接诱发 | `refuted` | fault clone 为 NVMe |
| 61feb 同源修复 | `refuted` | 不同分支与不同生命周期 |
| 88.1/119.1 修复状态 | `unsupported` | 无发行商或源码证明 |

整体可信度：**低**，只适合作为早期假设和日志摘要，不能作为最终 RCA。

### 报告 B

| 层级 | verdict | 说明 |
|---|---|---|
| fault 字段和运行时对象 | `supported`，高 | 两轮 crash + DWARF + 反汇编 |
| old dm_target completion UAF | `supported`，高 | 对象几何、页表、table 生命周期闭环 |
| 缺失 suspend guard 为代码级根因 | `supported`，高 | 目标源码与上游补丁同源性 |
| iSCSI 非直接路径 | `supported`，高 | clone/gendisk/path 对象 |
| 具体外部 unquiesce 来源 | `inconclusive` | 静态 vmcore 无历史事件链 |
| iSCSI 间接促成 | `inconclusive` | 缺少 multipathd/ioctl 对象链 |
| 119.1 已修复且确定不复发 | `unsupported` | 未核验发行商源码/回移植 |

整体可信度：**高，但整改版本声明和少数“唯一/确定”措辞需要修订**。

## 结论与建议

### 应采信的技术根因

采信报告 B/T0144 的代码级根因，但使用以下收敛措辞：

> 本次 panic 的直接原因是 `dm_softirq_done()` 完成路径解引用已失效的
> `tio->ti->type`。该 `tio->ti` 高置信属于同一 dm-19 的旧 table target，
> 在 table swap 后随旧 table 销毁而解除映射。目标 3.10 内核的
> `dm_mq_queue_rq()` 缺少 suspend flag guard，允许 request-based blk-mq
> 请求在 suspend 隔离被外部打破时保存旧 target 并跨越 table destroy。
> faulting I/O 的直接底层路径是 NVMe；具体外部 unquiesce 动作及 iSCSI
> 是否间接促成 reload 尚未闭合。

### 报告修订建议

1. 报告 A 标记为“早期日志假设稿/已被后续 vmcore 取证推翻”，不要继续作为
   最终 RCA。
2. 报告 B 保留核心证据链，但把“PTE=0 直接唯一证明 vfree”改为组合证据的
   高置信推断。
3. 删除或改写“119.1 确定包含修复、升级后确定不会复发”；在核验 SRPM 或
   发行商支持答复后再指定修复版本。
4. 保留 iSCSI 稳定性治理建议，但把它与本次内核直接根因分栏，不写成已证明
   的直接触发条件。
5. 若要关闭剩余分支，最小追加证据是：
   - 目标升级内核的 `dm_mq_queue_rq()` 源码/反汇编，确认存在语义等价 guard；
   - multipathd debug、udev 与 DM ioctl 审计，连接 iSCSI 事件和 dm-19 reload；
   - 补丁前后 suspend/reload + `nr_requests`/queue 事件 A/B 压测。

## 参考资料

- [报告 A](/home/black/Downloads/vmcore_analysis_report.md)
- [报告 A 原始生成文件](/home/black/vmcore_analysis_report.md)
- [报告 A 去敏分析过程账本](analysis-process-ledger.md)
- [报告 B](</home/black/Downloads/shqddb2内核崩溃根因分析报告v2.md>)
- [T0144 根因证明](/home/black/Documents/pdca-workflow/records/T0144-0729-vmcore-source-revalidation/evidence/root-cause-proof.md)
- [T0144 逻辑闭合审查](/home/black/Documents/pdca-workflow/records/T0144-0729-vmcore-source-revalidation/evidence/logic-closure-review.md)
- [T0144 补丁同源性证明](/home/black/Documents/pdca-workflow/records/T0144-0729-vmcore-source-revalidation/evidence/patch-equivalence-proof.md)
- [目标源码 dm-rq.c](/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/drivers/md/dm-rq.c)
- [Linux 上游提交 b4459b11e840](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b4459b11e84092658fa195a2587aff3b9637f0e7)
- [Red Hat RHSA-2023:1091](https://access.redhat.com/errata/RHSA-2023:1091)
- [Red Hat CVE-2021-47498 / Bug 2282917](https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2021-47498)
