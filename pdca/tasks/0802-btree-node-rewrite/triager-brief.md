# T0205 triager brief：btree 节点重写（rewrite/格式化，journal-first 持久化）

## 输入

- 上一轮 T0204（merge 归档）范围外清单首位：btree_node_rewrite
  （设计替代已论证：journal-first 持久化 + __bch2_btree_node_write）。
- 用户决策：新核心能力方向，5 方向串行推进，本任务 = 方向 1。

## 现状核查

- subvol 有 `BTREE_NODE_need_rewrite` 标志（types.rs:677）与全套
  访问器，但仅 clear（初始化/恢复），无 set/消费路径 → 能力缺失。
- 已有可复用设施：calc_format（interior.rs:1411）、sort_into
  （bset_build.rs:839）、build_aux_trees（753）、mem_alloc
  （cache.rs:490）、锁升级（interior.rs:1688，T0204 引入）、
  retire_node（596/1769）、pending_interior 提交（update.rs:2219）、
  节点写（io.rs:283 journal-first）。
- 缺失：rewrite 主体、alloc_replacement、format_fits、公开入口
  （rewrite_key/rewrite_pos）、消费路径。

## 上游对照

- bch2_btree_node_rewrite（interior.c:3276-3343）：alloc_replacement →
  take_new_node → emit_new_node_key → parent?insert_node:set_root →
  will_free_node → write_new_node → free_inmem → trans_node_add →
  verify_not_in_iters → update_done → path_put → downgrade；失败
  update_free。
- bch2_btree_node_alloc_replacement（interior.c:593-616）：calc_format
  放不下回退旧格式、seq+1、min/max 继承、sort_into、reset_sib_u64s。
- 入口：rewrite_key（hash 匹配，fsck/scrub 用）/ rewrite_pos
  （level>0 按 pos）/ async_btree_rewrite_work（域内不做异步）。
- format_fits 语义（check.c:1353 注释：alloc_replacement 尊重边界）。

## 建议 AC（草案见 prd.md）

AC-1 锚点记录 → AC-2 alloc_replacement → AC-3 rewrite 主体 →
AC-4 入口+测试（键集/格式/seq/pivot/root/失败注入/崩溃恢复）→
AC-5 全量 <1min 基线。

## 风险

- 失败路径恢复完整性（新节点/锁/路径三态恢复）为正确性关键，须
  逐分支对照 interior.c 顺序。
- root 重写分支（无 parent）易漏，需定向测试。
- 崩溃恢复：重写提交后 crash → journal 回放必须一致（journal-first
  无磁盘上"新旧节点共存"窗口）。
