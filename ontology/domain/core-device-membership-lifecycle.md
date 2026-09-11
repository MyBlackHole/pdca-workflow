---
schema: pdca.asset/v2
id: ontology:domain/core-device-membership-lifecycle
type: domain
layer: Knowledge
status: active
summary: 设备成员槽位分配 + 删除双态 + 移除流水线回滚
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 多设备成员增删改、上下线、只读切换、移除数据迁移场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/sb/members.c 在仓库中存在且含 bch2_sb_member_alloc 定义
  evidence_level: unclassified
- name: constraints
  desc: 成员变更前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认槽位哨兵、删除双态、移除栅栏三条前提在引用代码中有对应实现
  evidence_level: unclassified
revision: 3.1.0
authority: reference
dcterms_modified: '2026-09-12'
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 设备成员全生命周期管理

沉淀自 T0495（内核第七轮）。对照 bcachefs `fs/sb/members.c`、
`fs/sb/members.h`、`fs/init/dev.c`、`fs/data/migrate.c`。

## 核心概念

1. **槽位分配与哨兵保留**：未满追加，否则复用 uuid 为零且最久
   未挂载空洞；255 号永不分配；DELETED 槽不复用，提示跑 fsck
   （`bch2_sb_member_alloc`）。
2. **删除槽双态与延迟清理**：快删写 DELETED 占位防指针复活，
   旧路径直接清零；clean 批量清零并落盘；存活判定排斥两者
   （`bch2_dev_remove`、`bch2_sb_members_clean_deleted`）。
3. **v1/v2 变长升级**：无 v2 按 v1 长拷贝建；从后向前搬移扩到
   新结构；旧版本回拷前部字节保挂载兼容
   （`sb_members_v2_resize_entries`）。
4. **合法性校验**：桶数上限、下限 512、桶不小于块与节点、位移
   上限、初始化互斥；v1/v2 逐成员调（`validate_member`）。
5. **移除分诊**：扫 DELETED 置移除位；缺失指针区分已移除与不
   存在，分别计数并触发恢复（`bch2_sb_members_to_cpu`）。
6. **IO 引用双轨与读写门控**：读写分轨枚举引用；按状态掩码过
   滤取在线盘；写仅读写盘放行；下线停对应轨
   （`bch2_dev_get_ioref`）。
7. **RO/RW 切换时序**：转只读先腾日志 → 排空开桶在途 → 停写 →
   停日志 → 异步丢弃 → 刷 EC 防背指针遗漏；逆向加回
   （`__bch2_dev_read_only`）。
8. **状态机与扫描联动**：同态直接返；转 rw/逐出/进出 rw 各发
   对应扫描；持久化夹在两次扫描间；离 rw 需容量校验或强制
   （`__bch2_dev_set_state`）。
9. **移除全流水线与失败回滚**：置移除栅栏 → 强转逐出 → 快/慢
   双路径迁数据 → 刷三类 pin → 下线禁读 → 删分配段 → 再刷 →
   副本回收 → 摘设备排空引用；失败清栅栏，仍在线调回读写
   （`__bch2_dev_remove`）。
10. **添加四阶段 fallthrough**：约束检查 → 槽位分配 → 多设备标
    记 → 初始化四阶段；上线经分裂脑检查 + 补索引 + 刷降级；
    下线双检读写能力；扩容禁缩并预发扫描
    （`bch2_dev_add`、`bch2_dev_online`）。

## 复用指南

- 成员槽位必须有哨兵保留与删除双态，禁止复用删除中槽位。
- 移除必须是带栅栏的全流水线 + 失败回滚，禁止半截摘设备。
- 状态转换必须联动对应扫描，持久化夹在扫描之间。
