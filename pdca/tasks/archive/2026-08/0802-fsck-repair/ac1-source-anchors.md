# T0198 AC-1 上游锚点记录

## fix_errors 门控（修复语义的唯一裁决点）

- `fs/init/error.c:433-463` `bch2_fsck_err_opt`：按 `c->opts.fix_errors`
  分支——`FSCK_FIX_exit` → 返回 `fsck_errors_not_fixed`（不修）；
  `FSCK_FIX_yes` 且带 `FSCK_CAN_FIX` → 返回 `fsck_fix`（执行修复）；
  `FSCK_FIX_no` → `fsck_ignore`；`FSCK_FIX_ask` → `fsck_ask`/`fsck_fix`
  （AUTOFIX）。
- 选项枚举 `fs/opts.h:132` `FSCK_FIX_##t`（exit/yes/no/ask）。
- engine-local 对应：`fsck_image`（engine.rs:2424）当前仅 no-repair
  （等价 fix_errors=no）；本任务扩展 FixErrors::No/Yes 两值
  （对齐 FSCK_FIX_no/yes，ask 需交互不在范围）。

## check_allocations 修复动作（均为"删除错误派生索引键"）

- `fs/alloc/check.c:388-423` `bch2_check_discard_key`：need_discard 键
  对应的 alloc 树 data_type != need_discard 或 journal_seq_empty 不符 →
  `bch2_btree_bit_mod_buffered(trans, BTREE_ID_need_discard, pos, false)`
  （删除该 need_discard 键）；无效 dev:bucket 同理删除。
- `fs/alloc/check.c:399-473` `__bch2_check_freespace_key`：freespace 键
  对应 alloc 树非 free 或 genbits 不符 → `delete_freespace_key`
  （check.c:352-386）：非 async 路径 = `bch2_btree_bit_mod_iter(trans,
  iter, false)` + `bch2_trans_commit`，**每键一个事务**；无效
  dev:bucket → 同样删除。
- `fs/alloc/check.c:144-190` `bch2_check_alloc_key`：alloc 键对应无效
  dev:bucket → `bch2_btree_delete_at(trans, alloc_iter, 0)`（engine 单
  设备，此动作不在本任务范围）。
- 修复门控：`bch2_need_discard_or_freespace_err`（check.c:117-142）——
  `repair` 参数 → FSCK_CAN_FIX；被 fsck 循环调用处（`bch2_check_
  allocations` 主 pass）传 `repair=true`。

## CLI 参数（-y/-n/-f 语义）

- `src/commands/fsck.rs:32-46`：`auto_repair: bool`（-y）、
  `no_repair: bool`（-n）、`force: bool`（-f）。
- `fsck.rs:266-269`：`no_repair` → opts 追加 `nochanges` +
  `fix_errors=no`；`fsck.rs:229-234`：`auto_repair`（系统调用路径）
  直接返回；`-y` 经 `cli.yes` → `fix_errors=yes`（fsck.rs:248-250）。
- engine-local CLI：`bin/subvol-fsck.rs`（T0195）已有 `-n/--no-repair`
  （唯一模式）与 `-f/--force`（预留）；本任务新增 `-y/--yes` 修复
  模式，`-f` 保持预留（engine 无 clean 标记，force 无承载）。

## engine-local 写路径模板

- `set_need_discard_index`（engine.rs:2674-2690）：`bch2_btree_bit_mod
  (&mut trans, BTREE_ID_NEED_DISCARD, position, set)` + `bch2_trans_
  commit`，-12（ENOMEM）→ realloc 重试，单事务/键——即
  delete_freespace_key 的 engine-local 等价模板（set=false 即删除）。
- `verify_bucket_indexes`（engine.rs:618-668）：alloc_free /
  expected_need_discard 派生集 vs freespace / need_discard 树实际集
  ——修复动作的"删除集合"来源（树中不在 expected 集的键）。
- `delete_sync`（engine.rs:562）事务删除入口（备选，位图键需 bit_mod）。
- BTREE_ID_FREESPACE=5 / BTREE_ID_NEED_DISCARD=6（engine.rs:87-88，
  本仓库 btree id 方案，约束 14 豁免）。
