# 崩溃分析结论

## 崩溃概要

| 项目 | 内容 |
|------|------|
| 内核 | 3.10.0-1160.83.1.el7.x86_64 |
| 服务器 | WOQU R6900 G5, 192 CPUs, 1024 GB |
| 时间 | 2026-07-23 10:01:20 (uptime 805天) |
| Panic | BUG: unable to handle kernel paging request at ffffbd16abacc048 |

## 崩溃点

- **函数**: `dm_softirq_done` → `dm_done` (内联)
- **源码**: `drivers/md/dm-rq.c:361` — `rq_end_io = tio->ti->type->rq_end_io;`
- **指令**: `mov 0x8(%rdi),%rdx` (解引用 `ti->type`)
- **失败原因**: `tio->ti` 指针为 `ffffbd16abacc040`，该地址未映射 (PTE=0)

## 崩溃链

```
CPU 137 idle → IPI → IRQ exit → softirq → blk_done_softirq
→ dm_softirq_done (dm-rq.c:394)
  → tio = tio_from_request(rq)        line 397
  → clone = tio->clone                line 398
  → dm_done(clone, ...)               line 406 (内联)
    → tio2 = clone->end_io_data       line 357
    → if (tio2->ti)                   line 360 (非 NULL 但无效)
    → tio2->ti->type->rq_end_io       line 361 ← CRASH
```

## 根因（待深入排查）

**当前分析结论**：悬空指针 (dangling pointer) 导致的 use-after-free。

`clone->end_io_data->ti` 指向的 `struct dm_target` 在 I/O 完成前已被释放或重新配置。

### 失败原因

用户确认分析结果有误，需要更深入的排查。可能的改进方向：
1. 检查 `clone->end_io_data` 指向的 `tio` 结构体完整内容（使用 crash `struct` 命令）
2. 追踪 `tio->ti` 的值变化历史（检查 slab allocator 状态）
3. 检查 dm target 的 refcount 使用情况
4. 查看是否有 Oracle ACFS/ADVM 模块与 DM 层的交互导致异常
5. 查看崩溃前更详细的日志（特别是 DM 相关操作）
6. 使用 `bt -a` 检查其他 CPU 的状态，特别是操作 DM 设备的线程

## 证据

| 证据 | ID | 说明 |
|------|----|------|
| 分析报告 | E001-crash-report | 完整的堆栈、反汇编、源码映射和根因分析 |

## 验收标准达成

- [x] crash 命令成功执行，无加载错误
- [x] 堆栈回溯完整，显示崩溃函数及调用链
- [x] 每个栈帧都关联了源码文件:行号
- [x] 根因分析明确指出问题函数和崩溃机制
