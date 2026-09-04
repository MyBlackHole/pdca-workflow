---
schema: pdca.asset/v1
id: ontology:domain/core-foreground-merge-mount-semantics
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-foreground-merge-mount-semantics/1.0.0
summary: 前台合并挂载语义链：merge_count 区分 / 打包追加 / 锁升级 / 谐振规避（T0204）
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 foreground-merge-mount-semantics 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 前台合并挂载语义链：merge_count 区分 / 打包追加 / 锁升级 / 谐振规避（T0204）

## 适用场景

为 btree 实现 bcachefs 风格前台合并（foreground merge）并挂载到事务
提交路径；或排查"commit 无限 restart / merge 丢键 / merge 内写锁断言
失败"类问题。

## 关键事实（引擎语义）

1. **merge_count 区分是挂载正确性核心**（interior.h:203）：wrapper
   `bch2_foreground_maybe_merge` 返回 0 有两种含义——"无需合并"
   （needs_merge 门控不满足）与"合并成功"。调用方必须用
   `u64s *merge_count` 出参区分：**仅 merge_count>0 时事务 restart
   （restarted=4, return -4）重遍历**；否则继续提交。缺失该区分
   导致"无需合并也 restart"的无限循环（每轮重放必然再次不合并，
   无进展）。split 后逐层调用点传 `null_mut` 显式关闭 restart。
2. **N→1 打包必须追加而非覆写**（sort.c:132）：`bch2_btree_sort_into`
   对多个 src 逐次调用 `bch2_sort_repack`，输出位置必须是
   `vstruct_last(dst)`（`dst + 3 + (*dst).u64s`）。固定从 bset 头写
   会覆盖前序打包内容导致丢键（实测 live_u64s 9 vs 24 断言暴露）。
3. **merge 需要父层 intent 锁升级**（interior.c:3068 / commit.c:1432）：
   `bch2_btree_node_lock_write(parent)` 要求本线程已持 parent intent
   锁；路径仅 read 锁时必须先 `bch2_btree_path_upgrade(trans, path,
   level+2)`，失败走毒化（merge_fail_reset_sib_u64s）+ 路径释放
   （merge_put_sibling_paths）返回负值。
4. **失败毒化防反复尝试**（interior.c:2577/2591）：任何失败路径
   `sib_u64s = live + sib_live`（超 HYSTERESIS 减半，min(U16_MAX-1)），
   使 needs_merge 门控短期不满足；毒化路径必须同步恢复已拿的写锁、
   释放 sibling 路径（merge_put_sibling_paths 跳过 pivot）。
5. **merge 合法参与分裂节奏**：插入流程中 split 与 merge 交替出现，
   分裂点序列偏移（原 [19,27,35...] → 实际 [14,22,30...]）是 merge
   合并 3 子树为 2 的正确表现；测试期望必须用 restart 循环（重建
   iter + update + 重 commit 至 0）表达，不能假定无 merge 的固定序列。
6. **测试批大小必须避开叶容量谐振**：叶容量 64 键时，批大小 32 与
   split 后半叶 32 键**恰好谐振**——每轮重放必然再次 split，无限
   restart（实测 53844 轮无进展）。批大小取 16（或避开"容量/2"）
   即收敛。同理路径池上限 BTREE_ITER_INITIAL=64 约束单事务 update
   数 ≤32（每 update 持一条路径引用）。

## 验证手法

- 删除压力收缩断言：tree_stats（沿 root child DFS，逐节点
  `bch2_btree_node_check_topology`）前后对比 depth 不增、叶/节点数
  减少——直接证明 merge 真实收缩。
- 崩溃恢复：delete 压力后 drop 不 flush → open_persistent 重开 →
  键集精确恢复 + verify_all。
- 属性测试：LCG 随机 put/delete × 每步 BTreeMap 模型对照。
