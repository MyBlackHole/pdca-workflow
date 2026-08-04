# Convergence Map — T0143 vmcore-deep

## 根因结论

**dm-multipath 表重载与 blk-mq I/O 完成之间的竞争条件导致 `struct dm_target` 的 use-after-free。**

崩溃时 `tio->ti` 指向一块已被释放回页分配器的内存（`ffffbd16abacc040`），而当前有效的 dm_target 位于 `ffffbd16abbd2040`。两者在同一物理内存区域，但 `tio->ti` 指向的是旧表的目标，该目标在表重载时被释放。

## 触发链

```
SCSI LUN 热添加 (Actifio)
    → multipathd 触发 dmsetup reload + resume
        → dm_swap_table() / __bind() 设置新目标
        → dm_sync_table() 同步 SRCU/RCU 读者
        → dm_table_destroy(old_map) 释放旧目标
            → tio->ti 成为悬空指针
                → dm_done() 访问 tio->ti->type
                    → CRASH
```

## 证据一致性检查

| 证据 | 状态 | 说明 |
|------|--------|------|
| 崩溃 RIP 匹配 dm-rq.c:361 | ✅ | `tio->ti->type` 解引用 |
| CR2 = ffffbd16abacc048 | ✅ | `ti + offsetof(type)` = 8 字节 |
| tio->ti = ffffbd16abacc040 无效 | ✅ | `rd` 返回 invalid KVADDR |
| 当前目标有效 | ✅ | 0xffffbd16abbd2040 可读且匹配 dm_table |
| dm 名称 = 253:19 | ✅ | mapped_device 匹配 |
| 类型 = multipath (dm_multipath) | ✅ | 0xffffffffc17f8040 符号已解析 |
| SCSI 热添加时间窗 | ✅ | ~45 秒前（[69474366] vs [69474411]） |
| use_blk_mq = true | ✅ | blk-mq 路径 |
| 栈中无 dm 其他线程竞争 | ✅ | CPU 137 idle，softirq 上下文 |

## 根本原因

`dm_mq_queue_rq()` (`dm-rq.c:895`) 在 I/O 提交时通过 `md->immutable_target` 保存 `tio->ti`，该指针 **无引用计数**。当 `__bind()` 进行表重载后，旧表中的目标被释放，`tio->ti` 成为悬空指针。`dm_sync_table()` 仅同步 `md->map` 的 RCU/SRCU 读者，但 `tio->ti` 的引用不受该同步保护。

## 更新建议

- 升级内核到包含 dm 表重载修复的 RHEL 7 补丁版本
- 或限制 SCSI LUN 热添加期间的并发的 dm 操作
- 或添加对 `tio->ti` 的引用计数保护
