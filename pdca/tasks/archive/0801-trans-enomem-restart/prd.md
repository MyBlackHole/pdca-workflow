# T0175 事务 commit 循环未将 -ENOMEM 纳入 restart 导致分裂路径硬失败

## 问题

T0174 `split_stress_preserves_model` 阶段 1 预写 2000 键稳定复现
`Transaction(-12)`：分裂路径需要大事务内存（subbuf），trans 初始内存
预算不足时引擎硬失败，而 bcachefs 对该情形执行 transaction restart。

## 根因

- 引擎 `__bch2_trans_kmalloc`（update.rs:99-102）：`mem_bytes != 0` 且空间
  不足时设置 `realloc_bytes_required` 返回 null → subbuf reserve
  （update.rs:219）返回 -12 → commit 循环（engine.rs:871）仅对 `-4`
  restart，`-12` 硬失败返回用户。
- bcachefs `__bch2_trans_kmalloc`（iter.c:3795-3800）：mem 已存在且需扩容
  时返回 `BCH_ERR_transaction_restart_mem_realloced`（restart 类错误）并
  记录 `realloc_bytes_required`；`bch2_trans_begin`（iter.c:3913-3933）
  消费该字段 `krealloc` 扩容 `mem_bytes`。
- bcachefs `bch2_trans_commit`（commit.c:1319-1320）顶层把 `-ENOMEM` 与
  `BCH_ERR_transaction_restart` 同等纳入重试。

## 方案

对齐 iter.c:3798-3800 + 3913-3933 + commit.c:1319：

1. **update.rs `__bch2_trans_kmalloc` 空间不足分支**：设置
   `realloc_bytes_required` 后同时设置 `trans.restarted` 为
   `BCH_ERR_transaction_restart_mem_realloced` 对应码（新码，如 5，
   与既有 4=fault_inject 区分）。
2. **update.rs subbuf reserve 失败传播**：`__bch2_trans_subbuf_alloc`
   返回 null 时，若 `trans.restarted != 0` 则返回 -4（restart 传播），
   否则保持 -12（真 ENOMEM，如 size > BTREE_TRANS_MEM_MAX）。
3. **iter.rs `bch2_trans_begin`**：`restarted == mem_realloced 码` 时消费
   `realloc_bytes_required` 扩容 `mem`（`realloc`，更新 `mem_bytes`），
   对齐 iter.c:3913-3933（引擎无 mempool 降级，直接 realloc，失败保持
   原 mem 并继续重试语义）。

不改动 commit 循环（restart 统一由 -4 表达，与既有 -4 处理路径一致）。

## 影响面

- update.rs（kmalloc 分支 + subbuf 传播）、iter.rs（trans_begin 扩容）
- 涉及路径：所有事务操作（put/delete/批量），分裂路径为首次真实触发者
- 既有 -4 restart 路径不变（restart_count 机制不变）

## 验收标准

- [ ] AC-1: T0174 `split_stress_preserves_model` 通过（分裂路径不再 Transaction(-12)）
- [ ] AC-2: 既有全量回归绿（lib 173 + 集成 9/9 以上）+ fmt 干净
- [ ] AC-3: trans 扩容仅发生在 restart 时（trans_begin 消费 realloc_bytes_required），无运行时回归
- [ ] AC-4: 连续 8 轮 T0174 + 既有 crash/fault/reclaim 属性测试稳定
- [ ] AC-5: 与 bcachefs 语义对齐（iter.c:3798-3800/3913-3933/commit.c:1319）

## 范围外

- interior split 异步 update_start 完整语义（T0168 P1 其余部分）
- T0174 测试本身（其 PRD/证据独立登记）
- 真 ENOMEM（超 BTREE_TRANS_MEM_MAX）路径保持硬失败（bcachefs 同）

## 备注

- 提交：bug-commit-format（【B-T0175】…，0.1.0 -> 0.1.0）
- parent: T0174（T0174 测试暴露本缺陷）
