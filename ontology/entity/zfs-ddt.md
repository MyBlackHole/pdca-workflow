---
schema: pdca.asset/v2
id: ontology:entity/zfs-ddt
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/zfs-ddt/3.1.0
summary: OpenZFS zfs-2.3.0：DDT/BRT边界重建，旧状态图与伪接口撤回
relations:
  specializes:
  - ontology:concept/domain-entity
  relates_to:
  - ontology:entity/zfs-zio
  - ontology:domain/zfs-crypto
  - ontology:pattern/production-ontology-scientific-gate
  - ontology:pattern/research-diagram-methodology
attributes:
- name: ddt_lock
  desc: 锁接口不是插入接口
  constraint: ddt_enter(ddt_t*)进入ddt_lock；不等价于新增DDT项
  testable_signal: 固定ddt.c签名和函数体核对；ddt_enter(ddt,bp,tx)当新增接口应拒绝
  evidence_level: source
- name: reference_models
  desc: DDT/BRT职责分离
  constraint: 去重写与显式块克隆分开；不得把去重命中变成hole
  testable_signal: 固定zio_ddt_write和brt_pending_apply_vdev来源，加真实池读回及引用观测，后者NOT_RUN
  evidence_level: source
revision: 3.1.0
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
  content_review: 2026-09-12; pinned sources only; not latest-release certification
validation:
  claim_status: source_checked_scoped
  adoption: claim_review_required
  checked_claims:
  - DDT_ENTER_LOCK
  - DDT_NOT_HOLE
  - BRT_CLONE
  - BRT_DDT_FALLBACK
  source_refs:
  - https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/ddt.c
  - https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/include/sys/ddt.h
  - https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/zio.c
  - https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/brt.c
  runtime_validation: not_run
---

# ZFS DDT与BRT：固定版本的职责边界

本节点只适用OpenZFS **zfs-2.3.0**的下列已核对事实。旧版的HOLE/EVICT状态图、brt_add伪接口、固定三槽结构与“按图即可实现”示例撤回；原文可由v3包/变更补丁追溯，不能继续当oracle。

## 定义与调用边界

DDT支撑自动去重；`ddt_enter(ddt_t *ddt)`只进入互斥锁，`ddt_exit`退出。实体布局有传统和flat分支，不能把省略结构当成实际ABI。[ddt.c](https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/ddt.c)、[ddt.h](https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/include/sys/ddt.h)。

`zio_ddt_write`在DDT锁内lookup，按所需DVA和在途I/O处理复用/写入；命中复用不是把数据改成hole。`zio_nop_write`是独立阶段，不能仅凭去重命中手动跳过底层I/O。[zio.c](https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/zio.c)。

BRT管理显式块克隆引用。在`brt_pending_apply_vdev`中，DEDUP块先尝试`ddt_addref`；**只有全部pending引用被DDT承接**才移除pending项并继续。无法全部承接时存在后续BRT路径，不能反向断言DEDUP块永远不进入BRT。[brt.c](https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/module/zfs/brt.c)。

## 回归与采用范围

[存储与内容回归](../../tests/content-regression.md)分开定义普通去重命中、非去重块克隆、DDT成功承接的克隆以及承接失败路径。每例要保存固定构建、特性、输入数据、计数/调用证据与数据读回。不得使用生产池进行故障注入。

本次只有源码核对，未创建ZFS池、未证明完整持久化和并发行为。已核对的语义纠错可用于建模；实现/验收必须继续绑定真实目标源码与受控测试。缺少观测时结果unknown，不从源码关键词推导运行PASS。
