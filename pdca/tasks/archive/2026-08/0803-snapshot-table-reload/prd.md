# T0209 PRD：快照表启动重建（对齐 bch2_snapshots_read）

## 背景

T0208 后对 btree 核心做完整性盘点（对照本地 bcachefs `fs/btree/` 与
`fs/snapshots/`），确认三处缺口，其中"snapshot 遍历语义"经验证：
**iter 侧完整**（`bch2_btree_iter_peek_max` filter_snapshots 六步流程
对齐 iter.c:2808-2900：out_of_range → `p.snapshot < iter.snapshot`
快路径 → update_path 释放 → intent 缓存 update_path → **ancestor 过滤**
→ whiteout），但**快照表生命周期不完整**：

- `bch_fs.snapshots.table` 只由事务提交时的 trigger
  （`bch2_mark_snapshot`，snapshot.rs:475）填充；
- **无启动/恢复时从快照 btree 反向遍历重建内存表**（上游对应
  `bch2_snapshots_read`，snapshot.c:783-806：`for_each_btree_key_reverse`
  遍历 + `__bch2_mark_snapshot(trans, id, 0, null, k, 0)` + 
  `bch2_check_snapshot_needs_deletion` 统计空内部节点）。
- 后果：崩溃重开后表为空 → `bch2_snapshot_is_ancestor` 查表全 false
  → filter_snapshots 会把所有带 snapshot 的 key 过滤掉。
- **当前未暴露**是因为 engine 层遍历全部用 `BTREE_ITER_all_snapshots`
  规避（engine.rs:2419-2427 注释明言 "must enumerate all snapshots"）
  ——这是规避而非实现，快照子树可见性语义（ancestor 过滤）从未在
  重开后真实生效。

另确认：域内无 `BTREE_ID_snapshots`（域内自有 9 个 btree id，约束 14
豁免编号），快照键 `KEY_TYPE_snapshot`（type=22）经任意 id 的事务写入，
trigger 按 key type 分发（update.rs:1989/2708/3141）。快照树 id 归属为
域内实现决策。

## 目标

重开/恢复后快照表从磁盘键重建（对齐 `bch2_snapshots_read` 的反向遍历
顺序与 mark 调用形式），ancestor 查询与 filter_snapshots 语义在重开后
真实可用；不再依赖 all_snapshots 规避。

## 验收标准（AC）

- [ ] **AC-1 重开加载**：`open_persistent`（engine.rs:566）成功后自动
  执行快照表重建：反向遍历快照树键（POS_MAX 起，对齐
  `for_each_btree_key_reverse`），每个 `KEY_TYPE_snapshot` 键经
  mark 路径重建 `snapshot_t`（parent/children/tree/subvol/depth/skip/
  state/is_ancestor bitmap）；重建后表内容与崩溃前一致（逐字段断言，
  含 is_ancestor bitmap 按 id 序构建）。
- [ ] **AC-2 ancestor 语义重开可用**：重开后非 all_snapshots 迭代的
  filter_snapshots 正确生效：快照子树内 key 可见、跨分支 key 被跳过
  （对齐 iter.c:2874 `bch2_snapshot_is_ancestor` 分支）；重开前后同一
  快照树的可见 key 集合一致。
- [ ] **AC-3 端到端一致性**：多层快照树（root→child→leaf，含 skip 字段
  与 IS_ANCESTOR_BITMAP 内/外 id 距离）写入 → drop（崩溃）→ 重开 →
  表重建正确；重开后继续写快照键（mark 追加/替换）与表一致；无快照键
  的旧镜像加载为空表（幂等）。
- [ ] **AC-4 门禁**：全量 `cargo test --lib`（247+ 测试，<1min，约束 9）
  + `cargo fmt --check` + diff gate 干净。

## 对齐依据（约束 1/3/10）

| 域内行为 | bcachefs 对应（本地源码） |
|---------|--------------------------|
| 反向遍历 + mark 重建表 | `bch2_snapshots_read`（snapshot.c:783-806：`for_each_btree_key_reverse(trans, iter, BTREE_ID_snapshots, POS_MAX, 0, k, ...)`，注释明言 bitmap 需祖先先初始化故反向） |
| 裸 key 调 mark | `__bch2_mark_snapshot(trans, btree, level, old, new, flags)`（snapshot.c:490，static 6 参低层版；801 行加载调用 `__bch2_mark_snapshot(trans, BTREE_ID_snapshots, 0, bkey_s_c_null, k, 0)`） |
| trigger 包装 | `bch2_mark_snapshot(trans, op)`（snapshot.c:558，域内 snapshot.rs:475 已有，加载时以 `op{old:null, new:k}` 复用） |
| 表锁 | `guard(mutex)(&c->snapshots.table_lock)`（snapshot.c:497，域内 snapshot.rs:481 已有） |
| 空内部节点统计 | `bch2_check_snapshot_needs_deletion`（snapshot.c:802，域内保留计数与日志，回收动作范围外） |
| ancestor 过滤 | `btree_iter_filter_snapshots`（iter.c:2808-2900，域内 iter.rs:2062-2152 已对齐，待重开验证） |
| WILL_DELETE flag | `__bch2_mark_snapshot` 中 `BCH_SNAPSHOT_WILL_DELETE` → `BCH_FS_need_delete_dead_snapshots`（snapshot.rs:522 已有，加载时同样设置） |

快照树 btree id 归属为域内自有方案（约束 14 豁免），但遍历顺序与
mark 调用形式严格照搬上游。

## 实现决策（草案）

- 域内快照树 id 归属：engine 层现有测试将 `KEY_TYPE_snapshot` 键写入
  id 0（snapshot.rs 单测）；决策为域内固定"快照树 = 遍历所有 live
  btrees 收集 KEY_TYPE_snapshot 键"（等价上游遍历专属树全部键，且不
  引入新 btree id），或按实测成本收敛为固定 id。实现开始时对照
  engine 层快照键写入路径再定。
- 触发时机：`open_persistent` 成功后、首次读操作前（对齐上游
  `bch2_snapshots_read` 在 go_rw 前执行）。
- 表重建用现有 `bch2_mark_snapshot(trans, op)` 以 `op{old:null,
  new:k, flags:0}` 复用（不新增函数，约束 8）。
- 反向遍历：`bch2_btree_iter_peek_prev` + `bch2_btree_iter_advance`
  （snapshot.rs `__bch2_get_snapshot_overwrites` 已示范同模式）。
- 测试：engine.rs 端到端（三层快照树 + drop + 重开 + 表逐字段断言 +
  重开前后可见 key 集合一致 + 继续写入），snapshot.rs 单测补充
  空表幂等与 WILL_DELETE 加载。
- 死快照删除（`bch2_delete_dead_snapshots_work`）范围外，仅保留
  `bch2_check_snapshot_needs_deletion` 计数语义与日志。

## 范围外

- 死快照删除/回收（delete_dead_snapshots_work 大块逻辑）。
- key_cache / write_buffer（性能层）。
- 不新增 engine API、不新增 btree id。
- fs 层兼容（AGENTS.md 范围外）。

## 风险

- 域内快照键可能分散在多个 btree（无专属树）→ 遍历范围决策需在
  实现开始时与既有写入路径核对，避免漏扫。
- 反向遍历在表为空时的行为（peek_prev 全空）需幂等。
- 表重建与并发事务 mark 的互斥（table_lock 已存在，对齐上游
  guard(mutex) 顺序）。
- 现有持久化镜像（T0201+ 积累）大多无快照键 → 空表加载必须幂等，
  不得破坏既有 247 测试。
