# b4459b11e840 与 T0144 崩溃的同源性及修复充分性证明

## 1. 要证明的三个命题

不能把“提交说明相似”直接等同于“已经证明修复”。需分别证明：

- **命题 S1：同源性**  
  T0144 与 b4459b11e840 修复的是同一个安全不变量破坏：DM suspend
  期间 blk-mq request 仍能进入 `dm_mq_queue_rq()`。
- **命题 S2：机制充分性**  
  guard 能切断 T0144 从 suspend 中闯入请求到 stale `tio->ti` 的必要路径。
- **命题 S3：运行时有效性**  
  针对 3.10 API 做语义等价回移植后，在相同压力下不再发生 flag
  置位期间的 request mapping/UAF，同时不破坏正常 I/O。

当前 vmcore + 源码可以高置信证明 S1、静态证明 S2。S3 必须通过实际回移植、
编译和补丁前后 A/B 压测才能最终证明。

## 2. 上游提交到底修改了什么

上游提交：

- SHA：`b4459b11e84092658fa195a2587aff3b9637f0e7`
- 标题：`dm rq: don't queue request to blk-mq during DM suspend`
- 上游链接：
  https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b4459b11e84092658fa195a2587aff3b9637f0e7

提交在 `dm_mq_queue_rq()` 中读取 `md->immutable_target` 后、第一次使用 target
之前增加：

```c
if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
        return BLK_STS_RESOURCE;
```

提交说明明确描述：

1. DM 用 blk-mq quiesce/unquiesce 停止和启动 queue；
2. unquiesce 也可能由 DM 外部事件触发，例如 elevator 切换、更新
   `nr_requests`；
3. 请求因此可能在 suspend 中进入；
4. 修复策略是让 blk-mq 重排队；
5. 原问题可在 `nr_requests` 更新与 dm-mpath suspend/resume 压测中触发
   kernel panic。

## 3. S1：与 T0144 是否为同一 bug

### 3.1 配置与执行路径相同

| 上游修复前提 | T0144 vmcore 证明 | 结果 |
|---|---|---|
| request-based DM | 当前 table type=`DM_TYPE_MQ_REQUEST_BASED` | 相同 |
| 使用 blk-mq | `mapped_device.use_blk_mq=true`、queue ops=`dm_mq_ops` | 相同 |
| dm-multipath | target type=`multipath_target [dm_multipath]` | 相同 |
| 完成走 `dm_softirq_done()` | RIP=`dm_softirq_done+97`，栈含 `blk_done_softirq` | 相同 |

### 3.2 被破坏的不变量相同

正常不变量：

```text
DMF_BLOCK_IO_FOR_SUSPEND == 1
    ⇒ 不允许新 request 进入 target mapping
    ⇒ pending drain 后不再出现引用旧 table 的新请求
    ⇒ old table 可以安全销毁
```

本地源码：

- `dm.c:2536` 设置 `DMF_BLOCK_IO_FOR_SUSPEND`；
- `dm.c:2545` quiesce queue；
- `dm.c:2557` 等待 pending 为 0；
- `dm-rq.c:889–927` 的 `dm_mq_queue_rq()` 完全不检查该 flag。

因此本地 request-based blk-mq 路径没有执行这个不变量。

### 3.3 vmcore 显示了不变量被破坏后的特征状态

T0144：

```text
tio->ti             = ffffbd16abacc040  // request 保存的旧 target
current immutable ti= ffffbd16abbd2040  // md 当前新 target
old ti vtop         = not mapped, PTE 0
current targets     = current highs + 0x40
old ti              = another vmalloc page + 0x40
```

指定源码证明：

1. `dm-rq.c:895` 从 `md->immutable_target` 取 target；
2. `dm-rq.c:908` 增加 pending；
3. `dm-rq.c:916` 保存到 `tio->ti`；
4. `dm.c:2063` table bind 更新 `md->immutable_target`；
5. `dm-ioctl.c:1068` resume 后 destroy old map；
6. `dm-table.c:255` 对包含 target 的 vmalloc block 执行 `vfree()`；
7. `dm-rq.c:361` 完成时再次读取 `tio->ti->type`。

这正是“请求在旧 table 销毁前取得旧 target、在销毁后完成”的状态。

### 3.4 table swap 必然经过 suspend

`dm.c:2405–2407`：

```c
/* device must be suspended */
if (!dm_suspended_md(md))
        goto out;
```

