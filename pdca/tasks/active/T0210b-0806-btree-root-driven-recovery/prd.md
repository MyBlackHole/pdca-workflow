# T0210b PRD：btree 节点实体恢复切换（AC-3/AC-4）

## 背景

T0210 AC-1/AC-2（已提交 3da6aae）落地节点磁盘扇区 ptr：分配产出
btree_ptr_v2（dev/offset/gen）、脏节点经 flush→write_trans 写 ptr
扇区、split/merge 新节点可读回。但恢复仍走 T0201 journal-first 语义：
重开纯 btree_keys 重放从空重建树，节点扇区从不读盘。

本任务按 PRD 原 AC-3/AC-4 补齐：恢复切换为 root 绑定 + 节点遍历加载，
并为节点写盘路径补崩溃矩阵与故障注入。

## 上游对齐锚点

- recovery.c `bch2_fs_btree_iter_init` / `bch2_btree_roots_read`：重放后
  从 journal btree_root 条目绑定 root，再按需 bch2_btree_node_read
  加载（lazy：traversal 才读盘）。
- journal/entry.c / journal.c btree_root 条目（BCH_JSET_ENTRY_btree_root）
  格式与写入侧（update.rs commit 时写 root）。
- read.c `bch2_btree_node_read`（io.rs 已有，seq/csum 校验）。
- bset 头 journal_seq 过滤：读回 bset 仅采纳 journal_seq <= 重放 seq 的
  部分（对齐 read.c first_bset/bset journal_seq 黑名单语义）。

## 交付物

1. **root 绑定**：open_persistent 重放后从 journal btree_root 条目绑定
   各 btree root（对齐 recovery.c）。当前 journal 已含 root 记录（
   T0201 建立），engine 层需接入读取。
2. **节点遍历加载**：从 root 出发 bch2_btree_node_read 递归加载子节点
   （对齐 btree iter 首次访问路径）；重开后树内容与崩溃前一致
   （scan 与 shadow 对比）。
3. **journal_seq 过滤**：节点 bset 头 journal_seq 新于重放 seq 的扇区
   作废（构造"扇区新于重放 seq"场景验证）。
4. **崩溃矩阵（AC-4）**：T0201 框架扩展——commit 前/后崩溃、节点写盘
   前/中/后崩溃，重开一致性与不变量保持（约束 9：测试 1 分钟内）。
5. **故障注入**：节点扇区写失败、节点损坏读失败（为 P3 node_scan 铺路）。

## 验收标准

- [ ] **AC-3 恢复切换**：重开走 root 绑定 + 节点遍历加载（非纯 btree_keys
  重放重建）；重开后树内容与崩溃前一致（scan 与 shadow 对比）；节点
  bset 头 journal_seq 过滤正确（扇区新于重放 seq 作废，节点数据以
  journal 为准）。
- [ ] **AC-4 崩溃矩阵**：commit 前/后崩溃、节点写盘前/中/后崩溃，重开
  一致性与不变量保持（约束 9：测试 1 分钟内）。
- [ ] **AC-5 门禁**：全量 `cargo test --lib`（<1min）+ `cargo fmt --check`
  + diff gate 干净。

## 边界

- 单设备（s_bdev_file 模拟盘）。
- node_scan（P3）不在本任务实现；故障注入仅铺路（失败语义正确即可）。
- 恢复语义与崩溃前一致性以现有 shadow/model 校验为准。

## 对齐依据

- 所有新增控制流来自上表锚点函数（recovery.c/journal entry 解析/read.c）；
  降级路径照搬不简化（约束 6）。
- 不新增上游不存在的函数（约束 8）。
- btree id 编号保持域内自有（约束 14 豁免）。
