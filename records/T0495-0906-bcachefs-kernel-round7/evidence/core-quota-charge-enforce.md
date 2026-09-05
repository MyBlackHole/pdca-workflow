---
schema: pdca.asset/v1
id: ontology:domain/core-quota-charge-enforce
type: domain
layer: Knowledge
status: active
summary: 配额预留联动 + 三档收费 + 超限强制 + 迁移回滚
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-vfs-folio-reservation-writeback
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 用户组项目配额收费、预留联动、超限强制、属主迁移场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/fs/quota.c 在仓库中存在且含 bch2_quota_acct 定义"
- name: constraints
  desc: 收费强制前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认三档语义、超限三态、迁移回滚三条前提在引用代码中有对应实现"
---

# 配额预留联动与超限强制

沉淀自 T0495（内核第七轮；配额实际在 `fs/fs/quota.c`，不在
`fs/quota/`）。对照 bcachefs `fs/fs/quota.c`、`fs/vfs/io.h`、
`fs/vfs/io.c`、`fs/vfs/fs.c`。

## 核心概念

1. **内存预留与落账联动**：预留按模式选检查档，成功累加 inode
   预留与请求扇区；落账有预留直接扣，否则走警告收费；归还以
   负数返还（`bch2_quota_reservation_add`、
   `__bch2_i_sectors_acct`）。
2. **三档收费语义分层**：NOCHECK 用于重建回滚直接放行；PREALLOC
   用于创建预留先验；WARN 用于落账驱逐删除；inode 数创建用
   预留档、失败用警告档回滚（`bch2_quota_check_limit`）。
3. **超限强制三态**：硬限非特权直接拒；软限首次置定时器发警告，
   超时仍超才拒；减量清警告发回落通知
   （`ignore_hardlimit`、`prepare_warning`）。
4. **内存表两阶段提交**：按 qid 取表，按类型序全加锁，先对所有
   类型做检查，任一失败全不加，全过才累加，最后发警告
   （`bch2_quota_acct`）。
5. **迁移与失败回滚**：过滤相同属主；以块数加预留做迁移； setattr
   先迁新属主，事务失败再迁回旧属主防与磁盘分歧；项目号仅迁
   单类型（`bch2_fs_quota_transfer`）。
6. **启动重建只读扫描**：先恢复限额默认，再扫限额表，最后扫
   inode 仅主卷累加且全用免检档（`bch2_fs_quota_read`）。
7. **quotactl 记账与强制分离**：启用禁记账后开；删除要求先禁用
   后删全表；查态置位；改信息仅允定时器与警告域
   （`bch2_quota_enable/disable/remove`）。

## 复用指南

- 预留与落账必须联动记账，禁止两套独立数字。
- 收费分档（免检/预留/警告）必须语义分层，禁止一档走天下。
- 属主迁移失败必须迁回，禁止与磁盘分歧。
