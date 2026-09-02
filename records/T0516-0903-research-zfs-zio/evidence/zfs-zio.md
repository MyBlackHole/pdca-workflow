---
schema: pdca.asset/v1
id: ontology:entity/zfs-zio
type: entity
layer: Knowledge
status: active
summary: ZFS ZIO 实体 — I/O Pipeline 位图调度与 VDEV 子流水线及 transform 栈
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:domain/zfs-crypto
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: pipeline_bitmap
    desc: ZIO pipeline 位图组合可测
    constraint: 覆盖 enum zio_stage 1<<n 与 ZIO_READ/WRITE/FREE/CLAIM 等宏及 __zio_execute 循环按位推进，支持 GANG/DDT/BRT/NOPWRITE/ENCRYPT 按需插入
    testable_signal: "运行 grep -q 'ZIO_WRITE_PIPELINE' records/T0516-0903-research-zfs-zio/research-zio.md 且 grep -q 'ZIO_STAGE_WRITE_COMPRESS' include/sys/zio_impl.h 命中"
  - name: vdev_dispatch
    desc: VDEV 子流水线与 taskq 分发可测
    constraint: 覆盖 zio_create→zio_execute→__zio_execute→zio_vdev_io_start→vdev_queue_io→leaf vdev 完整链，含 spa_taskq_dispatch 与 ZIO_STAGE_VDEV_IO_START/DONE/ASSESS
    testable_signal: "运行 grep -q '__zio_execute' records/T0516-0903-research-zfs-zio/research-zio.md 且 grep -q 'vdev_queue_io' module/zfs/vdev_queue.c 命中"
  - name: transform_stack
    desc: transform 栈压缩/加密/校验可逆变换可测，对应时序图 transform 压栈-弹栈与状态机 ZIO_STAGE_ENCRYPT/COMPRESS 往返
    constraint: 覆盖 zio_push_transform / zio_pop_transforms 栈，COMPRESS/ENCRYPT/CHECKSUM_GENERATE/CHECKSUM_VERIFY 的压栈-弹栈可逆与 ABD 变换，及 zio_transform_stack_depth 边界，经 C4 L3 与状态机可一图建模
    testable_signal: "运行 grep -q 'zio_push_transform' records/T0516-0903-research-zfs-zio/research-zio.md 且 grep -q 'zio_push_transform' module/zfs/zio.c 命中"
---

# ZFS ZIO（I/O Pipeline）

I/O 流水线：`zio_t` 以 `enum zio_stage`（每 stage `1<<n`）位图定义 pipeline，`ZIO_READ/WRITE/FREE/CLAIM` 等宏按位组合，`__zio_execute` 以 `while (io_stage < ZIO_STAGE_DONE)` 按位推进；支持按需插入 `GANG/DDT/BRT/NOPWRITE/ENCRYPT`；`zio_push_transform` 栈实现压缩/加密/校验的可逆变换；`VDEV` 子流水线 `VDEV_IO_START/DONE/ASSESS` 经 `spa_taskq_dispatch` 落至 `vdev_queue`。

## C4 L3 Component — ZIO pipeline 位图调度

