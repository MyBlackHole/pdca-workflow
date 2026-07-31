---
schema: pdca.asset/v1
id: R0143
phase: check
source_ids: [E0143-crash-analysis, convergence-map]
---

## 上下文

内核 3.10.0-1160.83.1.el7 (x86_64) 运行在 WOQU R6900 G5 (192 CPU, 1024 GB)，崩溃于 uptime 805 天时 dm-multipath 设备的 blk-mq I/O 完成路径。此前轮次 (R0142) 被用户判定为 rejected，本次为深入追查。

## 假设与结果

| 假设 | 结果 | 说明 |
|------|------|------|
| tio->ti 悬空指针是 use-after-free | 确认 | `rd` 确认地址未映射 (PTE=0) |
| 释放源是 dm 表重载 | 确认 | `immutable_target` 无保护 + `dm_sync_table` 不足 |
| 触发事件是 SCSI 热添加 | 确认 | dmesg 显示崩溃前 ~45s 有 sdg/sdi 接入 |
| 非其他 CPU 并发竞争 | 确认 | bt -a 显示 CPU 137 idle 无竞争者 |
| 非硬件损坏 | 确认 | PTE=0 而非位翻转 |

## 分析

根因链完整建立:

```
SCSI hot-add (sdg/sdi @ [69474366])
  → multipathd 检测新路径
    → DM_TABLE_LOAD ioctl → __bind() 表重载
      → synchronize_srcu + synchronize_rcu_expedited (只等 md->map 读者)
      → dm_table_destroy(old_map) → 旧 dm_target 被 kfree
  ── 同时 ──
  dm_mq_queue_rq: tio->ti = md->immutable_target (无保护/引用)
  → I/O 完成 → dm_softirq_done → dm_done
    → tio->ti->type → CRASH (ffffffbd16abacc048 PTE=0)
```

上游修复搜索:
- **CVE-2026-43278** (2026-05): 同路径 (dm_softirq_done/dm_done) bio 指针残留修复
- **Libo Chen patch** (2026-03): `dm_mq_queue_rq` vs `__dm_destroy` 竞争修复
- 无单一 CVE 精确匹配 `tio->ti` 悬空指针问题 — 这是 RHEL 7 (3.10) `immutable_target` 优化特有的设计缺陷

## 适用边界

- 仅影响 dm-multipath + blk-mq 组合模式 (use_blk_mq=true)
- 仅发生在表重载 (dmsetup reload/resume) 与 in-flight I/O 完成重叠的时间窗
- RHEL 7.9 (3.10.0-1160.83.1.el7) 特有；上游 >4.x 通过 `DMF_BLOCK_IO_FOR_SUSPEND` + `blk_mq_quiesce_queue` 缓解

## 下一轮建议

1. 升级内核到包含 CVE-2026-43278 修复的最新 RHEL 7.z 版本
2. 若无法升级，考虑限制 SCSI LUN 热添加期间的 dm 操作并发度
3. 将此根因模式记录到知识库，供后续类似 crash dump 分析参考
