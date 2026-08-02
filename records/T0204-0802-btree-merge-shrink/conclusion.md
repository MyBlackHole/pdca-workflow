# T0204 conclusion：btree merge（前台合并/树收缩）

## 结论

AC-1..AC-5 验收通过，无偏离。do 阶段提交 `4d4a2b2`（subvol: T0204 前台
合并挂载与三处实现缺陷修复, 0.1.0，1011 行）；全量回归：lib 233 passed
（串行 25.61s / 并行 --test-threads=4 13.5s，8 轮 7 全过）、btree_proptest
15 passed（45.19s）、fsck_cli 5 passed；单项均 <1min。收敛验证
valid:true（E-0001/E-0002/convergence-map 已注册）。

## 关键发现

1. **merge 门控/计数语义是挂载正确性的核心**：bcachefs 以
   `u64s *merge_count`（interior.h:203）区分"成功合并（调用方须 restart
   重遍历）"与"无需合并（继续提交）"。subvol 首版缺失该区分导致 commit
   无限 restart（无操作也重启）；修复后仅 `merge_count>0` 触发
   `restarted=4`。同类语义在 split 后逐层调用处以 `null_mut` 显式关闭。
2. **N→1 打包的追加语义**：`bch2_btree_sort_into` 对多个 src 逐次调用
   `bch2_sort_repack`，输出位置必须是 `vstruct_last(dst)`（sort.c:132）
   追加而非 bset 头覆写；首版固定偏移覆写导致 merge 丢键
   （live_u64s 9 vs 24 断言暴露）。
3. **merge 需要父层 intent 锁升级**：parent 仅持 read 锁时
   `bch2_btree_node_lock_write` 断言 owner 失败；按 interior.c:3068
   update_start / commit.c:1432 语义在 merge 内对 parent 路径执行
   `bch2_btree_path_upgrade(level+2)`，失败走毒化+put（-7）。
4. **merge 合法参与分裂节奏**：插入流程中 split 与 merge 交替出现，
   分裂点序列偏移（原 [19,27,35...] → 实际 [14,22,30...]）是 merge
   合并 3 子树为 2 的正确表现，非实现错误；测试期望按 bcachefs 语义
   修正为 restart 循环。
5. **测试侧两处容量约束**（非实现缺陷）：① 路径池上限
   BTREE_ITER_INITIAL=64（每 update 持一条路径引用），单事务批量须
   ≤32；② 叶容量 64 键与批大小 32 谐振（split 后半叶恰 32 键 + 批 32
   键 = 恰好填满）导致无限 split 重放（实测 53844 轮无进展），批 16
   键避开谐振后收敛——批大小必须避开"容量/2"谐振点。

## 证据

E-0001 check-evidence.md（AC-1..AC-5）、E-0002 ac1-source-anchors.md
（AC-1）、convergence-map（AC-1..AC-5）。

## 处置

- 知识沉淀：merge 挂载语义链（merge_count 区分 / vstruct_last 追加 /
  parent 锁升级 / 批大小与叶容量谐振规避）进入 knowledge/core。
- 后续候选：merge 失败路径定向故障注入（锁冲突/push_pos miss 毒化）；
  3→2 打包域内不可达（D10）的降级路径验证；并行 flaky（split_stress
  同类）基线问题专项。
