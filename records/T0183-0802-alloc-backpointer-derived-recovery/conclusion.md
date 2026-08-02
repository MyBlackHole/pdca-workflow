# T0183 conclusion：alloc/backpointer 派生维护与崩溃恢复验证

## 结论

AC-1..AC-5 验收通过。提交 `d259b46`（subvol）。

## 关键发现

1. **实现已被前置系列吸收**：pointer → alloc/backpointer 同事务派生链路
   （trigger_update_value/trigger_pointer_derived/bch2_trigger_extent）、
   恢复重建（bch2_rebuild_derived_for_key/rebuild_derived_state）、确定性
   验证器（check_extents_to_backpointers）与 recovery fault matrix 分别由
   T0181/T0182（64e6a49/e857bf1）、T0185/T0186（336c570/d6f11a1）、
   T0187 系列实现。T0183 增量收敛为：AC-1 源码锚点、AC-2 覆盖（overwrite）
   场景专项测试、AC-5 全量验证。
2. **AC-1 对照结论**：upstream `bch2_trigger_pointer`（buckets.c:630）→
   `bch2_trans_start_alloc_update` + `__mark_pointer` + 
   `bch2_bucket_backpointer_mod` 三件套与 subvol 派生实现逐行对应；两处
   记录差异（data_type 不入派生、delete 无 bp 匹配校验）经判定为 subvol
   域内设计，与 T0202 组合模型（data_type 由 alloc op 状态机管理）一致，
   不违反约束 12/13。
3. **overwrite 测试捕获语义**：同 pos 覆盖时 bch2_trigger_extent 先 old
   减（-3 扇区、删 bp 35）后 new 加（+5 扇区、写 bp 44），alloc 3→5、
   bp 精确迁移，check 通过——验证"无重复/悬挂/漏记"。
4. **既有 flaky 备注**：lib 并行偶发 1 failed 未能复现（连续 3 次全过），
   与已知 split_stress 并行 flaky 同类；验证基线 --test-threads=4。

## 证据

E-0001 ac1-source-anchors.md（AC-1）、E-0002 check-evidence.md
（AC-2..AC-5）、convergence-map。

## 处置

- 知识沉淀：AC-1 锚点表（trigger 三件套 + gen 校验链 + bp 键位编码）
  进入 knowledge/core。
- 后续候选：bp→extent 反向校验（T0185 限定方向 1）、data_type 并入
  派生（待 alloc op 状态机域扩展）、GC trigger。