因此 current/old target 替换不是无 suspend 的正常 swap。旧请求跨越 table
销毁而仍未完成，说明 suspend 的“禁止新 request + drain”不变量没有成立。

### 3.5 同源性判定

**同一 bug 类和同一缺失保护点：高置信成立。**

静态 vmcore 无法指出是哪一个线程执行了外部 unquiesce；但是无论它来自
`nr_requests`、elevator、queue stopped/quiesced 边界还是其他外部路径，
只要表现为 `DMF_BLOCK_IO_FOR_SUSPEND=1` 时调用 `dm_mq_queue_rq()`，
b4459b11e840 修复的就是这个共同的不变量破坏。

## 4. S2：为什么该 guard 足以切断此次崩溃路径

### 4.1 补丁前控制流

本地 `drivers/md/dm-rq.c:889–923`：

```text
ti = md->immutable_target        // 可能为旧 table target
ti->type->busy(...)              // 第一次解引用
dm_start_request(md, rq)         // pending++
init_tio(...)
tio->ti = ti                     // 裸指针跨异步 I/O 保存
map_request(tio)                 // 下发 clone
```

如果 queue 在 suspend 期间被重新 unquiesce，该路径没有任何 flag 检查。

### 4.2 补丁后控制流

语义为：

```text
ti = md->immutable_target
if DMF_BLOCK_IO_FOR_SUSPEND:
        return REQUEUE

// 只有 flag 清除后才允许：
dereference ti
pending++
tio->ti = ti
map_request
```

guard 位于以下所有危险操作之前：

- `ti->type` 解引用；
- pending 墇加；
- `tio->ti` 保存；
- clone 下发。

所以 flag 置位期间闯入的 request 不会持有 target 跨越 table destroy。

### 4.3 3.10 中 REQUEUE 的语义等价

上游新 API 返回 `BLK_STS_RESOURCE`。当前 3.10 接口返回 `int`，对应值是：

```c
BLK_MQ_RQ_QUEUE_BUSY = 1; /* requeue IO for later */
```

本地 `block/blk-mq.c:1267–1279` 和 `1753–1756` 证明：

```c
case BLK_MQ_RQ_QUEUE_BUSY:
        __blk_mq_requeue_request(rq);
        break;
```

因此 3.10 的语义等价回移植应返回 `BLK_MQ_RQ_QUEUE_BUSY`，不能机械复制
`BLK_STS_RESOURCE`。

### 4.4 resume 后为什么能安全重试

本地时序：

1. `__bind()` 先安装新 `md->immutable_target`；
2. `dm_resume()` 的 `dm_queue_flush()` 清除 block flag；
3. `dm-rq.c:72–76` unquiesce queue 并 kick requeue list；
4. 被 BUSY 重排队的 request 重新进入，读取的是新 target；
5. `do_resume()` 随后销毁 old map。

因此被 guard 拦截的 request 不会保存旧 target，resume 后仍能正常重试。

### 4.5 反事实证明

把补丁条件代入 T0144 必要时序：

```text
事实：fault request 必须在 old target 仍是 immutable_target 时取得该指针；
事实：它未被 suspend pending drain 等待完成；
事实：old target 随后被 vfree；
必要条件：该 request 在 suspend block 窗口中仍进入 queue_rq/map_request。

加入 guard：
block flag == 1 ⇒ queue_rq 返回 BUSY
               ⇒ 不执行 dm_start_request
               ⇒ 不设置 tio->ti
               ⇒ 不下发 clone
               ⇒ 不可能在 old table vfree 后进入 dm_softirq_done
               ⇒ T0144 的 fault 链不可达。
```

所以对这条已证明的故障路径，guard 是充分切断条件。

## 5. 3.10 回移植注意事项

不能直接 cherry-pick 上游 8 行：

1. 本地 `dm_mq_queue_rq()` 返回 `int`，应返回
   `BLK_MQ_RQ_QUEUE_BUSY`；
2. `DMF_BLOCK_IO_FOR_SUSPEND` 当前只定义在 `dm.c`，`dm-rq.c`
   虽包含 `dm-core.h` 但看不到该宏；
3. 回移植需把该 flag 编号安全地共享到 DM internal header，或增加一个内部
   helper；必须避免重复定义和 KABI 影响；
4. guard 必须位于 `md->immutable_target` load 之后、任何 `ti`
   解引用及 `dm_start_request()` 之前；
