# btree 分裂压力测试 + ENOMEM restart 修复模式

来源：T0174-0801-btree-split-proptest / T0175-0801-trans-enomem-restart
（bcachefs 风格 Rust 存储引擎属性测试与缺陷修复）。

## 上下文与约束

分裂路径在随机属性测试中天然是冷路径：节点容量 ~118 键（4KB、
max_u64s≈470、最小键 4 u64s），而小键空间 + 少量 ops 的属性测试恒深 1。
多级分裂（leaf split → 内部节点更新 → root 分裂）是 btree 正确性核心路径，
首次真实触发即暴露三类缺陷：节点容量配置错误、trans 扩容未纳入 restart、
journal reclaim 偶发 -9。

## 假设与行动

- **确定性触发分裂**（容量算术保证，非概率）：节点容量上界
  max_u64s ≈ 470、最小键 4 u64s → 单节点最多 ~118 键；阶段 1 预写
  2000 唯一键（超上界 10 倍）必然 17+ leaf split + root 分裂、深度 ≥ 2。
- **ENOMEM restart 三件套**（对齐 iter.c:3798-3800/3913-3933、
  commit.c:1319-1320）：
  1. `__bch2_trans_kmalloc` mem 不足时设置 `trans.restarted = 5`
     （mem_realloced）并记录 `realloc_bytes_required`，返回 null。
  2. 消费方（subbuf reserve）失败且 `restarted != 0` → 传播 -4（restart），
     真 OOM（未设置 restarted）保持 -12 硬失败。
  3. `bch2_trans_begin` 在 `restarted == 5` 时消费 `realloc_bytes_required`
     realloc 扩容（失败降级 BTREE_TRANS_MEM_MAX，再失败保留原 mem 重试）。
- **commit 循环兜底**：`-4 || (-12 && restarted != 0)` 纳入 restart 重试，
  真 OOM（首分配失败、restarted 未设置）保持硬失败避免无限重试。
- **journal res_get 等待语义**（对齐 journal.c res_get_slowpath()）：direct
  reclaim 未推进时 `update_last_seq` + 10s deadline + 1ms sleep 重试，
  超时才 -9；`__btree_node_flush` 三分支（0=已写完 / -1=保留 unflushed /
  -5=写盘失败，对齐 commit.c:254 与失败 break 语义）。

## 结果与证据

- T0175 修复后：lib 173/173、集成 10/10（多轮 78.95-100.14s 全绿）。
- 关键回归锚点：`direct_reclaim_keeps_btree_pin_unflushed_after_write_error`
  （写盘失败翻转 write_idx 后 pin 必须保留 unflushed，journal.rs:2767/2772）。
- proptest-regressions 自动记录修复前失败用例，后续运行重放保障回归。

## 成功原因

- 缺陷定位依赖**节点几何锚点**：`BCH_SB_BTREE_NODE_SIZE` 位域 12-27 单位
  为扇区（bcachefs_format.h:1223），`flags[0] = 8<<12` 才是 4KB——
  1 扇区=512B 时 2000 键必然触发第 4 级分裂越界 `BTREE_MAX_DEPTH=4`。
- 修复前用 eprintln 打点 + 失败现场日志（restarted/req/mem_bytes/
  nr_updates）定位 write_idx 翻转路径，随后对齐 commit.c:254 分支语义。
- 大事务压力（subbuf）+ 并行 reclaim 同时覆盖，暴露 res_get 立即失败缺陷。

## 适用与不适用条件

- 适用：任何 btree/索引引擎需要验证分裂路径 + 崩溃恢复 + ENOMEM 语义的场景。
- 不适用：无 restart 机制（引擎直接失败返回）或节点容量可动态增长的场景
  （容量算术触发的前提是固定节点上限）。

## 下一轮建议

- interior split 异步 update_start 完整语义（T0168 P1，T0174 范围外声明），
  本测试已建立多级分裂基线可衔接。
- D2 seq 环回（JOURNAL_SEQ_MAX 硬失败）与 res_get 语义同域，可趁热排期。
