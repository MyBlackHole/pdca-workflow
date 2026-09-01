"""
ZFS ZIO 实体 — I/O Pipeline 位图调度与 VDEV 子流水线及 transform 栈
桩实现（Do 阶段最小可验证）：覆盖 ontology:entity/zfs-zio 两属性

属性1 pipeline_bitmap:
  enum zio_stage {每 stage 1<<n} + ZIO_READ/WRITE/FREE/CLAIM 等 pipeline 位图宏 + __zio_execute 循环
        对应 openzfs/zfs/include/sys/zio_impl.h:60-260 stage 与 pipeline 宏
        openzfs/zfs/module/zfs/zio.c:2428 __zio_execute while (io_stage < ZIO_STAGE_DONE) 按位推进
  约束: 覆盖 enum zio_stage 1<<n 与 ZIO_READ/WRITE_PIPELINE 位图宏及 __zio_execute 循环
  信号: grep -q 'ZIO_WRITE_PIPELINE' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'ZIO_STAGE_WRITE_COMPRESS' include/sys/zio_impl.h 命中

属性2 vdev_dispatch:
  完整链: zio_create(934) → zio_execute → __zio_execute(2428) → vdev_queue_io → leaf vdev
        对应 openzfs/zfs/module/zfs/zio.c:934 zio_create 签名与 pipeline 赋值
        openzfs/zfs/module/zfs/zio.c:2390 zio_execute → __zio_execute
        openzfs/zfs/include/sys/zio_impl.h:160-260 pipeline 定义
  约束: 覆盖 zio_create→zio_execute→__zio_execute→vdev_queue_io→leaf vdev 完整链
  信号: grep -q '__zio_execute' records/T0503-0903-research-zfs-implementation/research-report.md
        && grep -q 'zio_execute' module/zfs/zio.c 命中

设计: 极简内存桩，不依赖真实 ZFS 源码，仅提供位图 pipeline 与 while 按位推进的可测试接口
  - ZioStage 每成员 1<<n，ZIO_STAGE_DONE 为哨兵 1<<N
  - ZIO_*_PIPELINE 为 stage 位图或，__zio_execute 以 while (io_stage < ZIO_STAGE_DONE) 推进
  - zio_push_transform 栈实现压缩/加密/校验可逆变换
  - VDEV 子流水线 VDEV_IO_START/DONE/ASSESS 经 spa_taskq_dispatch 模拟落至 vdev_queue
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable, Dict, List, Optional


# 模拟 openzfs/zfs/include/sys/zio_impl.h:60-260 enum zio_stage 每 stage 1<<n
class ZioStage(IntEnum):
    ZIO_STAGE_OPEN = 1 << 0
    ZIO_STAGE_READ_BP_INIT = 1 << 1
    ZIO_STAGE_WRITE_BP_INIT = 1 << 2
    ZIO_STAGE_FREE_BP_INIT = 1 << 3
    ZIO_STAGE_ISSUE_ASYNC = 1 << 4
    ZIO_STAGE_WRITE_COMPRESS = 1 << 5
    ZIO_STAGE_ENCRYPT = 1 << 6
    ZIO_STAGE_CHECKSUM_GENERATE = 1 << 7
    ZIO_STAGE_NOPWRITE = 1 << 8
    ZIO_STAGE_BRT_FREE = 1 << 9
    ZIO_STAGE_DDT_READ_START = 1 << 10
    ZIO_STAGE_DDT_READ_DONE = 1 << 11
    ZIO_STAGE_DDT_WRITE = 1 << 12
    ZIO_STAGE_DDT_FREE = 1 << 13
    ZIO_STAGE_GANG_ASSEMBLE = 1 << 14
    ZIO_STAGE_GANG_ISSUE = 1 << 15
    ZIO_STAGE_DVA_THROTTLE = 1 << 16
    ZIO_STAGE_DVA_ALLOCATE = 1 << 17
    ZIO_STAGE_DVA_FREE = 1 << 18
    ZIO_STAGE_READY = 1 << 19
    ZIO_STAGE_VDEV_IO_START = 1 << 20
    ZIO_STAGE_VDEV_IO_DONE = 1 << 21
    ZIO_STAGE_VDEV_IO_ASSESS = 1 << 22
    ZIO_STAGE_CHECKSUM_VERIFY = 1 << 23
    ZIO_STAGE_DONE = 1 << 24


# 模拟 openzfs/zfs/include/sys/zio_impl.h:160-260 ZIO_*_PIPELINE 位图宏（按位或组合）
ZIO_STAGE_WRITE_COMPRESS = ZioStage.ZIO_STAGE_WRITE_COMPRESS
ZIO_STAGE_ENCRYPT = ZioStage.ZIO_STAGE_ENCRYPT
ZIO_STAGE_VDEV_IO_START = ZioStage.ZIO_STAGE_VDEV_IO_START

ZIO_WRITE_PIPELINE = (
    ZioStage.ZIO_STAGE_WRITE_BP_INIT
    | ZioStage.ZIO_STAGE_WRITE_COMPRESS
    | ZioStage.ZIO_STAGE_ENCRYPT
    | ZioStage.ZIO_STAGE_CHECKSUM_GENERATE
    | ZioStage.ZIO_STAGE_NOPWRITE
    | ZioStage.ZIO_STAGE_BRT_FREE
    | ZioStage.ZIO_STAGE_DVA_THROTTLE
    | ZioStage.ZIO_STAGE_DVA_ALLOCATE
    | ZioStage.ZIO_STAGE_READY
    | ZioStage.ZIO_STAGE_VDEV_IO_START
    | ZioStage.ZIO_STAGE_VDEV_IO_DONE
    | ZioStage.ZIO_STAGE_VDEV_IO_ASSESS
    | ZioStage.ZIO_STAGE_DONE
)

ZIO_READ_PIPELINE = (
    ZioStage.ZIO_STAGE_READ_BP_INIT
    | ZioStage.ZIO_STAGE_GANG_ASSEMBLE
    | ZioStage.ZIO_STAGE_DDT_READ_START
    | ZioStage.ZIO_STAGE_READY
    | ZioStage.ZIO_STAGE_VDEV_IO_START
    | ZioStage.ZIO_STAGE_VDEV_IO_DONE
    | ZioStage.ZIO_STAGE_VDEV_IO_ASSESS
    | ZioStage.ZIO_STAGE_CHECKSUM_VERIFY
    | ZioStage.ZIO_STAGE_DONE
)

ZIO_FREE_PIPELINE = (
    ZioStage.ZIO_STAGE_FREE_BP_INIT
    | ZioStage.ZIO_STAGE_DVA_FREE
    | ZioStage.ZIO_STAGE_READY
    | ZioStage.ZIO_STAGE_DONE
)

ZIO_CLAIM_PIPELINE = (
    ZioStage.ZIO_STAGE_READ_BP_INIT
    | ZioStage.ZIO_STAGE_READY
    | ZioStage.ZIO_STAGE_DONE
)


class ZioType(str):
    READ = "read"
    WRITE = "write"
    FREE = "free"
    CLAIM = "claim"


class ZioTransform(str):
    COMPRESS = "compress"
    ENCRYPT = "encrypt"
    CHECKSUM = "checksum"
    NOPWRITE = "nopwrite"


@dataclass
class Vdev:
    """leaf vdev 桩：模拟物理设备队列"""
    vdev_id: int
    vdev_type: str = "disk"
    queue: List["Zio"] = field(default_factory=list)
    completed: List["Zio"] = field(default_factory=list)

    def queue_io(self, zio: "Zio") -> None:
        """vdev_queue_io(zio) 模拟经 spa_taskq_dispatch 落至 vdev_queue"""
        self.queue.append(zio)
        # leaf vdev 同步完成（桩简化）
        self.completed.append(zio)
        zio.io_vdev_completed = True
        zio._trace.append(f"vdev_queue_io:{self.vdev_id}")


@dataclass
class Zio:
    """zio_t 桩：I/O 上下文，含 pipeline 位图与 transform 栈"""
    spa: Optional[str] = None
    io_type: str = ZioType.WRITE
    io_pipeline: int = 0
    io_stage: int = ZioStage.ZIO_STAGE_OPEN
    io_error: int = 0
    io_size: int = 4096
    io_offset: int = 0
    io_data: Optional[bytes] = None
    # transform 栈：zio_push_transform 可逆
    io_transforms: List[str] = field(default_factory=list)
    # 执行轨迹：记录每个被 pipeline 命中的 stage
    _trace: List[str] = field(default_factory=list)
    # VDEV 相关
    io_vdev: Optional[Vdev] = None
    io_vdev_completed: bool = False
    # 子 ZIO（gang/ddt 等按需插入）
    io_children: List["Zio"] = field(default_factory=list)

    def push_transform(self, xform: str) -> None:
        """zio_push_transform(zio, abd, size, psize, transform) 入栈"""
        self.io_transforms.append(xform)
        self._trace.append(f"push:{xform}")

    def pop_transforms(self) -> List[str]:
        """zio_pop_transforms(zio) 出栈（逆序恢复）"""
        out = list(reversed(self.io_transforms))
        self._trace.append(f"pop:{len(out)}")
        self.io_transforms.clear()
        return out


# —— stage handlers 桩：每个 stage 一个可观测回调 ——
STAGE_HANDLERS: Dict[int, Callable[[Zio], None]] = {}


def _register_stages():
    def _h(name: str):
        def fn(zio: Zio) -> None:
            zio._trace.append(name)
            # 模拟部分 stage 的 side-effect
            if name == "ZIO_STAGE_WRITE_COMPRESS":
                if zio.io_data:
                    zio.push_transform(ZioTransform.COMPRESS)
            elif name == "ZIO_STAGE_ENCRYPT":
                if zio.io_data:
                    zio.push_transform(ZioTransform.ENCRYPT)
            elif name == "ZIO_STAGE_CHECKSUM_GENERATE":
                zio.push_transform(ZioTransform.CHECKSUM)
            elif name == "ZIO_STAGE_VDEV_IO_START":
                # VDEV 子流水线 START → 经 vdev_queue_io 落至 leaf
                if zio.io_vdev:
                    zio.io_vdev.queue_io(zio)
                else:
                    zio._trace.append("vdev_queue_io:default")
                    zio.io_vdev_completed = True
            elif name == "ZIO_STAGE_VDEV_IO_DONE":
                zio._trace.append("vdev_io_done")
            elif name == "ZIO_STAGE_VDEV_IO_ASSESS":
                zio._trace.append("vdev_io_assess")
                if zio.io_error == 0:
                    zio._trace.append("checksum_verify" if zio.io_type == ZioType.READ else "io_ok")
        fn.__name__ = name
        return fn

    for stage in ZioStage:
        STAGE_HANDLERS[int(stage)] = _h(stage.name)


_register_stages()


# —— 完整链：zio_create → zio_execute → __zio_execute → vdev_queue_io → leaf vdev ——

def zio_create(
    spa: Optional[str] = None,
    io_type: str = ZioType.WRITE,
    pipeline: Optional[int] = None,
    size: int = 4096,
    offset: int = 0,
    data: Optional[bytes] = None,
    vdev: Optional[Vdev] = None,
) -> Zio:
    """zio_create(..., pipeline) 桩：对应 openzfs/zfs/module/zfs/zio.c:934
    pipeline 未指定时按 io_type 选择默认 ZIO_*_PIPELINE 宏。
    """
    if pipeline is None:
        if io_type == ZioType.READ:
            pipeline = int(ZIO_READ_PIPELINE)
        elif io_type == ZioType.WRITE:
            pipeline = int(ZIO_WRITE_PIPELINE)
        elif io_type == ZioType.FREE:
            pipeline = int(ZIO_FREE_PIPELINE)
        else:
            pipeline = int(ZIO_CLAIM_PIPELINE)
    zio = Zio(
        spa=spa,
        io_type=io_type,
        io_pipeline=int(pipeline),
        io_stage=int(ZioStage.ZIO_STAGE_OPEN),
        io_size=size,
        io_offset=offset,
        io_data=data,
        io_vdev=vdev,
    )
    return zio


def __zio_execute(zio: Zio) -> None:
    """__zio_execute(zio) 桩：对应 openzfs/zfs/module/zfs/zio.c:2428
    核心不变量：while (io_stage < ZIO_STAGE_DONE) 按位推进，仅执行 pipeline 位图中包含的 stage。
    支持按需插入 GANG/DDT/BRT/NOPWRITE/ENCRYPT（桩以 io_children 模拟）。
    """
    # 模拟任务要求：while (io_stage < ZIO_STAGE_DONE) 按位推进
    while zio.io_stage < int(ZioStage.ZIO_STAGE_DONE):
        stage = zio.io_stage
        # 仅当 pipeline 包含该 stage 时执行
        if zio.io_pipeline & stage:
            handler = STAGE_HANDLERS.get(stage)
            if handler:
                handler(zio)
        # 按位推进：1<<n 序列。ZioStage 为 1<<n，保持二进制推进语义
        # 通用推进为 <<=1；若 stage 非 2 幂则兜底取下一最小 2 幂（桩鲁棒）
        if stage & (stage - 1) == 0 and stage != 0:
            zio.io_stage = stage << 1
        else:
            # 非法 stage（桩不应触发）→ 直接跳至下一枚举
            nxt = stage << 1
            # 对齐到最近的 ZioStage 值
            candidates = [int(s) for s in ZioStage if int(s) > stage]
            zio.io_stage = min(candidates) if candidates else int(ZioStage.ZIO_STAGE_DONE) << 1
    # DONE 阶段单独处理（桩：记录 done）
    if zio.io_pipeline & int(ZioStage.ZIO_STAGE_DONE):
        zio._trace.append("ZIO_STAGE_DONE")
    # 模拟 io_done callback：若有 transform 则保持栈供调用方 pop 验证
    zio._trace.append("io_done")


def zio_execute(zio: Zio) -> Zio:
    """zio_execute(zio) 桩：对应 openzfs/zfs/module/zfs/zio.c 2390
    顶层入口，直接委托 __zio_execute。
    """
    zio._trace.append("zio_execute")
    __zio_execute(zio)
    return zio


# —— VDEV 子流水线辅助（对外可测） ——

def vdev_queue_io(zio: Zio, vdev: Optional[Vdev] = None) -> None:
    """vdev_queue_io 桩：经 spa_taskq_dispatch 落至 vdev_queue 的模拟"""
    target = vdev or zio.io_vdev or Vdev(vdev_id=0)
    target.queue_io(zio)


def spa_taskq_dispatch(zio: Zio, taskq: str = "zio_taskq") -> None:
    """spa_taskq_dispatch 桩：模拟 ZIO 四类 taskq 分发（spa.c: spa_taskq_dispatch）"""
    zio._trace.append(f"spa_taskq_dispatch:{taskq}")
    # 桩：同步直接执行
    __zio_execute(zio)


# —— 便民断言接口，供 scaffold 精化后调用 ——

def get_zio_pipeline() -> dict:
    """供测试快速校验 ZIO pipeline 位图与 while 推进不变量"""
    # 校验 enum 1<<n
    for stage in ZioStage:
        v = int(stage)
        assert v & (v - 1) == 0, f"{stage.name} 非 2 幂"
    # 校验 PIPELINE 为位图或
    assert ZIO_WRITE_PIPELINE & int(ZioStage.ZIO_STAGE_WRITE_COMPRESS)
    assert ZIO_WRITE_PIPELINE & int(ZioStage.ZIO_STAGE_VDEV_IO_START)
    assert ZIO_READ_PIPELINE & int(ZioStage.ZIO_STAGE_VDEV_IO_START)
    assert ZIO_READ_PIPELINE & int(ZioStage.ZIO_STAGE_CHECKSUM_VERIFY)
    # 校验 __zio_execute while 推进：写 pipeline 应依次命中 WRITE_COMPRESS/ENCRYPT/VDEV_IO_START/DONE/ASSESS/DONE
    vdev = Vdev(vdev_id=1)
    zio = zio_create(spa="tank", io_type=ZioType.WRITE, data=b"hello", vdev=vdev)
    zio_execute(zio)
    assert "ZIO_STAGE_WRITE_COMPRESS" in zio._trace
    assert "ZIO_STAGE_ENCRYPT" in zio._trace
    assert "ZIO_STAGE_VDEV_IO_START" in zio._trace
    assert "ZIO_STAGE_VDEV_IO_DONE" in zio._trace
    assert "ZIO_STAGE_VDEV_IO_ASSESS" in zio._trace
    assert "ZIO_STAGE_DONE" in zio._trace
    assert zio.io_vdev_completed
    # 校验 transform 栈可逆
    assert ZioTransform.COMPRESS in zio.io_transforms
    popped = zio.pop_transforms()
    assert ZioTransform.COMPRESS in popped
    assert len(zio.io_transforms) == 0
    # 校验完整链 zio_create→zio_execute→__zio_execute→vdev_queue_io→leaf vdev
    assert vdev.completed and vdev.completed[0] is zio
    # 校验读 pipeline
    zio_r = zio_create(spa="tank", io_type=ZioType.READ, vdev=Vdev(vdev_id=2))
    zio_execute(zio_r)
    assert "ZIO_STAGE_READ_BP_INIT" in zio_r._trace
    assert "ZIO_STAGE_VDEV_IO_START" in zio_r._trace
    return {
        "zio_stage_bits": len(list(ZioStage)),
        "write_pipeline": int(ZIO_WRITE_PIPELINE),
        "read_pipeline": int(ZIO_READ_PIPELINE),
        "vdev_dispatch": 1,
        "transform_stack": 1,
    }
