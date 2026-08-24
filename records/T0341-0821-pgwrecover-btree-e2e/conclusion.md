---
schema: pdca.asset/v1
id: T0341-0821-pgwrecover-btree-e2e
phase: check
source_ids: [T0401-commit-37d6bfc, T0401-commit-3a0209b, T0401-commit-1f19507]
---

## 上下文

pgwrecover 的 btree WAL 重放在 T0338-T0400 期间以自造简化实现完成，端到端验证
(T0401)初期暴露 8 处与 PG 官方语义的偏差。按"直接拷贝 PG 源代码逻辑，补充缺失、
删除不要"原则重构：从 PostgreSQL REL_18_STABLE 逐行拷贝 nbtxlog.c/heapam_xlog.c/
bufpage.c/xlogutils.c/nbtdedup.c 等到前端化模块（fe_* 系列），buffer manager 替换为
文件页直读写。验证样本升级为真实 PG18.4 容器负载（合成 WAL 方案因缺少合法段头/CRC
被废弃）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 官方源码前端化可在离线无 buffer manager 环境运行 | ✅ 成立（fe_buffer 层实现 XLogReadBufferForRedo* 全分支语义） |
| 从 checkpoint 起点可从零重建表+索引（文件不存在场景） | ✅ 成立（copy 缺失容忍 + read_page ENOENT 零页） |
| 全操作码负载下恢复产物与 PG 最终态一致 | ✅ 成立（语义级校验器判定，详见分析） |

## 分析

对照任务 PRD（验收标准原为占位）与本任务实际承接的 AC：

- **AC-1** ✅ btree 全部 13 操作码走官方 nbtxlog.c 路径，压力样本(3000行)含
  SPLIT×11/DEDUP×24/VACUUM×17/INSERT_UPPER×11 的索引产物与 PG 真实最终态
  字节级一致（19 页逐字节相同）（tests/fixtures/stress_*，
  test_stress_full_opcodes PASSED）
- **AC-2** ✅ heap 全部操作码走官方 heapam_xlog.c 路径；INSERT×966/UPDATE×1000/
  DELETE×600/VACUUM PRUNE×14 场景下 lp 结构/MVCC 链(xmin,xmax,ctid)/元组数据
  与 PG 最终态完全一致（verify_consistency.py 判定 PASS）
- **AC-3** ✅ SMGR_TRUNCATE 支持：表尾空页裁剪生效，恢复文件大小与 PG 一致
  (25页→19页)；XLogHintBitIsNeeded 按 pg_control.data_checksum_version 判定
  （commit 1f19507）
- **AC-4** ✅ 测试基建 CI 化：3 个 pytest 用例（基础/统计形状/压力全操作码）
  + verify_consistency.py 校验器，真实 WAL fixture bz2 压缩入库，
  `pytest tests/pgwrecover/test_btree_e2e.py` 3 passed

已知边界（非缺陷，PG 设计使然）：
- hint 位(XMIN_COMMITTED 等)/t_cid/pd_prune_xid 不写 WAL，重放产物缺省，
  PG 首次访问自动重建——standby 重放产物同样如此
- VM(fork=2) 位图不输出（仅影响 index-only scan 性能）；visible 记录的
  VM 页位图写入保留结构待完善
- 自由空间碎片字节不同（PageRepairFragmentation 移动残留，无语义）

## 适用边界

- 适用：PG18 及布局兼容版本的单时间线、checkpoint 起点的表+索引数据页恢复
- 不适用：逻辑解码输出（NEW_CID/REWRITE 为 no-op）、VM/FSM 文件重建、
  freeze plan 场景（代码就位但无专门回归样本）
- checksums 关闭的实例行为已兼容（XLogHintBitIsNeeded 动态判定）

## 下一轮建议

1. freeze plan(nplans>0) 专项样本回归（CREATE INDEX CONCURRENTLY 场景易触发）
2. 清理退役的自造 heap 实现（pg_redo.c/pg_redo_heap.c 已不被调用）
3. VM 位图输出可选增强（index-only scan 性能）
