---
schema: pdca.asset/v2
id: ontology:domain/core-userspace-device-manage
type: domain
layer: Knowledge
status: active
summary: 设备增删上下线改态扩容疏散全命令集
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-userspace-device-scan
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 设备增删、上下线、改态、扩容、疏散命令场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 src/commands/device.rs 在仓库中存在且含 cmd_device_add 定义
  evidence_level: unclassified
- name: constraints
  desc: 设备命令前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认在线离线分流、强制分档、失败回滚三条前提在引用代码中有对应实现
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

# 设备管理全命令集语义

沉淀自 T0504（20 轮第 3 轮；现树旧形态）。对照 bcachefs
`src/commands/device.rs`。

## 核心概念

1. **增删双路径分发**：在线离线分流，在线调内核，离线自启停
   后台任务；离线打开禁清运重整（`cmd_device_add`）。
2. **参数继承现有系统**：在线取 sysfs，离线取选项，组装后触
   发 udev 落定（`device_add_format`）。
3. **标识解析加归属校验**：序号直通，路径开盘比 UUID；序号必
   另给路径（`open_dev/resolve_dev`）。
4. **上下线不对称**：上线仅路径无强制，下线先取序号，强制映
   射降级位（`cmd_device_online/offline`）。
5. **删除三档强制**：默认降级档，加级加数据丢失档，再加元数据
   丢失档（`cmd_device_remove`）。
6. **在线改态加离线直写**：在线调内核，离线读超块持锁直写，初
   始化拒防跳写，临时清禁写标志（`set_state_offline`）。
7. **扩容失败回落离线**：在线算桶调内核，失败且路径存在转离
   线，要求恰一盘在线；离线收缩直接错
   （`cmd_device_resize`）。
8. **疏散两跳置态加轮询**：先验版本，再读写转只读转逐出，写触
   发唤醒，每秒求和归零提示删盘（`cmd_device_evacuate`）。

## 复用指南

- 设备变更必须在线离线双路径，离线路径禁后台任务。
- 破坏性操作必须分档强制，默认档最保守。
- 失败必须回落离线路径，禁止直接报错。
