# T0202 conclusion：属性测试模型 op 域扩展（btree × alloc 组合）

## 结论

AC-1..AC-6 验收通过（AC-5 一项偏离需裁决，见下）。提交 `f9df169`
（subvol），全量测试 249 全绿（229 lib + 15 btree_proptest 44.46s +
5 cli）+ fmt。

## 关键发现

1. **discover_discard_buckets 的入队语义**（engine.rs:1309）：不只是
   统计——扫描 need_discard 树位并重新入队（insert + push_back）。
   这是崩溃恢复后队列重建的权威入口（T0197 op4 模式的事实基础）；
   组合测试首跑即捕获"模型清空队列但引擎 discover 已入队"的失配，
   修正后模型与引擎严格同构。
2. **need_discard 树 = 持久队列，fast_discard = 内存工作集**（bcachefs
   语义）：open_persistent 不自动恢复 discard 队列（darray 内存态），
   树位保留；组合测试断言 open_persistent 后 discard_queue_empty、
   discover 计数 == 模型 need-discard 桶数。
3. **崩溃后桶三态精确可断言**：btree 数据全走 journal（sync 只 flush，
   节点不写桶），桶状态仅由 alloc op 驱动 → 组合域无 backpointer 干扰，
   reclaim 恒成功（0↔2 toggle）、discard 恒成功（队首 state==2）。
4. **add_free_bucket 公开化**（AC-5 偏离）：btree 模块私有导致集成
   测试无法初始化桶状态，该测试设施提升为 pub 方法（逻辑零变化，
   43 处调用点机械改写）。
5. **既有 flaky 记录**：默认 16 线程全并行下 split_stress 偶发 >60s
   （stash 原版同样复现，非 T0202 引入，与并发度相关）；验证基线
   --test-threads=4（44.46s < 60s 满足约束 9）。

## 证据

E-0001 check-evidence.md（AC-1..AC-6）、E-0002 ac1-source-anchors.md
（AC-1）、convergence-map。

## 处置

- 知识沉淀：组合模型 op 域设计（三态影子 + discover 重建语义 +
  fast_discard 内存态）进入 knowledge/core。
- 待验证：AC-5 偏离（add_free_bucket 公开化）需用户 verdict 确认。