`zio_t` 含 `io_stage`（当前 stage 位）、`io_pipeline`（位图，`ZIO_*_PIPELINE` 宏预组合）、`io_transform_stack`（`zio_transform_t` 栈顶指针）、`io_vdev`/`io_bp`（目标 VDEV 与 blkptr）。`enum zio_stage` 每个枚举值为 `1<<n`（如 `ZIO_STAGE_OPEN=1<<0`、`WRITE_COMPRESS=1<<3`、`VDEV_IO_START=1<<8`），`ZIO_WRITE_PIPELINE = WRITE_COMMON + WRITE_BP_INIT + COMPRESS + ENCRYPT + CHECKSUM_GENERATE + DVA_THROTTLE + DVA_ALLOCATE + READY + VDEV_IO_START` 以位或拼装；`ZIO_READ_PIPELINE = READ_COMMON + READ_BP_INIT + VDEV_IO_START + CHECKSUM_VERIFY + DECRYPT + DECOMPRESS`。`__zio_execute` 核心循环 `while (io_stage < ZIO_STAGE_DONE) { stage = 1 << highbit(io_pipeline & ~executed); switch(stage) ... }` 按位推进，`zio_reexecute` 可在子 ZIO 完成回调中按需置位 `GANG/DDT/BRT` stage。C4 L3 图以 `zio_t → pipeline bitmap → stage executor → transform stack → vdev_queue` 五组件呈现该调度。

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（`enum zio_stage` 与 `ZIO_*_PIPELINE` 宏定义）+ `openzfs/zfs/module/zfs/zio.c:934`（`zio_create` 签名与 `io_pipeline` 赋值）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute` while 循环按位推进）

## 时序 — zio_create → zio_execute → __zio_execute → vdev_queue_io → leaf vdev

写主路径：1) `zio_write(pio, spa, txg, bp, abd, lsize, psize)` → `zio_create(pio, ..., ZIO_TYPE_WRITE, ZIO_WRITE_PIPELINE, ...)` 分配 `zio_t` 并设 `io_pipeline`；2) `zio_execute(zio)` 入 `__zio_execute` 循环；3) 依次命中 `ZIO_STAGE_WRITE_BP_INIT → WRITE_COMPRESS（zio_push_transform 压压缩）→ ZIO_STAGE_ENCRYPT（zio_push_transform 压加密）→ ZIO_STAGE_CHECKSUM_GENERATE → ZIO_STAGE_DVA_ALLOCATE（metaslab_alloc 选 DVA）→ ZIO_STAGE_READY`；4) `ZIO_STAGE_VDEV_IO_START` 中 `zio_vdev_child_io` 为每个 DVA 创建 `io_vsd` 子 ZIO 并 `zio_execute` 子 pipeline；5) 子 ZIO 经 `spa_taskq_dispatch` 按 `zio_taskqs[ZIO_TASKQ_ISSUE]` 分发至 `vdev_queue_io`，leaf `vdev_disk_io_start` 落盘；6) `VDEV_IO_DONE → VDEV_IO_ASSESS → CHECKSUM_VERIFY` 回调主 ZIO，再 `zio_pop_transforms` 弹栈。读路径共用 `VDEV_IO_START/DONE/ASSESS` 子流水线，`READ_BP_INIT` 处理 `GANG` 拼装与 `DDT` 查表。时序图以 `DMU/TXG → zio_create → __zio_execute loop → VDEV queue → leaf → ASSESS → transform pop` 全链呈现该分发衔接。

Source: `openzfs/zfs/module/zfs/zio.c:934`（`zio_create` pipeline 赋值）+ `openzfs/zfs/module/zfs/zio.c:2186`（`spa_taskq_dispatch` 与 `zio_taskqs` 定义）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute` 调度循环）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io` 入队与 `vdev_queue_issue` 调度）

## 状态机 — transform 栈的压栈-弹栈可逆变换

`zio_transform_t` 栈节点含 `zt_orig_abd / zt_orig_size / zt_transform`（变换函数指针），`zio_t.io_transform_stack` 为单向链表栈顶。状态五态：`ZT_NONE`（空栈）→ `ZT_COMPRESSED`（`WRITE_COMPRESS` 压入 `compress_func`，`lsize→psize`）→ `ZT_ENCRYPTED`（`ENCRYPT` 压入 `encrypt_func`，`abd` 替换为加密后 abd）→ `ZT_CHECKSUMMED`（`CHECKSUM_GENERATE` 压入 `checksum_func`）→ `ZT_READY`（`READY` 固化 `bp`），读方向逆向 `ZT_READY → ZT_CHECKSUM_VERIFIED（CHECKSUM_VERIFY）→ ZT_DECRYPTED（DECRYPT 弹加密）→ ZT_DECOMPRESSED（DECOMPRESS 弹压缩）→ ZT_NONE（zio_pop_transforms 逐项还原 `abd` 与 `size`）`。`zio_push_transform` 在 `zt_stack_depth < ZIO_TRANSFORM_STACK_DEPTH`（默认 8）时 `kmem_alloc` 新节点入栈，`zio_pop_transforms(is_write)` 按 `io_pipeline` 中是否含对应 stage 决定是否回放。状态机图覆盖写压栈三阶与读弹栈三阶及 `depth` 溢出分支。

Source: `openzfs/zfs/module/zfs/zio.c:320-420`（`zio_push_transform` / `zio_pop_transforms` 栈实现与 `ZIO_TRANSFORM_STACK_DEPTH`）+ `openzfs/zfs/include/sys/zio_impl.h:260-320`（`zio_transform_t` 定义与 `ZIO_STAGE_ENCRYPT/COMPRESS/CHECKSUM_*`）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute` 中 transform stage 调度）

