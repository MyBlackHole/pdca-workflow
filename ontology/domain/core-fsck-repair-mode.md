---
schema: pdca.asset/v1
id: ontology:domain/core-fsck-repair-mode
type: domain
layer: Knowledge
status: active
summary: fsck 修复模式模式（Fsck Repair Mode）
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
  testable_signal: "检查本文件 fsck-repair-mode 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# fsck 修复模式模式（Fsck Repair Mode）

## 适用场景

一致性检查入口（fsck_image）需要支持"检查→修复→复验"闭环时，修复
动作必须严格对齐上游 fsck 的 fix_errors 门控与 check_allocations
修复语义，且只修 verify 报告的错误类别。

## 模式要点

1. **单入口 + 模式枚举**：fsck_image(path, FixErrors::No/Yes) 对齐
   bch2_fs_fsck_errcode（单函数）+ fix_errors 选项（opts.h:132
   FSCK_FIX_no/yes）；不新增并行函数（约束 8）。No=只报错不修
   （-n → nochanges+fix_errors=no，fsck.rs:266-269），Yes=自动修复
   （-y → fix_errors=yes，fsck.rs:248-250）。
2. **修复动作双向**：check.c 的修复是"删除错误索引键 + 补齐缺失键"
   双向（bch2_check_alloc_key alloc/check.c:175-188：need_discard
   补键 175-179、freespace 补/删 185-188）。只做删除会漏掉"alloc 有
   状态但树缺键"的损坏。
3. **每键单事务**：对齐 delete_freespace_key（check.c:352-386 的
   bit_mod + trans_commit）；-12（ENOMEM）realloc 重试；非索引错误
   `?` 传播中止（对齐上游 ret），不部分修复后假装成功。
4. **修复必须落盘**：修复事务提交后需 flush_journal 再复验——journal
   replay 只重放已落盘事务，缺落盘时 reopen 后脏键复活（实测定位；
   对齐上游 fs.exit() 关盘语义 fsck.rs:457-460）。
5. **修复范围 = verify 报错类别**：只修 verify_bucket_indexes 报的
   FreespaceSet / NeedDiscardSet；守卫错误名（OpenBucketFree /
   NotRwBucketFree）不修复——上游为 skip 语义（bch2_bucket_is_open_safe
   discard.c:344-347 / bch2_dev_get_ioref discard.c:349-357），无 fsck
   修复动作，且这些是纯运行期内存不变量（open_buckets/rw_devs 不
   持久化，reopen 后天然为空）。
6. **修复场景由树的重建范围决定**：open_persistent 打开时
   rebuild_derived_state 会重建部分派生树（engine.rs:2014-2019 清
   4/5/8，need_discard 树保留）——不被重建的树的脏键跨 reopen 存活，
   才是持久化修复的真实场景；被重建的树的修复动作为防御性实现。
   写测试前先实验确认哪些树的脏键跨 reopen 存活。

## 关键语义（本实现确认）

- fsck_image(Yes) 流程：open_persistent（打开即重建派生态）→
  repair_derived_indexes（双向）→ flush_journal → verify_all。
- CLI 修复开关是 -y（auto_repair）而非 -f（force，fsck.rs:32-46
  三字段各自独立）；-n/-y 互斥（避免 fix_errors 双重设置歧义）。
- 损坏镜像的 CLI 级构造常不可达（脏键注入需内部 API），修复语义由
  库级测试承担，CLI 集成只覆盖模式行为与互斥——验收口径需在实现期
  澄清（grilling round）并写进 check-evidence。
