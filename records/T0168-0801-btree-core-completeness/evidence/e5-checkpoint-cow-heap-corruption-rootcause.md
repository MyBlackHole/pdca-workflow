# 证据 e5：checkpoint COW 测试堆崩溃根因（AC-5）

## 复现

```bash
# 单测单独运行即崩溃（SIGABRT，glibc heap check）
cargo test --lib engine::tests::checkpoint_pages_are_cow_and_corrupt_page_falls_back_to_prior_root

# ASAN 定位（nightly + -Zsanitizer=address）
RUSTFLAGS="-Zsanitizer=address" cargo +nightly test --lib engine::tests::checkpoint_pages_are_cow
```

## ASAN 报告（关键帧）

```
ERROR: AddressSanitizer: heap-buffer-overflow
WRITE of size 40
    #1 core::ptr::copy_nonoverlapping::<u64>  btree/bset_update.rs:188
    #2 subvol::btree::bset_update::bch2_bset_insert  btree/bset_update.rs:188
    #3 subvol::btree::update::bch2_btree_bset_insert_key_inlined  update.rs:1644
    #4 subvol::btree::update::bch2_btree_insert_key_leaf  update.rs:1676
    #5 subvol::btree::update::bch2_trans_commit  update.rs:2160
    #6 StorageEngine::commit_operations_once  engine.rs:1142
    #7 StorageEngine::commit_operations  engine.rs:1081
    #8 Transaction::commit  engine.rs:490
```

## 根因（对照 bcachefs）

**直接根因**：`bch2_trans_commit`（crates/subvol/src/btree/update.rs:1953-1975）
的空间检查对**同一 leaf 的多个 update 不累加占用**，每个 update 单独按
当前节点剩余空间判断（检查时节点为空，16 个 8-u64s key 全部 fits=true），
随后一次性顺序插入；节点（512 字节 = 64 u64s）在第 8 个 key 后已满，
第 8 次 `bch2_bset_insert` 的 `copy_nonoverlapping` 仍向
`where_`（偏移 608 字节 > 512 字节分配）写入 40 字节，越界破坏堆。

**bcachefs 对照**（/home/black/Documents/bcachefs-tools/fs/btree/commit.c:1083-1097）：
持有写锁后、插入前，`trans_for_each_update` 对同一 leaf 的 update **累加**
`u64s += i->k->k.u64s`，再 `btree_key_can_insert(b, u64s)`（commit.c:427-432，
内部即 `bch2_btree_node_insert_fits`）；放不下返回错误中止 commit 并触发
split/restart。subvol 缺失该累加语义。

**次要防御缺失**：bcachefs `bch2_btree_bset_insert_key_inlined`
（commit.c:189-195）含 `EBUG_ON(insert->k.u64s > bch2_btree_keys_u64s_remaining(b))`
防御断言（调试期即可暴露越界），subvol 对应函数（update.rs:1593）缺失。

## 现场数据（临时调试输出，已还原）

```
check idx=0..15 全部 fits=true required=8 want=false   ← 检查时节点为空
insert where_off=160 node_size=512 nsets=1 bset_u64s=0   ← 第 1 次
insert where_off=608 node_size=512 nsets=1 bset_u64s=56  ← 第 8 次（越界点）
free(): invalid next size (normal)                        ← 释放时暴露
```

## 影响面与严重度

- 影响面：btree 写路径空间检查；任何单事务向同一 leaf 写入累计超过节点
  容量的 key 序列即触发；512 字节小节点最易触发，4KB 节点需更多 key。
- 严重度：**高（数据损坏/崩溃）**——内存破坏会污染堆，崩溃时机不定，
  checkpoint/持久化路径均受影响。
- 修复方向（供后续任务）：`bch2_trans_commit` 空间检查循环中对同一 leaf
  （`same_leaf_as_prev`）累加 `u64s` 后检查 `bch2_btree_node_insert_fits`，
  放不下即 `bch2_btree_split_leaf` + restart（对齐 bcachefs commit.c 语义）；
  并补 `bch2_btree_bset_insert_key_inlined` 的剩余空间 EBUG_ON。
