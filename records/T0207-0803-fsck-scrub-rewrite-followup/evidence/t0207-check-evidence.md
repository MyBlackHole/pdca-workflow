# T0207 Check 证据：root 重写 extent 保留修复 + AC-5/AC-6 完成

任务：T0207-0803-fsck-scrub-rewrite-followup（跟进 T0206 partial 判定
V-T0206-001 的 root extent 缺陷与 AC-5/AC-6）

## AC-1：root 分支 extent 保留修复与上游对齐

- 修改：`crates/subvol/src/btree/interior.rs` child_ptr 闭包
  （bch2_btree_node_rewrite 内，root 分支）。
- 上游对照：
  - `fs/btree/interior.c:515-518` `__bch2_btree_node_alloc` 经
    `bch2_alloc_sectors_append_ptrs` 构造新节点 key，必带 extent。
  - `fs/btree/interior.c:1628-1645` `bch2_btree_set_root` 安装新 root。
  - `fs/btree/interior.c:3276` 起 `bch2_btree_node_rewrite`，root 分支
    3310-3312 调 `bch2_btree_set_root`。
- 实现：child_ptr 从旧节点 `b.key` 经 `bch2_bkey_ptrs_c` 取 extent，
  非空则 `bch2_bkey_append_ptr` 合并进新键（覆盖写原位置语义，
  T0205 D 记录）。无新增自有分支/结构体（约束 8/12/13 对齐：
  合并动作即上游 alloc 的 append_ptrs 语义）。

## AC-2：rewritten_node_revalidates_on_reopen 通过

- `cargo test --lib rewritten_node_revalidates_on_reopen` 通过。
- 修复前失败链：-2（slot.key 无 extent，bch2_bkey_ptrs_c 空）→
  -11（seq 不匹配，重写未落盘）→ 103（重开 key.sectors_written=0
  触发二次重写）。
- 修复后断言：重开 root_read 成功（magic/seq/level/范围逐项校验，
  io.rs:478-503）、无 need_rewrite（磁盘字节干净）、seq=102 持久化、
  键集 = 修复后内容（键 1 @ SPOS(9,1,0)）、拓扑校验通过
  （bch2_btree_node_check_topology）。

## AC-3：重写提交后 verify_all 通过；io 层重开一致

- io 层重开一致 = AC-2 测试（重写 → flush 写盘 → 序列化 root 记录 →
  重开 root_read 重新校验全链路）。
- engine 层 verify_all：`cargo test --lib engine::` 70 通过（含
  重写/崩溃注入场景，verify_all 全绿，无回归）。
- 写盘/序列化语义对照：`fs/btree/commit.c:254` `__btree_node_flush`
  → `bch2_btree_node_write_trans`；`io.c` `bch2_write_super` →
  `bch2_btree_roots`（关闭时从节点 key 序列化 root 记录）。

## AC-4：全量门禁

- `cargo test --lib`：244 passed; 0 failed（10.49s < 1min）。
- `cargo fmt --check`：干净。
- diff gate：5 文件改动已提交（interior.rs / io.rs / types.rs /
  update.rs / engine.rs，1004 insertions, 139 deletions），commit
  10c3bd6。

## 结论

全部 4 项 AC 收敛，无遗留差异。
