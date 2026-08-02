# T0192 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0189

## 本地源码核验

- `fs/alloc/foreground.c:1171-1230`：`bch2_open_buckets_stop` 在 fs 只读/销毁路径
  关闭全部 open buckets（`fs.c:324` umount 时调用），设备下线时先 `set_rw(false)`
  再停设备 open buckets（`background.c:1690-1702` `bch2_dev_allocator_remove`），
  并等待 `!bch2_dev_has_open_write_point`（foreground.c:1644-1662）。
- `fs/alloc/background.c:1663-1689`：`bch2_dev_allocator_set_rw` 按成员
  data_allowed/durability 更新 rw_devs 位图；`bch2_dev_allocator_add`（1723-1728）
  设备上线时置 rw。

## 查重

T0189 的 disposition 已登记两项 LOW 技术债（rw_devs 初始 [0] 硬编码、open/close
配对泄漏检测）并明确"留待多设备/真实 I/O 任务"。T0189/T0190/T0191 已覆盖守卫、
inflight 去重与 FIFO 公平性；open bucket 生命周期（drop 泄漏检测）与 rw_devs
按 sb 初始化未实现，无同范围活动任务。

## 推荐

承接 T0189 技术债：① `StorageEngine::drop` 时校验 open_buckets 为空（对应
`bch2_open_buckets_stop` 的 fs 只读/销毁关闭语义），未配对 close 视为泄漏；
② `rw_devs` 初始化从 sb members/devs_online 推导（对应 `bch2_dev_allocator_add`
语义），移除 [0] 硬编码。两者均为守卫基线收尾，不引入真实设备 I/O。
