---
schema: pdca.asset/v2
id: ontology:domain/core-userspace-wait-multipath
type: domain
layer: Knowledge
status: active
summary: 事件驱动等盘 + dev_idx判齐 + 多路径归一防环
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
  desc: 开机等盘、多路径去重、成员判齐场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 src/commands/wait_devices.rs 在仓库中存在且含 every_device_is_initialized 定义
  evidence_level: unclassified
- name: constraints
  desc: 等盘判齐前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认事件阻塞、三重过滤、防环深度三条前提在引用代码中有对应实现
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

# 事件等盘与多路径归一

沉淀自 T0502（20 轮第 1 轮）。对照 bcachefs
`src/commands/wait_devices.rs`、`src/device_scan.rs`、
`src/device_multipath.rs`。

## 核心概念

1. **事件驱动等盘**：先全量加入，再监听阻塞等增删改事件，
   错即错；仅接受目标 UUID（`cmd_wait_devices:32-68`）。
2. **三重过滤加判齐**：初始化状态、类型、UUID 三过滤；读超块
   容忍竞态消失盘；二次核对 UUID；墓碑槽告警丢弃；按设备序
   号集合判齐；固定删后加防重复计数
   （`WaitInitialized::add`、`every_device_is_initialized`）。
3. **多路径双层跳过加归一**：udev 路径查属性，无则查 sysfs；
   回落扫同样查持有者；命中归一到映射路径；显式路径仅告警
   不拦截（`should_skip_multipath_component`）。
4. **顶层归一与防环**：循环剥分区前缀识别嵌套；以 dm 标识为
   唯一判据；沿持有者递归上溯顶层，限深防环；以设备号防陈
   旧重定向（`find_multipath_holder_inner`）。

## 复用指南

- 等盘必须事件阻塞，禁止盲轮询；判齐必须按序号集合。
- 多路径必须归一顶层 + 限深防环，禁止双算容量。
