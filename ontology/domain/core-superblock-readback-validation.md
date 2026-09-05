---
schema: pdca.asset/v1
id: ontology:domain/core-superblock-readback-validation
type: domain
layer: Knowledge
status: active
summary: 超块选优读 + 写前校验读回 + 错误计数有序合并
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-format-compat-stable-evolution
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 多副本元数据读写、静默丢弃检测、错误计数持久化场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/sb/io.c 在仓库中存在且含 read_back_super 定义"
- name: constraints
  desc: 读写校验前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认选优仲裁规则、读回比对分支、归并无损三条前提在引用代码中有对应实现"
---

# 超块选优读 + 写前校验读回

沉淀自 T0491（内核遗漏扫描）。对照 bcachefs `fs/sb/io.c`、
`fs/sb/errors.c`。

## 核心概念

1. **全拷贝选优读**：先读主扇区取内嵌 layout，失败才读独立
   layout；轮询全部 sb_offset 取最高 seq（平局后扫胜免回读），
   防撕裂写/单槽掉队/备份腐烂；支持定点调试
   （`read_super_and_backups`、`read_backup_supers`）。
2. **写前校验 + 读回防静默丢**：持 sb_lock 递增 seq 同步成员；
   逐盘 validate，拒写条件明确；先全盘读回记 scratch.seq，写
   后比对：变小为静默丢弃，变大为他进程篡改必 ERO
   （`__bch2_write_super`、`read_back_super`）。
3. **错误计数有序合并**：内存按 id 有序插入增量；落盘带
   nr/first/last；读合并 v2 + legacy 排序归并，降级后老内核
   追加段求和取时间并集，下次写回折叠无损
   （`bch2_sb_error_count`、`bch2_sb_errors_to_cpu`）。

## 复用指南

- 多副本元数据读必须全拷贝仲裁取最优，禁止只读主副本。
- 写后必须读回比对，静默丢弃与篡改要有区分明确的报错。
- 计数类持久化用有序合并，降级/升级路径无损是硬要求。
