---
schema: pdca.asset/v1
id: ontology:domain/core-fsck-interactive-error-handling
type: domain
layer: Knowledge
status: active
summary: 拓扑双路径 + 事务转储 + 写错超时降级 + 提问解锁
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-fsck-autofix-graded-self-healing
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 拓扑错误恢复内外路径、IO 错误降级、交互式修复提问场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/init/error.c 在仓库中存在且含 __bch2_fsck_err 定义"
- name: constraints
  desc: 交互处理前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认内外路径分流、降级三守卫、提问先解锁三条前提在引用代码中有对应实现"
---

# 交互式错误处理与降级

沉淀自 T0494（内核第六轮）。对照 bcachefs `fs/init/error.c`、
`fs/init/error.h`、`fs/init/damage.c`、`fs/vfs/ioctl.c`。

## 核心概念

1. **拓扑错误恢复内外双路径**：非恢复期置位后走不一致错误并
   抛修复需求；恢复期内改跑显式拓扑检查 pass，不成再抛同码
   （`__bch2_topology_error`）。
2. **事务转储随错**：trans 非空时追加事务更新文本再判策略；
   致命错仅当本次导致转 RO 才打印（`bch2_fs_trans_inconsistent`、
   `bch2_fatal_error`）。
3. **写错超时降级三守卫**：原子计数 + 首错打点 + 入队（已入队
   放回引用）；到期校验非移除非停止非只读才置设备 RO，不成
   则整 fs 紧急只读；成功 IO 清零计时
   （`bch2_io_error`、`bch2_io_error_work`）。
4. **提问期短解锁升级**：无通道直接否；有事务先解锁并设 2 秒
   升级点，超时转长解锁重试，问完重锁
   （`bch2_fsck_ask_yn`、`do_fsck_ask_yn`）。
5. **动作语法糖**：问句尾 `?` + 末逗号切自定义动作；fix 转
   fixing 时态；修复落事务日志，成败分计数
   （`prt_actioning`、`__bch2_fsck_err`）。
6. **损伤删查**：删键随 inode 同事务，不存在直接返；白化按卷
   过滤删，无祖先保留则实删否则转白化隐藏；查询分单点过滤
   与祖先并集归并（`bch2_damage_delete`、`bch2_damage_clear`、
   `bch2_damage_accumulate`）。

## 复用指南

- 恢复内外必须分流：外抛需求、内跑显式 pass，禁止同一路径。
- 设备降级必须三守卫 + 超时，禁止单错即降级。
- 提问必须先解锁事务 + 超时升级，禁止持锁等用户。
