# T0144 源码证据索引

源码基线：`/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7`

| 文件与行号 | 证据意义 |
|---|---|
| `drivers/md/dm-rq.c:354–364` | fault 对应 `tio->ti->type->rq_end_io` |
| `drivers/md/dm-rq.c:394–418` | `dm_softirq_done()` 取得 tio/clone 并进入 `dm_done()` |
| `drivers/md/dm-rq.c:702–731` | `dm_start_request()` 增加 pending |
| `drivers/md/dm-rq.c:889–927` | blk-mq 提交：读 target、增 pending、保存 `tio->ti`；缺少 suspend guard |
| `drivers/md/dm.c:2027–2082` | `__bind()` 更新 immutable target 与 map |
| `drivers/md/dm.c:2485–2578` | suspend 设置 block flag、quiesce、等待 pending |
| `drivers/md/dm-ioctl.c:1008–1068` | reload 的 suspend/swap/resume/destroy 顺序 |
| `drivers/md/dm-table.c:160–182` | highs 与 targets 的同块 vmalloc 布局 |
| `drivers/md/dm-table.c:234–255` | target 析构及 `vfree(t->highs)` |
| `block/blk-mq.c:221–237` | quiesce 等待在途 queue_rq 的 RCU/SRCU 语义 |

上游交叉验证：

- commit：`b4459b11e84092658fa195a2587aff3b9637f0e7`
- subject：`dm rq: don't queue request to blk-mq during DM suspend`
- URL：https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b4459b11e84092658fa195a2587aff3b9637f0e7
- 与当前源码差异：在读取 `md->immutable_target` 后检查 `DMF_BLOCK_IO_FOR_SUSPEND`，命中则要求 blk-mq 重排队。
