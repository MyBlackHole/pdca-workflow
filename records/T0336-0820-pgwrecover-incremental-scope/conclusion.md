---
schema: pdca.asset/v1
id: T0336-0820-pgwrecover-incremental-scope
phase: check
source_ids: [t0336-unit-scope, t0336-btree-justification, t0336-e2e, t0336-knowledge]
---

## 上下文

T0334（自研离线 WAL 恢复引擎 pgwrecover）遗留三缺口：MULTI_INSERT 增量跳过、
UPDATE prefix/suffix 压缩不重组、btree 增量未论证。本轮 T0336 收口前两项并论证第三项。

## 假设与结果

| AC | 验收标准 | 结果 | 证据 |
|----|---------|------|------|
| AC-1 | MULTI_INSERT 增量重放单测 PASS | **通过** | t0336-unit-scope：test_redo_scope.py 中 MULTI_INSERT 场景重放后 blk2 新页 6 items 与运行库字节级一致 |
| AC-2 | UPDATE prefix/suffix 重放单测 PASS | **通过** | t0336-unit-scope：t0336-prefix(flags 0x20, item1 len=79)/t0336-psuf(flags 0x60, item1 len=1532) 与运行库字节级一致 |
| AC-3 | btree 决策落地（S3b 论证跳过安全） | **通过** | t0336-btree-justification：pgbin 不读 btree fork，跳过不影响 heap→parquet 正确性 |
| AC-4 | 端到端回归 PASS（重放后 parquet 行数一致、增量行 diff=0） | **通过** | t0336-e2e：3 场景容器实证，重放 heap 与运行库字节级一致（较 parquet 行数级更强） |
| AC-5 | 回归不破坏（T0334 既有 5 单测 + e2e 仍 PASS） | **通过** | t0336-unit-scope + t0336-e2e：tests/pgwrecover/ 9 项单测全 PASS |
| AC-6 | 知识沉淀更新（MULTI_INSERT/prefix-suffix/btree 决策要点） | **通过** | t0336-knowledge：t0334-pgwrecover-implementation.md 补充 T0336 章节 |

## 分析

1. **核心修复链**：T0334 的分发掩码 `&~XLOG_HEAP_OPMASK` 使 UPDATE(0x20) 误路由
   redo_heap_insert——这是"UPDATE 后崩溃"的根因，与 T0334 已记录的 tuple 头错位
   （SizeofHeapTupleHeader=23 vs sizeof=24）是两条独立缺陷。本轮一并修复。
2. **MULTI_INSERT 关键认知**：xl_multi_insert_tuple 头 7B ≠ xl_heap_header 5B，
   不能复用 build_tuple（数据错位 2B）。官方按块内偏移顺序写入 tuple，需直接构造。
3. **prefix/suffix 重组对齐官方**：heapam_xlog.c 843-904 行，flags 0x20/0x40 读取
   两段 uint16（WAL 内先后缀后前缀），旧 tuple 取前后缀 + WAL 中间数据。
4. **同页分支 bug**：oldblk==newblk 修改 opage 却写回 npage，旧版本元数据丢失
   （ctid/xmax/cmin 保持备份原样）。这是本轮测试逼出的真实缺陷，修复后与运行库一致。
5. **重放 vs 运行库唯一差异 = 可见性 hint bit**：HEAP_XMIN_COMMITTED(0x100)/
   XMAX_COMMITTED(0x400) 由运行库读取时按 clog 标记；XMAX_INVALID(0x800) 时
   xmax 残留值 1。均不影响可见性（clog 判断），测试屏蔽后字节级一致。
6. **TOAST 对 prefix 压缩的影响**：超阈值文本外联后 PG 只压缩定长列（prefixlen=4）；
   内联文本才触发 0x60。真实场景验证需内联文本。
7. **运行库后续 VACUUM prune 是环境噪音**：旧版本标记 DEAD 不在增量 WAL 内，
   场景对比限定增量新页（blk2）。

## 适用边界

- 仅 PG18（poct25 容器）实证；PG16 及更早的 xl_multi_insert_tuple 布局待验。
- 增量 WAL 覆盖：RM_HEAP INSERT/MULTI_INSERT/UPDATE/HOT_UPDATE/DELETE/LOCK。
- btree 一致性未实现（S3b 论证跳过，已记遗留）。
- clog 需配合提交后 clog 才能看到增量行可见性。

## 下一轮建议

- 遗留：btree 增量重放（若目标升级为"恢复产物可启动 PG"）。
- pgbin 未对齐 varlena 读取崩溃（T0334 遗留，`*(uint32*)vp`）独立修复。
- 扩展验证：PG16 布局差异、多 segment WAL 跨段重放、>8KB TOAST 行。
