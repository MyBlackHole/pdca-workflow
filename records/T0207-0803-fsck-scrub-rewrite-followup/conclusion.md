# T0207 结论：root 重写 extent 保留修复 + AC-5/AC-6 完成

任务：T0207-0803-fsck-scrub-rewrite-followup（跟进 T0206 partial
判定 V-T0206-001）

## Verdict

**complete**（V-T0207-001）——4 项 AC 全部收敛，无遗留差异，无
待办跟进项。

## AC 收敛状态

| AC | 内容 | 状态 | 证据 |
|----|------|------|------|
| AC-1 | root 分支 extent 保留修复与上游对齐 | 完成 | check-evidence |
| AC-2 | rewritten_node_revalidates_on_reopen 通过 | 完成 | check-evidence |
| AC-3 | 重写提交后 verify_all 通过；io 层重开一致 | 完成 | check-evidence |
| AC-4 | 全量 cargo test --lib + fmt + diff gate | 完成 | check-evidence |

## 关键结论

1. **根因**：域内 child_ptr 闭包构造的新节点 key 仅含 mem_ptr、
   无 extent（上游 `__bch2_btree_node_alloc` interior.c:515-518 经
   `bch2_alloc_sectors_append_ptrs` 必带磁盘位置），root 分支
   set_root 后 slot.key 丢失磁盘位置 → io 层重开 root_read 失败 -2。
2. **修复**：child_ptr 从旧节点 `b.key` 继承 extent 合并到新键
   （覆盖写原位置语义，T0205 D）。语义完全对应上游 alloc 的
   append_ptrs，无新增自有逻辑/结构体。
3. **AC-5 测试修复链**：-2（无 extent）→ -11（未落盘）→ 103
   （sectors_written=0 二次重写）→ 通过。测试按上游语义补充
   提交 flush（commit.c:254 __btree_node_flush）与关闭序列化
   root 记录（io.c bch2_write_super → bch2_btree_roots）。
4. **门禁**：244 测试全绿（10.49s）、fmt 干净、diff 已提交
   （10c3bd6，5 文件 1004+/139-）。

## 沉淀

- 知识文件 `knowledge/core/btree-node-rewrite-key-extent-contract.md`
  已在 T0206 Act 阶段登记（mem_ptr/extent 双模式契约），本任务
  的落盘/序列化语义（flush + write_super）补充到 check-evidence。

## 后续

无遗留项。T0206 的 partial 判定经由本任务完全闭合。