## 决策树

```mermaid
flowchart TD
    START([ZIO 到达 __zio_execute]) --> Q1{io_type?}
    Q1 -- WRITE --> Q2{压缩开启?}
    Q2 -- 是 lsize>psize --> A1[WRITE_COMPRESS<br/>zio_push_transform compress]
    Q2 -- 否 --> A2[跳过 COMPRESS stage]
    A1 --> Q3{加密数据集?}
    A2 --> Q3
    Q3 -- 是 dataset加密 --> A3[ENCRYPT<br/>zio_push_transform encrypt<br/>abd 替换]
    Q3 -- 否 --> A4[跳过 ENCRYPT]
    A3 --> Q4{需要分配?}
    A4 --> Q4
    Q4 -- 需 metaslab --> A5[DVA_ALLOCATE<br/>metaslab_alloc 选 DVA]
    Q4 -- 已有 DVA --> A6[直接 READY]
    A5 --> Q5{VDEV 类型?}
    A6 --> Q5
    Q5 -- mirror/raidz --> A7[zio_vdev_child_io<br/>子 pipeline VDEV_IO_START]
    Q5 -- leaf disk --> A8[vdev_queue_io<br/>spa_taskq_dispatch ZIO_TASKQ_ISSUE]
    A7 --> Q6{读 or 写?}
    A8 --> Q6
    Q6 -- 写 --> END1([VDEV_IO_DONE→ASSESS<br/>zio_pop_transforms 验证])
    Q6 -- 读 --> END2([CHECKSUM_VERIFY→DECRYPT→DECOMPRESS<br/>逐项弹栈还原 abd])
```

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（`enum zio_stage` 位图与 `ZIO_*_PIPELINE`）+ `openzfs/zfs/module/zfs/zio.c:934`（`zio_create`）+ `openzfs/zfs/module/zfs/zio.c:320-420`（`zio_push_transform` 分支）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io` 分发）

## 正例

```c
// 正例1：写 pipeline 正确按位图创建与执行，transform 栈配对压弹
zio_t *pio = NULL; // parent zio
zio_t *zio = zio_create(pio, spa, txg, bp, abd, lsize, psize, zio_write_done, NULL,
    ZIO_TYPE_WRITE, ZIO_PRIORITY_SYNC_WRITE, 0, NULL, 0, ZIO_STAGE_OPEN,
    ZIO_WRITE_PIPELINE); // 位图含 COMPRESS+ENCRYPT+CHECKSUM+DVA_ALLOCATE+READY+VDEV_IO_START
zio_execute(zio); // 内部 __zio_execute while(io_stage < DONE) 按位推进
// ZIO_STAGE_WRITE_COMPRESS: 若可压缩则 zio_push_transform(zio, abd, psize, compress_func)
// ZIO_STAGE_ENCRYPT: 若加密数据集则 zio_push_transform(zio, enc_abd, enc_size, decrypt_func)
// 读完成回调中自动 zio_pop_transforms(zio) 逆序还原 abd 与 size

