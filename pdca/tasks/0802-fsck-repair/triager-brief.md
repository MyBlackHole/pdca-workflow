# T0198 Triage Brief

## 分类

- 类型：feature
- 场景：development
- 父任务：T0197

## 本地源码核验

- `src/commands/fsck.rs`：`FsckCli` 结构（fsck.rs:32-46）——
  `auto_repair: bool`（-y 自动修复）、`no_repair: bool`（-n 只检查）、
  `force: bool`（-f）；cmd_fsck 中 `-y` → opts `fix_errors=yes`、
  `-n` → `nochanges` + `fix_errors=no`（fsck.rs:266-269）；默认
  fix_errors=ask。修复由内核 `bch2_fs_fsck_errcode` 按 fsck=1 跑
  PASS_FSCK 全量 pass 执行。
- `fs/init/error.c:433-463` `bch2_fsck_err_opt`：FSCK_FIX_exit →
  fsck_errors_not_fixed（不修）；FSCK_FIX_yes + FSCK_CAN_FIX →
  fsck_fix（执行修复）；FSCK_FIX_no → fsck_ignore；FSCK_FIX_ask →
  fsck_ask/autofix。修复门控即此分支。
- `fs/alloc/check.c` 修复动作：`bch2_check_alloc_key`（144-190）无效
  dev/bucket → `bch2_btree_delete_at`；`bch2_check_discard_key`
  （388-423）need_discard 键与 alloc 树不符 → `bch2_btree_bit_mod_
  buffered(..., false)` 删除；`__bch2_check_freespace_key`（399-473）
  freespace 键不符 → `delete_freespace_key`（bit_mod_iter false +
  trans_commit，单事务/键）。修复动作均为"删除错误派生索引键"。
- engine-local：`fsck_image`（engine.rs:2424）仅 open_persistent +
  verify_all（无修复）；`verify_bucket_indexes`（engine.rs:618-668）
  给出 alloc_free/expected_need_discard 精确集合；`set_need_discard_
  index`（engine.rs:2674-2690）演示 bit_mod(false) + trans_commit 写
  路径（每键单事务模板）；BTREE_ID_FREESPACE=5 / BTREE_ID_NEED_DISCARD=6
  （本仓库 btree id 方案，约束 14 豁免）。

## 查重

T0195 disposition：「-f force 修复路径留待后续任务」；T0197
conclusion 建议链首项即 fsck 修复路径。无同范围活动任务。
T0195 已将 -f 定义为"即使标记干净也检查（engine 无 clean 标记，预留）"
——本任务按上游语义把**修复开关**落在 -y（auto_repair），-f 保持预留。

## 推荐

立项：feature/development，parent=T0197。库 fsck_image 扩展 fix_errors
模式（单入口对齐 bch2_fs_fsck_errcode）；修复动作=删除错误派生索引键
（freespace/need_discard，每键单事务）；守卫错误名（open/not_rw）不在
修复范围（skip 语义）；CLI -y 自动修复 + -n 默认只检查；退出码 0/1/2
沿用；集成测试覆盖 -y 修复成功与 -n 只检查不改镜像。
