# T0203 conclusion：并发组合序列（多写者 × alloc op × 崩溃恢复精确断言）

## 结论

AC-1..AC-5 验收通过，无偏离。新增 `crates/subvol/tests/concurrent_combined.rs`
（纯测试侧，引擎零改动），10 例 proptest（CASES=10）连续 4 轮全绿
（约 4s/轮）；全量回归：lib 230 passed（10.38s）、btree_proptest 15
passed（43.78s）、fsck_cli 5 passed、subvol-fsck 0/0；fmt 通过。
收敛验证 valid:true（E-0001/E-0002/convergence-map 已注册）。

## 关键发现

1. **提交日志 = 精确性的确定性来源成立**：测试锁内"引擎提交 + 日志
   追加"原子成对，锁序 == 引擎 fs 锁串行化提交序（T0199 实测）；
   崩溃点 = 日志 sync_all + engine.sync() 后 abort，恢复重放
   （journal replay 只回放已落盘记录，fs/journal/read.c
   journal_replay_maybe_drop_overwrites）与模型**精确相等**（btree
   BTreeMap、alloc 三态投影、队列语义），非 T0201 的最终一致。
2. **日志行二元组协议**：`<op> | <result>`（err 编码）使模型转换与
   真实提交序列同构——allocate 成功解析返回 offset 并断言落在模型
   桶域，失败按 err 编码分支；并发 -28/-17/回旋边界全部经真实引擎
   结果驱动，无需预判守卫。
3. **Barrier 起跑对齐**：3 写者 Barrier 同步后各自执行 6..=12 步组合
   op，交错由引擎 fs 锁决定；多次运行仅日志内容不同，可重放性不变。
4. **环境教训**：/tmp 堆积 909 个旧测试残留目录（subvol-bucket-api-*
   等）曾致 btree_proptest 600s 超时（IO 拖慢），清理后 43.78s 正常；
   属环境问题非代码问题，测试用例本身无泄漏（本次运行后 tmp 干净）。

## 证据

E-0001 check-evidence.md（AC-1..AC-5）、E-0002 ac1-source-anchors.md
（AC-1）、convergence-map（AC-1..AC-5）。

## 处置

- 知识沉淀：并发提交日志协议（锁序 append + 结果二元组重放 +
  sync 崩溃点）进入 knowledge/core。
- 后续候选：真实磁盘故障模拟、op 域扩展至 open/close/set_rw 组合
  （T0197 守卫 × btree 交错）、事务级失败注入与恢复的端到端对照。
