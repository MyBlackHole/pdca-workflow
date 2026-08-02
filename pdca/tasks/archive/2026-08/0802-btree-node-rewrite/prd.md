# T0205 PRD：btree 节点重写（rewrite/格式化，journal-first 持久化）

## 需求

实现 bcachefs 的 btree 节点重写能力（`bch2_btree_node_rewrite`
interior.c:3276 对齐）：为指定节点生成替换节点（格式重算 + seq+1 +
全键搬移），经 interior 更新提交替换旧节点（parent pivot 更新或
root 替换），旧节点 retire 释放。触发入口：按 key+hash 匹配
（rewrite_key）与按 pos 定位（rewrite_pos）。

背景：subvol 已有 `BTREE_NODE_need_rewrite` 标志（types.rs:677）但
仅有 clear 调用、无消费路径——节点重写能力完整缺失。该能力是
fsck 修复（T0195-T0200 已做 fix_errors 框架）与后续 GC 的前置。
T0204 已论证设计替代：subvol 节点持久化为 journal-first
（`__bch2_btree_node_write` io.rs:283），write_new_node 语义 =
事务内写节点，无 bcachefs 的异步写队列。

## 验收标准

- [ ] AC-1: 修改前逐段对照 bcachefs node rewrite 管线（interior.c
      `bch2_btree_node_rewrite` 3276-3343 / `bch2_btree_node_alloc_replacement`
      593-616 / `bch2_btree_node_rewrite_key` 3345-3359 /
      `bch2_btree_node_rewrite_pos` 3373-3388 / async_btree_rewrite
      3400+ / check.c:1353 format_fits 语义），记录锚点与 subvol
      域内差异判定。
- [ ] AC-2: 替换节点分配（alloc_replacement）：格式重算（复用
      `__bch2_btree_calc_format` interior.rs:1411）→ 放不下回退旧格式
      （`bch2_btree_node_format_fits` 语义）→ seq=旧+1 → min/max 继承 →
      `bch2_btree_sort_into` 全键搬移 → `btree_node_reset_sib_u64s`。
- [ ] AC-3: rewrite 主体：路径锁（intent 持有 + 写锁）、pending_interior
      提交设施（对齐 interior.c 的 update_start→emit_new_node_key→
      insert_node/set_root→update_done 顺序）、parent 分支（pivot 更新）
      与 root 分支（set_root）、旧节点 retire（will_free_node + free_inmem
      语义）、trans_node_add + verify_not_in_iters、失败路径完整恢复
      （新节点释放、锁恢复、路径释放）。
- [ ] AC-4: 公开入口与测试：rewrite_key（hash 匹配）/rewrite_pos 挂载
      引擎 API；测试覆盖——重写后键集/拓扑不变、格式与 seq 断言、
      parent pivot 更新、root 重写（无 parent 分支）、alloc/锁失败注入
      原节点不动、重写提交后崩溃恢复一致（journal-first 回放）。
- [ ] AC-5: 定向、属性和全量 workspace 测试通过，单项不超过一分钟
      （验证基线 --test-threads=4）。

## 范围外

fsck/scrub 调度集成、GC 触发重写、异步 rewrite worker 队列（async
work）、格式升级迁移策略、need_rewrite 自动触发机制（本次仅提供
能力与显式入口，不接自动触发）。

## 备注

复用：`__bch2_btree_calc_format`（interior.rs:1411）、
`bch2_btree_sort_into`（bset_build.rs:839）、`bch2_btree_build_aux_trees`
（753）、`bch2_btree_node_mem_alloc`（cache.rs:490）、
`bch2_btree_node_lock_write` + 路径锁升级（interior.rs:351/1688）、
`retire_node`（596/1769 闭包）、pending_interior 提交
`bch2_trans_commit_pending_interior`（update.rs:2219）、
`__bch2_btree_node_write`（io.rs:283）、`bch2_btree_node_check_topology`
（256）、`bch2_btree_set_root_for_read`（223）。

差异判定（草案，AC-1 细化）：
- D1: update_start/update_done → pending_interior 提交设施（无 btree_update
  对象，commit 全程持 fs 锁，D6 同 T0204）。
- D2: write_new_node 异步队列 → journal-first `__bch2_btree_node_write`
  事务内落盘（T0204 设计替代已论证）。
- D3: async_btree_rewrite work 队列 → 同步 API（域内无异步调度）。
- D4: `bch2_btree_node_format_fits` 需移植（subvol 无对应，校验格式
  重算后是否放得下，check.c:1353 语义）。
- D5: rewrite_pos 的 BUG_ON(!level)（域内 root 重写经 rewrite 主体
  parent==null 分支，pos 入口要求 level>0 保持一致）。
