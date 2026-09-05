---
schema: pdca.asset/v1
id: ontology:domain/core-vfs-folio-reservation-writeback
type: domain
layer: Knowledge
status: active
summary: folio双预留记账 + 免读快路 + 聚合回写 + 重映射
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-pagecache-buffered-direct-io
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 页缓存写预留、批量回写、重映射与打洞场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/vfs/pagecache.c 在仓库中存在且含 bch2_folio_reservation_get 定义"
- name: constraints
  desc: 预留回写前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认双预留、免读条件、失效循环三条前提在引用代码中有对应实现"
---

# folio双预留 + 聚合回写

沉淀自 T0494（内核第六轮）。对照 bcachefs
`fs/vfs/pagecache.c`、`fs/vfs/buffered.c`、`fs/vfs/io.c`。

## 核心概念

1. **folio 双预留记账**：按块对齐算磁盘与配额扇区，双加双放；
   部分预留按块截断；nofail 变体；快照跳过配额
   （`bch2_folio_reservation_get/put`）。
2. **write_begin 免读 + 越界清零**：整页覆盖/尾部/超尾三路免读
   直接清零，否则读页；再预留，失败未更新则重走确认
   （`bch2_write_begin`）。
3. **write_end 部分写重做**：未写满且未更新全页清零强制用户
   重写；锁下扩展 i_size；记脏时间戳（`bch2_write_end`）。
4. **writepages 聚合回写**：限流循环调单页写；跨尾页清零；
   快照扇区后解锁再按连续脏段组 bio 合并；同步标志透传
   （`bch2_writepages`）。
5. **readahead 批量读**：定量组 bio，插拔防调度时带锁阻塞；
   加页失败直接退出（`bch2_readahead`）。
6. **mmap/mkwrite**：fault 做映射死锁排序后透传；mkwrite 取
   快照读锁 + 防页错误启动，校验后预留置脏等稳定返回锁定
   （`bch2_page_fault`、`bch2_page_mkwrite`）。
7. **写前刷盘 + 失效循环**：刷盘加失效，忙重试，无页早退；
   被 DIO 写与重整调用；注释明示防 DIO 活锁
   （`bch2_write_invalidate_inode_pages_range`）。

## 复用指南

- 脏页必须双预留（磁盘 + 配额），缺一即超卖。
- 免读快路（全零/全覆盖）是写路径必备，禁止无条件读页。
- DIO 前必须刷盘 + 失效循环，忙重试而非一次失败。
