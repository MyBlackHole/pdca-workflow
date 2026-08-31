---
schema: pdca.asset/v1
id: ontology:domain/core-model-guard-decision-injection
type: domain
layer: Knowledge
status: active
summary: 模型守卫裁决注入模式（Model Guard-Decision Injection）
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
  testable_signal: "检查本文件 model-guard-decision-injection 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 模型守卫裁决注入模式（Model Guard-Decision Injection）

## 适用场景

属性测试模型需要覆盖"非法操作路径"（守卫/不变量错误路径）时，预判式
模型（`if state != 0 { 跳过 }`）只能验证合法路径，无法验证守卫错误名
与实现裁决的一致性。注入式模型改为无条件执行操作，由实现自身的
验证入口（verify_all / verify_guard_invariants）裁决合法/非法。

## 模式要点

1. **裁决入口必须是实现自己的验证函数**：模型不做 open 前守卫预判，
   而是 open 后让实现裁决。本实现 `open_bucket`（engine.rs:901）是
   无预校验 insert，open∧free 的非法态由 `verify_guard_invariants`
   （engine.rs:688-726）树序扫描报出（open 先于 not_rw）。
2. **期望推导按实现错误优先级**：模型按树序遍历 free 桶推导首个违规
   （OpenBucketFree 优先 NotRwBucketFree），与 verify_all（guard 检查
   最后执行）的首错误一致。
3. **影子状态与引擎状态脱节是反例重灾区**：① 影子数组更新遗漏（op 改
   造后循环 `open` 数组未同步）；② 错误假设维度独立性（allocate 清除
   open 标志——open 与 data_type 独立，allocate_bucket 不查 open）；
   ③ 新维度未进模型条件（worker 模型缺 device_rw → not_rw 时引擎
   EAGAIN 旋转而模型置 free）。
4. **panic 掩盖防护**：测试引擎用 Option 包装 + Drop 关桶，proptest
   失败时先关桶再 panic，防止引擎 drop 的 open-bucket-leak 断言
   （engine.rs:1788）遮蔽 prop_assert 真实消息。
5. **确定性场景锁定维度**：proptest 负责随机探索（含 shrink 反例），
   另配确定性测试逐条断言新维度的每个错误码（-1/-16/-11/错误名），
   防止随机序列覆盖不足。
6. **回归闭环**：proptest-regressions 自动保存最小反例重放；反例修复
   后必须确认新反例不再复现且保存的历史反例全部通过。

## 关键语义（来自实现反例确认）

- `open_bucket` 无守卫；`allocate_bucket` 不查 open_buckets（只查
  rw_devs、freespace 树、data_type）；`reclaim_bucket` 先查 open（-16）
  再查 rw（-16，同码）；`discard_bucket` 先查 queued（-11）再查 rw
  （-11，同码）。
- `set_device_rw(dev,false)` 在 open 桶存在时 -16（等 open write points
  排空，background.c:1690-1722）；reopen 后 rw_devs 从 devs_online
  重建（engine.rs:1687-1700），模型需在 flush-reopen 操作后重置
  device_rw。
- 错误码同值分支可合并断言（open/rw 都 -16），但语义注释需区分。