5. 需要检查所有内部/外部 suspend 路径是否都使用同一 block flag。

语义等价伪补丁：

```c
/* DM internal shared definition/helper */
DMF_BLOCK_IO_FOR_SUSPEND == bit 0

/* dm_mq_queue_rq(), before ti->type dereference */
if (unlikely(test_bit(DMF_BLOCK_IO_FOR_SUSPEND, &md->flags)))
        return BLK_MQ_RQ_QUEUE_BUSY;
```

## 6. S3：动态证明补丁实际解决

### 6.1 必须使用补丁前后同环境 A/B

两套内核除该回移植外保持一致：

- A：当前未修复 3.10；
- B：增加语义等价 guard 的 3.10；
- 同一 dm-multipath request-based blk-mq 拓扑；
- 同一 I/O、CPU、queue 参数和 suspend/resume 压力；
- 每组运行足够多轮，记录总循环数和运行时间。

### 6.2 最小定向压力

并发三条流：

```text
流 1：fio 持续对 dm-multipath 设备执行读写
流 2：循环执行 dm table reload / suspend / resume
流 3：循环更新 /sys/block/dm-X/queue/nr_requests
      或切换可触发 blk-mq unquiesce 的 elevator/queue 属性
```

不要在生产机直接执行该压力。

### 6.3 增加可判定的观测点

调试内核增加计数/trace：

```text
C_enter_blocked:
  dm_mq_queue_rq() 入口且 DMF_BLOCK_IO_FOR_SUSPEND=1 的次数

C_mapped_blocked:
  flag=1 时仍执行 dm_start_request/map_request 的次数

C_requeued:
  guard 命中并返回 BUSY 的次数

C_stale:
  completion 时 tio->ti != md->immutable_target 且旧 table 已销毁的次数
```

预期：

| 指标 | 未补丁 A | 补丁 B |
|---|---:|---:|
| `C_enter_blocked` | 可大于 0 | 可大于 0 |
| `C_mapped_blocked` | 可大于 0 | 必须为 0 |
| `C_requeued` | 0 | 应与 blocked 入口对应 |
| `C_stale`/UAF/panic | 压力下可能出现 | 必须为 0 |

关键不是只看“没有 panic”，而是证明 guard 实际命中并阻止 mapping。

### 6.4 功能与回归检查

补丁 B 还必须满足：

- fio 数据校验无错误；
- suspend/resume 与 table reload 无永久挂起；
- multipath failover/failback 正常；
- requeue list 在 resume 后被 kick，所有请求最终完成；
- pending 最终回到 0；
- 无 request starvation、超时或显著吞吐回退；
- lockdep/debug counters 无异常。

### 6.5 动态通过标准

可将“已证明解决”定义为：

1. 未补丁 A 能观察到 `flag=1` 时进入并继续 mapping，最好能复现 stale
   target/UAF；
2. 补丁 B 在相同压力中仍能观察到 blocked 入口；
3. B 的 blocked 入口全部在 guard 返回 BUSY，`C_mapped_blocked=0`；
4. resume 后重排队请求全部完成；
5. B 在至少与 A 复现所需轮数相同、最好高一个数量级的压力中无
   stale target、UAF 或 panic；
6. 正常功能和性能回归检查通过。

如果 A 无法稳定 panic，也可用确定性的 fault injection：在 flag 置位后故意
触发 queue unquiesce，并用 barrier 扩大窗口。此时应证明 A 继续执行
`dm_start_request/map_request`，B 在同一位置返回 BUSY。

## 7. 当前能够与不能够宣称的结论

可以宣称：

- T0144 与 b4459b11e840 在子系统、queue 模式、缺失保护点、被破坏不变量和
  stale target 后果上相同；
- 该 guard 对 T0144 已证明的故障路径具有静态充分性；
- 3.10 必须做 API 语义回移植，不能原样使用 `BLK_STS_RESOURCE`。

尚不能宣称：

- 未构建、未运行的 3.10 回移植二进制已经通过验证；
- 此次具体外部 unquiesce 一定由 `nr_requests`、elevator 或 iSCSI 触发；
- 只运行一次“未再 panic”就证明问题消失。

最终严谨表述：

> T0144 是 b4459b11e840 所修复安全不变量的同类实例，且该 guard
> 在控制流上能切断本次 stale `tio->ti` 的必要路径；完成 3.10
> 语义回移植和定向 A/B 压测后，才能把“机制充分”升级为“运行时修复已验证”。