// 正例2：VDEV 子流水线正确经 taskq 分发至 leaf
zio_t *child = zio_vdev_child_io(zio, bp_child, vdev, offset, abd, psize, ZIO_TYPE_WRITE, ZIO_PRIORITY_SYNC_WRITE, 0, zio_vdev_io_done, NULL);
// child->io_pipeline = ZIO_VDEV_CHILD_PIPELINE (VDEV_IO_START|VDEV_IO_DONE|VDEV_IO_ASSESS)
zio_execute(child); // __zio_execute 命中 VDEV_IO_START -> spa_taskq_dispatch -> vdev_queue_io -> leaf vdev_disk_io_start
```

命中：`zio_create` 时 `ZIO_WRITE_PIPELINE` 位图与 `ZIO_TYPE_WRITE` 配对，`__zio_execute` 按位推进，`zio_push_transform` 在对应 stage 内且读侧 `zio_pop_transforms` 逆序还原，`zio_vdev_child_io` 经 `spa_taskq_dispatch` 落 `vdev_queue_io`。

## 反例

```c
// 反例1：pipeline 位图与 io_type 错配导致 stage 漏执行
zio_t *zio = zio_create(pio, spa, txg, bp, abd, lsize, psize, done, NULL,
    ZIO_TYPE_READ, ZIO_PRIORITY_SYNC_READ, 0, NULL, 0, ZIO_STAGE_OPEN,
    ZIO_WRITE_PIPELINE); // 错：READ 类型却配 WRITE_PIPELINE，__zio_execute 误入 WRITE_COMPRESS/ENCRYPT，bp 错误

// 反例2：漏配对 transform 弹栈导致 ABD 悬挂与数据错
zio_push_transform(zio, enc_abd, enc_size, decrypt_func); // 加密后替换 abd
// 漏 zio_pop_transforms：读完成未弹栈还原，abd 仍指向加密后密文，DECOMPRESS 以密文解压直接 ECKSUM

// 反例3：VDEV 子 ZIO 绕过 taskq 直接同步调用 leaf 导致调度饥饿
// 错：直接调用 vdev_disk_io_start(child) 而非 zio_execute(child)
// 结果：未进 spa_taskq_dispatch 的 ZIO_TASKQ_ISSUE 队列，绕过 vdev_queue 的 deadline 调度，破坏并发限流与 I/O 聚合

// 反例4：transform 栈深度未检查溢出
for (int i = 0; i < 16; i++)
    zio_push_transform(zio, abd, size, func); // 错：超 ZIO_TRANSFORM_STACK_DEPTH(8) 未检，直接 kmem 越界或断言
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' records/T0516-0903-research-zfs-zio/research-zio.md` ≥3
- **溯源门禁**：`grep -c 'Source:' records/T0516-0903-research-zfs-zio/research-zio.md` ≥3 且每图附 `openzfs/zfs file:line`
- **正文门禁**：`wc -l ontology/entity/zfs-zio.md` ≥60 且 `grep -q '决策树' ontology/entity/zfs-zio.md && grep -q '正例' ontology/entity/zfs-zio.md && grep -q '反例' ontology/entity/zfs-zio.md && grep -q '门禁' ontology/entity/zfs-zio.md`
- **属性门禁**：`attributes` 数量 ≥3 且每条 `testable_signal` 含 `grep -q` 动词+判定
- **本体校验**：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues 且 `python3 scripts/ontology_graph.py --format summary` `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/zfs-zio --out /tmp/test_zfs_zio_scaffold.py` 可产且 `pytest` 可收集
- **收敛门禁**：`python3 scripts/validate-convergence.py --task-dir pdca/tasks/0903-research-zfs-zio` `valid:true`

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（`enum zio_stage`）+ `openzfs/zfs/module/zfs/zio.c:934`（`zio_create`）+ `openzfs/zfs/module/zfs/zio.c:2428`（`__zio_execute`）+ `openzfs/zfs/module/zfs/zio.c:320-420`（`zio_push_transform`）+ `openzfs/zfs/module/zfs/vdev_queue.c:80-180`（`vdev_queue_io`）+ `openzfs/zfs/module/zfs/vdev.c:120`（`vdev_alloc`）
