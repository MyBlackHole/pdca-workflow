---
schema: pdca.asset/v2
id: ontology:domain/core-userspace-fsck-routing
type: domain
layer: Knowledge
status: active
summary: fsck在线三选路由 + 版本仲裁 + fd中继取码
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
  desc: 文件系统检查路由选择、版本错位仲裁、进度中继场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 src/commands/fsck.rs 在仓库中存在且含 cmd_fsck 定义
  evidence_level: unclassified
- name: constraints
  desc: 路由中继前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认在线优先、版本双向命中、中继取码三条前提在引用代码中有对应实现
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

# fsck 三选路由与中继

沉淀自 T0503（20 轮第 2 轮；现树旧形态）。对照 bcachefs
`src/commands/fsck.rs`。

## 核心概念

1. **在线优先三选**：已挂载走在线查，否则内核离线，失败兜底
   用户态（`cmd_fsck`）。
2. **版本错位仲裁**：试开读三方版本，双向区间命中才用内核并
   打印版本（`should_use_kernel_fsck`）。
3. **选项互斥**：用户已设精选 pass 则基线不插全量，防覆盖
   （`recovery_passes`）。
4. **显式空转**：自动修复直接打印挂载时已查返回，不静默成功
   （`auto_repair`）。
5. **fd 双向中继取码**：非阻塞轮询双向桥接，终以关 fd 返回值
   退出（`splice_fd_to_stdinout`）。
6. **非块设备转 loop**：组控制报文打控制设备，事后统一释放；
   仅内核缺失才回退用户态（`loopdev_alloc`）。
7. **退出码叠加**：用户态结果与关机错按位或退出
   （`run_userspace_fsck`）。

## 复用指南

- 检查路由必须在线优先，版本错位必须仲裁，禁止硬编码一路。
- 进度中继必须双向桥接并以关闭返回值退出，禁止丢退出码。
