# pgwrecover btree 增量重放（多 fork 架构 + 核心 WAL 类型）

> parent: T0337
> 场景：development
> 调研来源：T0337 S2 调研（15 种 WAL 类型、BTPageOpaque/IndexTuple 结构）

## 问题陈述

T0334/T0336 完成后，pgwrecover 只输出单个 heap 文件。btree 索引 WAL 记录
（INSERT_LEAF/DELETE/SPLIT 等）全部跳过。若目标升级为"恢复产物可启动 PG 查询"，
必须：
1. 扩展架构支持多 fork 文件（heap + btree index）
2. 实现核心 btree WAL 类型的增量重放

## S1: 多 fork 架构（前置）

### 当前限制

- `pgwrecover` 只接受 `--rel-oid`，输出单个 `out_heap` 文件
- WAL 记录中的 `RelFileLocator.forkNum` 区分主 fork(0)/fsm(1)/vm(2)/btree(3+)
- 当前 btree FPI 被错误写入 heap 文件（应写入 btree fork 文件）

### 设计

新增 `--out-index` 参数（可选），指定 btree 索引输出目录。
- 不指定：保持当前行为（仅 heap，btree 跳过）
- 指定：自动从备份复制 btree fork 文件，WAL 记录按 `forkNum` 路由

路由表：
| forkNum | 文件后缀 | 输出路径 |
|---------|---------|---------|
| MAIN_FORKNUM (0) | 无 | out_heap（已有） |
| FSM_FORKNUM (1) | .1 | 跳过（pgbin 不用） |
| VISIBILITYMAP_FORKNUM (2) | .2 | 跳过 |
| >=3（btree/GIN/GiST） | .{forkNum} | out_index/relfilenode.{forkNum} |

## S2: 核心 btree WAL 重放（P0）

### 范围

| WAL 类型 | 操作 | 难度 |
|----------|------|------|
| INSERT_LEAF | 叶页插入 IndexTuple | 低 |
| DELETE | 标记 LP_DEAD + posting 更新 | 中 |
| SPLIT_L | 页分裂（新项在左页） | 极高 |
| SPLIT_R | 页分裂（新项在右页） | 极高 |
| NEWROOT | 创建新根页 | 中 |

### 关键技术点

1. **BTPageOpaque**：btree 页尾部 16 字节（btpo_prev/next/level/flags/cycleid）
2. **IndexTuple**：`t_info` 编码长度（低 13 位），`IndexTupleSize()` 宏
3. **从 scratch 重建**：SPLIT 需 `_bt_restore_page()` 逻辑（重建右页+重组左页）
4. **多块协调**：SPLIT 涉及 4 块（blk0-3），需分别读写不同 fork 文件

## 验收标准

- [ ] AC-1: `--out-index` 指定时，btree fork 文件从备份正确复制
- [ ] AC-2: btree FPI 记录正确写入 btree fork 文件（不污染 heap）
- [ ] AC-3: 不指定 `--out-index` 时行为不变（向后兼容）
- [ ] AC-4: INSERT_LEAF 重放单元测试（构造 btree WAL 样本，重放后叶页内容一致）
- [ ] AC-5: DELETE 重放单元测试（标记 LP_DEAD 后行指针正确）
- [ ] AC-6: SPLIT_L/R 重放单元测试（分裂后左右页内容+邻居链正确）
- [ ] AC-7: 回归不破坏：T0334+T0336+T0337 既有单测仍 PASS

## Seam 分析

### 声明的测试接缝
- tests/test_pg_replay.py -> src/pg/pg_replay.c
- tests/test_pg_redo.py -> src/pg/pg_redo.c
- tests/test_pgwrecover.py -> src/pg/pgwrecover.cpp

## 不做的项

- VACUUM/MARK_HALFDEAD/UNLINK_PAGE（P1，后续任务）
- INSERT_UPPER/INSERT_META/DEDUP/META_CLEANUP（P2，边界场景）
- REUSE_PAGE（仅 Hot Standby，pgwrecover 不需要）
- GIN/GiST/spgist 索引（非 btree）
