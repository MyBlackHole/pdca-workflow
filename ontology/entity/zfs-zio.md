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
    constraint: 覆盖 enum zio_stage 1<<n 与 ZIO_READ/WRITE_PIPELINE 位图宏及 __zio_execute 循环
    testable_signal: "运行 grep -q 'ZIO_WRITE_PIPELINE' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'ZIO_STAGE_WRITE_COMPRESS' include/sys/zio_impl.h 命中"
  - name: vdev_dispatch
    desc: VDEV 子流水线与 taskq 分发可测
    constraint: 覆盖 zio_create→zio_execute→__zio_execute→vdev_queue_io→leaf vdev 完整链
    testable_signal: "运行 grep -q '__zio_execute' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'zio_execute' module/zfs/zio.c 命中"
---

# ZFS ZIO（I/O Pipeline）

I/O 流水线：`zio_t` 以 `enum zio_stage`（每 stage `1<<n`）位图定义 pipeline，`ZIO_READ/WRITE/FREE/CLAIM` 等宏按位组合，`__zio_execute` 以 `while (io_stage < ZIO_STAGE_DONE)` 按位推进；支持按需插入 `GANG/DDT/BRT/NOPWRITE/ENCRYPT`；`zio_push_transform` 栈实现压缩/加密/校验的可逆变换；`VDEV` 子流水线 `VDEV_IO_START/DONE/ASSESS` 经 `spa_taskq_dispatch` 落至 `vdev_queue`。

Source: `openzfs/zfs/include/sys/zio_impl.h:60-260`（stage 与 pipeline 宏）+ `openzfs/zfs/module/zfs/zio.c:934,2428`（zio_create/__zio_execute）
