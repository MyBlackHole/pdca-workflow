# T0207 PRD（跟进）：T0206 收尾——root 重写 extent 保留修复 + AC-5/AC-6

## 需求

T0206 部分完成 PDCA（verdict=partial, V-T0206-001）的跟进任务，
完成 T0206 未交付部分：

1. **修复 root 重写 extent 缺陷**：`bch2_btree_node_rewrite` root
   分支（interior.rs）用 `child_ptr(n)` 构造自身指针键仅 mem_ptr
   寻址、无 extent ptr → 重写后 slot.key 丢失磁盘位置 → io 层重开
   `bch2_btree_root_read` 读盘 -2（io.rs:454 `bch2_bkey_ptrs_c`
   空）。上游语义：`bch2_btree_set_root` 后 root 记录保留原 extent
   （覆盖写原位置）。修复 = root 分支 bkey_copy 前合并旧 extent
   ptr（对齐上游 set_root 保留磁盘位置语义，知识契约
   `core/btree-node-rewrite-key-extent-contract.md`）。
2. **AC-5 完成**：`rewritten_node_revalidates_on_reopen` 测试修复
   后通过；重写提交后 verify_all 通过；崩溃注入收敛（fallback =
   io 层重开一致 + fsck 故障矩阵已有，T0200 模式）。
3. **AC-6 完成**：workspace 全量 `cargo test --lib` + `cargo fmt
   --check` + diff gate 通过，单项不超过一分钟。

## 验收标准

- [ ] AC-1: root 分支 extent 保留修复与上游对齐（对照 interior.c
      bch2_btree_set_root 语义），无新增自有逻辑（约束 8/12/13）。
- [ ] AC-2: rewritten_node_revalidates_on_reopen 通过（重写后
      slot.key 含 extent → mem_ptr 清零重开 → root_read 重新读盘
      成功、无 need_rewrite、seq=102、键集正确、拓扑校验通过）。
- [ ] AC-3: 重写提交后 verify_all 通过；io 层重开一致（崩溃注入
      fallback）验证。
- [ ] AC-4: 全量 `cargo test --lib` 通过（244+ 测试，<1min）+
      `cargo fmt --check` + diff gate 干净。

## 实现决策（草案）

- extent 合并：root 分支构造 `child_ptr(n)` 后，从 `b.key`（旧 root
  键）拷贝 extent ptr（bch2_bkey_append_ptr 或直接拷贝 ptr 数组）
  到 n_key，再 bkey_copy 到 slot.key。保持 mem_ptr 语义不变
  （engine journal-first 不读盘，无影响）。
- 上游对照：interior.c bch2_btree_set_root + bch2_btree_node_rewrite
  root 分支（T0205 已记录 3276/3312 锚点）。
- verify_all：engine 层重写提交后调 verify_all（T0200 模式）；
  io 层无 verify_all，等价验证 = 重开 root_read + topology。

## 范围外

T0206 已判定完成的 AC-1..AC-4（差异记录 D9 等）不在本任务范围，
除非修复引入回归。

## 备注

来源：T0206 conclusion.md（records/T0206-0803-fsck-scrub-rewrite/
conclusion.md）下一轮建议 1-3。前置：T0205（rewrite 主体）、
T0206 未提交工作区（4 文件，含 pending queue + 触发点 + 测试）。
