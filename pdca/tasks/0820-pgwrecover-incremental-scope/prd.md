# 跟进：pgwrecover 增量重放覆盖扩展（MULTI_INSERT/UPDATE prefix-suffix/btree 增量）

## 问题

T0334 交付的 pgwrecover 离线恢复引擎（src/pg/pg_redo.c 等）增量重放仅覆盖
XLOG_HEAP_INSERT / DELETE / UPDATE / HOT_UPDATE / LOCK 五个 opcode，存在三处已知缺口
（T0334 disposition 明确转出）：

1. **XLOG_HEAP2_MULTI_INSERT（RM_HEAP2）完全未处理**：走 default 跳过，
   `result->skipped_incremental++`。多行单事务批量插入是 VACUUM/COPY/批量 INSERT 的
   常见 WAL 形态，缺口会导致批量插入行在恢复产物中全部缺失。
2. **UPDATE prefix/suffix 压缩（XLH_UPDATE_PREFIX_FROM_OLD / XLH_UPDATE_SUFFIX_FROM_OLD）**：
   当前 redo_heap_update 只处理全量新 tuple；官方 WAL 在 column 更新时可裁剪前后缀，
   重放时需从旧 tuple 复制前后缀 + 中间新增数据重组新 tuple。当前若 WAL 带这些 flag
   会构造错 tuple。
3. **btree 无增量重放**：pg_replay.c 只对 RM_BTREE 做 FPI 落页，增量 XLOG_BTREE_*
   （INSERT/DELETE/SPLIT）跳过。DELETE 场景 btree 页可能悬空（索引指向已删 heap 行），
   但 pgbin 只读 heap 不读 btree，故当前端到端不受影响——此缺口影响的是"恢复产物中
   btree 一致性"这一完整目标。

## 目标

- 补齐 RM_HEAP2 MULTI_INSERT 增量重放（对齐官方 redo_heap_multi_insert 语义）
- 补齐 UPDATE prefix/suffix 压缩重放（对齐官方 XLH_UPDATE_PREFIX/SUFFIX 语义）
- btree 增量：实现 XLOG_BTREE_INSERT / XLOG_BTREE_DELETE / XLOG_BTREE_SPLIT 的
  最小重放（页内 tuple 增删 + 分裂重链），或明确论证跳过不影响 pgbin 转换正确性
- 全部以单元测试 + 端到端验证回归

## 方案方向

### S1: MULTI_INSERT（RM_HEAP2, 必做）
在 pg_redo.c 增加 `redo_heap_multi_insert()`，分发到 `pg_redo_heap_record` 的
RM_HEAP2 分支：
- 结构：`xl_heap_multi_insert`（flags/ntuples/offsets[FLEXIBLE_ARRAY_MEMBER]），
  块 0 数据区为 `xl_multi_insert_tuple` 序列（datalen/t_infomask2/t_infomask/t_hoff
  + tuple 数据，含 4 字节对齐 padding）。
- 对齐官方：`XLOG_HEAP_INIT_PAGE` 时整页还原且无 offsets；否则逐 tuple
  `PageAddItem` 落页。检查 `XLH_INSERT_LAST_IN_MULTI` 与 infomask 处理。
- 追加到 `tests/pgwrecover/` 单元测试（构造 multi_insert WAL 样本）。

### S2: UPDATE prefix/suffix（RM_HEAP, 必做）
在 redo_heap_update 中识别 `XLH_UPDATE_PREFIX_FROM_OLD` /
`XLH_UPDATE_SUFFIX_FROM_OLD`：
- 前缀/后缀为两段 uint16（先后缀后前缀，按官方顺序），从旧 tuple 复制对应
  `prefix_len` / `suffix_len` 字节到新 tuple 前后端，中间为 WAL 内新增数据。
- 与 `XLH_UPDATE_CONTAINS_NEW_TUPLE` 组合逻辑对齐官方。
- 单元测试覆盖带 prefix/suffix 的 UPDATE。

### S3: btree 增量（可做/论证）
（已定 S3b，见方向确认）
- **S3a 实现最小增量**：XLOG_BTREE_INSERT / DELETE / SPLIT 重放。
- **S3b 论证跳过安全**：证明 btree 增量跳过不影响 heap→parquet 转换正确性
  （pgbin 不读 btree），将 btree 一致性列为后续独立任务。
已定：S3b 论证跳过安全（用户确认）。

## 验收标准

- [ ] AC-1: MULTI_INSERT 增量重放单元测试 PASS：构造含 ntuples=2 的
  XLOG_HEAP2_MULTI_INSERT 记录样本，重放后目标页出现全部 tuple（offsets 正确、
  infomask/t_hoff 正确），`skipped_incremental` 不再增加
- [ ] AC-2: UPDATE prefix/suffix 重放单元测试 PASS：构造带 XLH_UPDATE_PREFIX/
  SUFFIX_FROM_OLD flag 的 UPDATE 记录，重放后新 tuple 的前后缀来自旧 tuple、
  中间为新增数据（字节级比对）
- [ ] AC-3: btree 决策落地：S3a 实现 btree INSERT/DELETE/SPLIT 增量重放（含
  单元测试）；或 S3b 记录论证（btree 增量跳过不影响 pgbin heap 转换正确性，
  决策记录到 prd/clarifications）
- [ ] AC-4: 端到端回归 PASS：复用 T0334 的容器备份样本（含批量多行 INSERT +
  UPDATE），重放后 parquet 行数与 SQL 全量一致、增量行逐字段 diff=0
- [ ] AC-5: 回归不破坏：T0334 既有 5 个单元测试 + e2e（单行 INSERT 场景）
  全部仍 PASS
- [ ] AC-6: 知识沉淀更新：pgwrecover-implementation.md 补充 MULTI_INSERT /
  prefix-suffix / btree 决策要点 + evidence 登记 + 结论

## Seam 分析

### 声明的测试接缝
- seam: tests/pgwrecover/test_redo_scope.py -> src/pg/pg_redo.c
- seam: tests/pgwrecover/test_replay.py -> src/pg/pg_replay.c
- seam: tests/pgwrecover/test_pg_control.py -> src/pg/pg_control_reader.c
- seam: tests/pgwrecover/test_wal_reader.py -> src/pg/wal_reader.c

## 范围外

- gin/gist/spgist/seq/logical 等其他 rmgr 增量重放
- PITR 时间点恢复、wal_level=minimal（无 FPI）备份
- MySQL 恢复引擎实现
- 真实生产备份产物（环境无样本，用容器构造，沿用 T0334 基线）

## 备注

- 依赖 T0334 知识：`knowledge/pg/pgwrecover-implementation.md`
- MULTI_INSERT/prefix-suffix 官方结构定义见
  `third_party/pg184/include/access/heapam_xlog.h`
- btree 决策 S3a/S3b 在 P2 Grill 时向用户展示取舍