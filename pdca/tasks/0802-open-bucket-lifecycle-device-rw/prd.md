# T0192 open bucket 生命周期：drop 泄漏检测与 rw_devs 按 sb 初始化

## 问题陈述

T0189 引入了 open_buckets/rw_devs 守卫，但 `rw_devs` 初始化为硬编码 `[0]`
（engine.rs:494），open/close 未配对时引擎静默容忍（无泄漏检测）。本地 bcachefs
在 fs 只读/销毁路径调用 `bch2_open_buckets_stop`（fs.c:324，foreground.c:1171）
关闭全部 open buckets，设备上线/下线分别走 `bch2_dev_allocator_add`/
`set_rw`（background.c:1663-1728）维护 rw_devs 位图。

## 目标

对齐 bcachefs open bucket 生命周期语义：drop 引擎时检测未配对 open bucket
（泄漏），rw_devs 初始状态按 sb members/devs_online 推导，并验证设备下线
（set_device_rw false）时 open 桶语义与上游一致。

## 验收标准

- [ ] AC-1: 修改前逐段记录 `bch2_open_buckets_stop`、`bch2_dev_allocator_add`/`set_rw`/`remove` 源码锚点。
- [ ] AC-2: `StorageEngine::drop` 时 open_buckets 非空 panic（对应 umount `bch2_open_buckets_stop` 关闭语义与 BUG_ON 风格）；close 配对后 drop 正常，定向测试用 should_panic 验证。
- [ ] AC-3: rw_devs 初始集合由 sb members/devs_online 推导，移除 [0] 硬编码；初始化与 allocate/reclaim/discard 守卫一致。
- [ ] AC-4: `set_device_rw(dev, false)` 时若该设备仍有 open bucket 返回 -16 拒绝下线（对应上游 remove 先 set_rw(false) 再等 open write point 清空的非阻塞等价，与 reclaim/discard 守卫同码）。
- [ ] AC-5: deterministic 定向测试 + 属性模型扩展（open 未配对不得随 drop 静默丢失）。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- engine-local：drop 泄漏检测用计数器或 drop 时校验（不引入真实设备 I/O）。
- rw_devs 初始化复用 `bch2_sb_member_get` 与 devs_online 遍历，与既有几何消费逻辑一致。
- 不实现真实设备热插拔/故障、多设备 I/O 调度。

## 范围外

真实 block-device I/O、设备热插拔事件、跨设备迁移、GC/LRU、VFS。

## 备注

前置：T0189 已归档；本任务承接其 disposition 登记的两项 LOW 技术债。
