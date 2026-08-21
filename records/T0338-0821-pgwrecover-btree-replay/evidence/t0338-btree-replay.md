# T0338 pgwrecover btree 增量重放（多 fork 架构 + 核心 WAL 类型）

> 来源：T0338-0821-pgwrecover-btree-replay
> 编译：bash scripts/build_pgwrecover.sh 通过

## 实现内容

### S1: 多 fork 架构

1. **pg_replay.h**：ReplayTarget 新增 `index_dir` 字段
2. **pg_replay.c**：FPI 路由按 forkNum 分流（heap=0, index>=3）
3. **pgwrecover.cpp**：新增 `--out-index=DIR` 参数 + `copy_index()` 复制 btree fork 文件
4. **pg_redo.h**：新增 `pg_redo_btree_record()` 声明

### S2: btree WAL 重放

**pg_redo_btree.c**（600+ 行）实现 5 种核心 WAL 类型：

| WAL 类型 | 实现状态 | 说明 |
|----------|---------|------|
| INSERT_LEAF | **已实现** | 解析 xl_btree_insert + IndexTuple，插入叶页 |
| DELETE | **已实现** | 解析 xl_btree_delete，标记 LP_DEAD |
| SPLIT_L/R | **已实现** | 重建左右页，设置 BTPageOpaque |
| NEWROOT | **已实现** | 创建根页，设置 BTP_ROOT 标志 |
| 其他 10 种 | 跳过 | VACUUM/UNLINK/DEDUP 等 P1/P2 类型 |

**关键实现**：
- 页操作原语：`page_init()`、`page_add_item()`、`page_set_lsn()`、`read_page()`、`write_page()`
- 自定义 BTPageOpaque/IndexTuple 类型（避免 nbtree.h 重依赖链）
- 幂等检查：页 LSN >= 记录 LSN 时跳过
- 页缺失时零初始化（对齐 XLOG_BTREE_INIT_PAGE）

## 待验证

- 需要真实 btree WAL 样本进行端到端验证（当前仅编译通过）
- SPLIT 的 IndexTuple 解析为简化实现（直接复制 WAL 数据，未完整重建）
- DELETE 的 posting list 更新未实现（仅标记 LP_DEAD）
