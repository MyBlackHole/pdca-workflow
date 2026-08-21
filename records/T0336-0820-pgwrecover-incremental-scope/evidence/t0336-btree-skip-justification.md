# T0336 S3b — btree 增量跳过安全论证

> 来源：T0336-0820-pgwrecover-incremental-scope（容器实证 PG18）
> 决策：S3b 论证跳过安全（用户已确认），btree 一致性列为后续独立任务。
> 关联：prd.md AC-3；实现见 `src/pg/pg_replay.c` 增量分派逻辑。

## 结论

**btree 增量跳过不影响 heap → parquet 转换正确性**。pgbin 数据链路不消费
btree（只读表堆），恢复产物中的索引不一致不进入转换结果。

## 当前行为（pg_replay.c）

| btree WAL 记录 | 处理 |
|---------------|------|
| 含 FPI 的页 | `RestoreBlockImage` 还原整页（备份后凡有全页镜像的索引页均复原） |
| 无 FPI 的增量块（XLOG_BTREE_INSERT/DELETE/SPLIT） | 跳过，计入 `skipped_incremental`，不落页 |

增量分派仅在 `rmid == RM_HEAP_ID || rmid == RM_HEAP2_ID` 时调用
`pg_redo_heap_record`，btree 记录即使带无 FPI 的增量块也不会进入增量重放器。

## 为什么安全（论证链）

1. **数据链路**：pgbin 转换只读表堆（`pg_heap_reader.c`），表定义来自
   pg_class/pg_attribute（分类目录），**全程不读取任何索引 fork**。
   索引是 heap 行的冗余加速结构，不承载业务数据。

2. **恢复目标对齐**：T0333/T0334 的恢复目标是"离线重放备份 + 增量，
   输出等价 heap 供 parquet 转换"。索引一致性不在该目标内。

3. **heap 完整性不受索引影响**：btree 增量跳过不影响 heap 页的 FPI/增量重放
   （两套 fork 相互独立）。若某索引页在恢复点前有 FPI，该页仍被还原为
   "恢复点之前最后一次全页镜像"的状态；其余索引页保持备份时点状态。
   可能出现的"索引指向已删 heap 行"（悬空）只会影响 PG 的索引扫描路径，
   pgbin 全表扫描路径不触发。

4. **代价收益**：XLOG_BTREE_INSERT/DELETE/SPLIT 重放需实现完整的 btree
   页结构操作（页分裂、兄弟/父指针链维护、item 位移、唯一约束检查），
   复杂度远超 heap 的顺序追加型重放；而当前目标的收益为零
   （转换结果不依赖索引）。投入产出不成立。

## 遗留影响（后续独立任务）

若目标升级为"恢复产物可直接启动 PG 查询"，btree 增量重放为必做项，
需覆盖：
- XLOG_BTREE_INSERT（含 split 的向右传播）
- XLOG_BTREE_DELETE（含 mark/unmark dead）
- XLOG_BTREE_SPLIT / GIN / GIST 等扩展索引 fork

此决策已记录到任务 prd/clarifications。