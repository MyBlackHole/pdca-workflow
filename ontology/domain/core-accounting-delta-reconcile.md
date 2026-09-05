---
schema: pdca.asset/v1
id: ontology:domain/core-accounting-delta-reconcile
type: domain
layer: Knowledge
status: active
summary: 记账双轨delta + 类型矩阵 + 归并读 + 自愈调度
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 磁盘用量记账、启动归并重建、记账自愈、容量视图场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/alloc/accounting.c 在仓库中存在且含 bch2_accounting_read 定义"
- name: constraints
  desc: 记账归并前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认双轨语义、归并累加、自愈触发三条前提在引用代码中有对应实现"
---

# 记账双轨 delta 与归并重建

沉淀自 T0495（内核第七轮）。对照 bcachefs
`fs/alloc/accounting.c`、`fs/alloc/accounting_format.h`、
`fs/alloc/replicas.c`、`fs/alloc/buckets.c`。

## 核心概念

1. **双轨 delta 机制**：磁盘 btree 存写缓冲 delta + 内存数组；
   同位合并，归零剔除；提交钩子以日志位赋唯一版本并累加，
   回滚取负再加一次（`bch2_disk_accounting_mod_normal`）。
2. **类型矩阵与非内存特例**：11 种记账类型；inum 为非内存型，
   内存读遇非内存必断言走 btree；位与磁盘位互转
   （`BCH_DISK_ACCOUNTING_TYPES`）。
3. **启动双流归并读**：清空内存用量，定位日志记账区间，关自动
   改手动双流归并，旧版本标覆盖，非内存整段跳，同位累加，
   最后排序重建预留与用量（`bch2_accounting_read`）。
4. **自愈调度**：下溢删零、失配补差、引用错均显式跑
   check_allocations；btree 与内存比对告警
   （`accounting_key_check_sanity`、`bch2_gc_accounting_done`）。
5. **副本表归一检索**：新副本先排序归一化，再二分查；快路径
   命中返零，否则双锁慢路径加表落盘；缓存特化单设备
   （`bch2_mark_replicas`）。
6. **容量短视图与隐藏扣减**：一次性求和，容量扣隐藏，已用取
   数据与预留较小者，空闲相减；代际递增使旧预留失效
   （`__bch2_fs_usage_read_short`）。

## 复用指南

- 记账必须双轨（持久 delta + 内存快照），提交钩子赋唯一版本。
- 启动重建用双流归并，旧版本标覆盖而非删除。
- 失配必须显式调度修复 pass，禁止静默补差。
