---
schema: pdca.asset/v1
id: T0205-0802-btree-node-rewrite
phase: check
source_ids: [E-0003, E-0002]
---

## 上下文

T0205 目标：为 subvol 增加 bcachefs 对齐的 btree 节点重写能力
（`bch2_btree_node_rewrite` interior.c:3276 + `rewrite_key` 3345 +
`rewrite_pos` 3373），挂载 `rewrite_node`/`rewrite_node_key` 公共入口，
交付叶/内部/root 重写、hash 匹配、失败注入、崩溃恢复与属性测试
（AC-1..AC-5）。

do 阶段提交 `468a0c5`（实现 + 7 测试 + 存量 flake 修复，846 行）；
Check 阶段代码审查发现 rewrite_key 的 level 语义偏差并修复（`0b1817a`）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| AC-1 修改前锚点记录完整（语义链/调用点/差异判定/测试锚点 4 表） | ✓ 通过，ac1-source-anchors.md 53 行，D1-D10 逐项判定 |
| AC-2 rewrite 实现与 interior.c:3276/593/346 语义一致 | ✓ 通过，审查逐段核对（alloc_replacement/format_fits 严格小于/seq+1/sort_into/take_new_node/parent/root 分支/retire） |
| AC-3 公共入口挂载正确 | ✓ 通过，但审查发现 rewrite_key level 语义偏移一层（首版按 rewrite_pos 约定实现），已修复 |
| AC-4 7 个专项测试覆盖全部场景 | ✓ 通过，T1-T7 断言与 PRD 锚点表一一对应 |
| AC-5 全量回归 <1min | ✓ 通过，lib 240（10.54s）/ proptest 15（42.6s）/ fsck_cli 5 / concurrent 2 |
| 存量 flake（drop 检测）为既有问题非 T0205 引入 | ✓ 通过，baseline stash 对照同样失败 1/12，修复随提交附带 |

## 分析

1. **rewrite_key 的 level 语义是本次审查的核心发现**：bcachefs 中
   `rewrite_key` 与 `rewrite_pos` 的 level 参数语义不同——rewrite_key
   的 level=目标节点层数（async 传 `b->c.level`、read.c:1243 传
   `scrub->level - 1`，CLASS depth=level），rewrite_pos 的 level=指针键
   所在层（move.c:321，depth=level-1）。subvol 首版将两个入口统一按
   rewrite_pos 约定实现（depth=level-1），导致 rewrite_key 调用方需比
   bcachefs 多传 1，且 level=0 时 u8 下溢 depth=255 崩溃（公共入口无
   断言）。修复为 depth=level（叶 level==0 合法），T4 传参 1→0，与
   bcachefs 严格对齐；全量回归通过。
2. **rewrite 主体与既有模式一致性**：path 换新走
   `btree_path_take_new_node`（与 split interior.rs:740/787/1155 同款），
   失败路径四态（-7/-8/-10/-12）均完整释放（release_node + 解锁 +
   path_put），与 interior.c err_free_update 语义对应；未发现悬挂引用。
3. **持久化**：parent 分支 set_dirty(parent)、root 分支 transition CLEAN +
   set_dirty(n)（journal-first），T6 崩溃恢复实测：sync 后 rewrite →
   drop 不 flush → 重开精确键集 + verify_all。
4. **存量 flake 根因**：reclaim worker 每 25ms `Weak::upgrade()` 短暂持有
   Arc，测试线程恰在窗口内 drop(engine) 时 EngineState::drop 不执行、
   catch_unwind 捕不到 panic。修复 = 测试内先置 stopping + notify_all +
   join worker 再 drop。修复后 10/10 全量稳定性验证 + 20 轮无挂起。
5. **代码审查方法论**：按 code-review-checklist 双轴（标准轴=内存安全/
   错误路径/锁序/持久化；规范轴=约束 8/12/13/14 无新函数/无自有逻辑/
   无新结构体/无范围蔓延），标准轴 0 Blocking / 0 Warning。

## 失败原因

无（confirmed）。Check 期间修复的 level 语义偏差已回归验证，
不计入失败。

## 适用边界

- rewrite 为同步 API（D3：域内无 async worker）；fsck/scrub 修复路径
  与 GC 触发重写不在本任务范围（后续候选）。
- root 重写经 rewrite 主体 parent==null 分支（D5/D6）；`rewrite_pos`
  `BUG_ON(!level)` 保留为公共入口断言；`rewrite_key` 叶 level==0 合法。
- 单写者域（commit 全程持 fs 锁，D1）：无 btree_update 记账对象、
  无异步写队列（D2 用 journal-first 写盘替代）。
- btree id 语义为 subvol 自定（约束 14 豁免），fs 层 type 规则不适用。

## 下一轮建议

- rewrite 的 fsck/scrub 自动触发路径（read.c:1243 语义）可作后续候选，
  需先有 fsck 修复调度框架（T0195-T0200 已建）。
- 并发场景下 rewrite 与 split/merge 交错的多写者测试可扩展
  （当前 T7 为单写者属性测试）。
- 存量 flake 修复模式（drop 前 join worker）可沉淀为通用测试辅助，
  供其他 worker 类测试复用（discard/reclaim worker 同款隐患）。
