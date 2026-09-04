---
schema: pdca.asset/v1
id: ontology:domain/core-fsck-repair-fault-injection
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-fsck-repair-fault-injection/1.0.0
summary: fsck 修复路径故障注入
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
  testable_signal: "检查本文件 fsck-repair-fault-injection 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# fsck 修复路径故障注入

> 沉淀自 T0200（V-T0200-001 confirmed），前置：T0196 恢复故障矩阵、
> T0198 修复路径、T0199 并发交错注入。

## 核心概念

fsck_image(FixErrors::Yes) 修复路径的故障行为验证：修复事务中断与
落盘失败的失败语义与恢复能力。对齐 T0196 的 RecoveryFaultPoint
一次性注入模式，覆盖 T0198 未验证的修复路径故障。

## 注入点设计（对齐上游）

| FsckFaultPoint | 注入内容 | 位点（上游锚点） | 结果 |
|---|---|---|---|
| DuringRepairRestart | -4（trans restart） | 修复事务提交前（trans_maybe_inject_restart，commit.c:1390） | 走 bch2_trans_begin 重试循环收敛（lockrestart_do，iter.h:1115-1127） |
| DuringRepairOom | 硬 -12（restarted==0，无 realloc） | 同上 | 不满足 realloc 重试条件 → 错误传播中止（Err(Transaction(-12))） |
| AfterRepairBeforeFlush | flush 前注入失败 | fs.exit() 落盘点（fsck.rs:457-460） | Journal 错误不误报成功；未落盘修复被 journal replay 丢弃 |

关键点：fault 一次性消费（&mut Option，首个事务吞掉，后续不受影响）。

## 关键语义

1. **修复事务 -4 必须重试**：上游 lockrestart_do 对 transaction_restart
   循环重试；bit_mod_sync 的 -4 分支与 reclaim/allocate 既有模式一致
   （`ret == -4 || (ret == -12 && realloc_bytes_required != 0)`）。
2. **真 OOM vs realloc**：-12 且 realloc_bytes_required==0（restarted
   ==0）→ 硬失败传播；注入真 -12 直接构造该条件，不误入重试循环。
3. **落盘失败恢复**：修复提交但未落盘 → 重跑时 journal replay 只回放
   已落盘事务，未落盘修复丢弃；open_persistent 重建派生态（清 4/5/8
   树）→ 重新修复收敛 → verify_all 通过。修复幂等是恢复的前提
   （从 alloc 树派生期望集，重跑重算）。
4. **矩阵模式**：所有失败注入点必须 Err（不发布虚假成功）；restart
   注入是重试非失败，从"必须失败"矩阵排除。

## 复用指南

- 新故障注入任务：复制 FsckFaultPoint/RecoveryFaultPoint 形态
  （枚举 + 私有带 fault 入口 + 公开入口传 None 零改动 + 一次性消费）。
- 测试断言：矩阵测试遍历失败注入点断言 Err；恢复验证用"重跑无注入
  成功 + open_persistent verify_all"。
- 注入位点规则：永远选上游既有的错误/重试边界（trans 提交前、
  flush 前），注入值走既有分支，禁止新逻辑分支。
