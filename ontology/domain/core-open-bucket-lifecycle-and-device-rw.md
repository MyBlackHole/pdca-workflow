---
schema: pdca.asset/v1
id: ontology:domain/core-open-bucket-lifecycle-and-device-rw
type: domain
layer: Knowledge
status: active
summary: open bucket 生命周期与设备 rw 初始化
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 open-bucket-lifecycle-and-device-rw 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# open bucket 生命周期与设备 rw 初始化

来源：T0192-0802-open-bucket-lifecycle-device-rw（bcachefs 风格 Rust 存储引擎
open bucket 生命周期收尾）。

## 上下文与约束

T0189 引入 open_buckets/rw_devs 守卫后遗留：rw_devs 硬编码 `[0]`、open/close
未配对静默容忍、设备下线无守卫。上游 bcachefs 的 open bucket 有明确生命周期
终点：fs 只读/销毁时 `bch2_open_buckets_stop`（fs.c:324，foreground.c:1171-1230）
关闭全部 open buckets；设备上线/下线走 `bch2_dev_allocator_add`/`set_rw`/`remove`
（background.c:1663-1728）。engine-local 约束：无真实设备 I/O，drop 为显式
生命周期终点，devs_online 位图为设备集合事实源。

## 假设与行动

- **生命周期终点语义**：`Drop for EngineState` 在 worker join + rcu barrier 后、
  free_super 前校验 open_buckets 非空即 panic（对齐 umount 关闭语义与 BUG_ON
  风格）——open 桶不允许"永开"状态，未配对 close 是调用方泄漏。
- **rw_devs 按 devs_online 推导**：attach_persistent_journal 配置 members 后按
  devs_online 位图清除重建 rw_devs（对齐 `bch2_dev_allocator_add` 上线即
  set_rw(true)，members.h:134-135 for_each_rw_member_rcu 语义），不硬编码设备号。
- **设备下线拒绝**：`set_device_rw(dev,false)` 时该设备仍有 open 桶返回 -16
  （对齐 `bch2_dev_allocator_remove` 先置 ro、`bch2_open_buckets_stop`、再等待
  open write point 清空 background.c:1650-1722 的非阻塞等价）。
- **锁序统一**：open_buckets → rw_devs，与 reclaim/discard 一致；任何守卫新增
  锁必须核对既有锁序，防止并发死锁。

## 结果与证据

- AC-1..AC-6 全部通过：3 新定向测试（drop 泄漏 panic 消息断言 / rw_devs 初始
  推导断言 / 设备下线拒绝）+ 205 lib + 10 集成 + fmt 全绿，单文件 +169/-3。
- 审查发现并修复：初版 set_device_rw 锁序 rw_devs→open_buckets 与
  reclaim/discard 相反构成死锁，修正后复测全绿。
- 既有测试适配：T0189 属性测试 restart/结束 drop 前未 close open 桶，被新
  drop 语义正确暴露，补充 close 循环后通过。

## 成功原因

- 生命周期终点语义（drop 校验）与上游 umount 关闭语义一一对应，泄漏在开发期
  即暴露而非静默。
- 初始化数据源用 devs_online（设备集合事实源）而非硬编码，未来多设备无需改
  rw_devs 初始化逻辑。
- 设备下线拒绝复用 -16（live reference 类），与 reclaim 守卫同码，调用方可
  区分硬失败与轮转。
- 锁序统一在审查阶段通过双轴清单发现并修复，避免并发死锁进入主线。

## 适用与不适用条件

- 适用：显式生命周期终点（drop/close）、设备集合位图为事实源、非阻塞拒绝
  表达等待语义、catch_unwind 断言 panic 消息。
- 不适用：真实设备热插拔/故障、I/O 中段撤销 open 的并发撤销语义、多设备
  I/O 调度（engine-local 单设备，推导路径仅 dev 0 覆盖）。
- drop panic 不可恢复（release 相同）：面向测试与配对契约，panic 路径
  free_super 不执行，资源由 OS 回收。

## 下一轮建议

- 引入多设备拓扑时补多设备成员定向测试（推导路径当前仅 dev 0 覆盖）。
- 「open/not_rw 桶不转 free」「drop 无泄漏」不变量可提升为公开断言工具，
  与 T0189/T0191 建议合并为 worker 守卫断言套件。
