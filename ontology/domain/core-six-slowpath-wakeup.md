---
schema: pdca.asset/v1
id: ontology:domain/core-six-slowpath-wakeup
type: domain
layer: Knowledge
status: active
summary: six trylock 回补 + 降级升级 + 定向唤醒 + 等待图快照
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 读写锁快慢路径、锁模式转换、公平唤醒与死锁检测场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/util/six.c 在仓库中存在且含 __do_six_trylock 定义"
- name: constraints
  desc: 快慢路径前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认伪唤醒回补、转换原子性、发布配对三条前提在引用代码中有对应实现"
---

# six 慢路径唤醒与等待图快照

沉淀自 T0492（内核第四轮）。对照 bcachefs `fs/util/six.c`、
`fs/util/six.h`、`fs/btree/locking.c`。

## 核心概念

1. **trylock 快慢分支 + 伪唤醒回补**：intent 走 CAS，read 走
   percpu 计数 + 屏障后查写持，write 预加写持后查计数；失败
   且有对立等待者返回要求调用方补唤醒，防伪唤醒丢事件
   （`__do_six_trylock`）。
2. **降级/试升级/转换原子路径**：降级为加读 + 解 intent；试升级
   CAS 确认无 intent 后减读加 intent；同型转换直接成功
   （`six_lock_downgrade`、`six_lock_tryupgrade`）。
3. **contended 跳检 + 慢路径休眠机**：跳过首次 trylock 省 CAS；
   写预占后入队，乐观自旋快返，否则让步循环睡；出错自摘，
   已得回滚（`__six_lock_slowpath`）。
4. **定向唤醒 + lockdep 集成**：读唤醒全部同类，intent/write
   按 slot 缓存时间选最早者单唤；slot 低 2 位存需求类型；
   发布配对内存屏障；非写全程 lockdep（`__six_lock_wakeup`）。
5. **等待图 DFS 快照与中止偏好**：percpu 显式栈，冲突判据为
   类型和 >1；RCU 解引用 + 快照入无睡内存防抖动；双校验去
   非等待者；按不可败优先、否则最年轻者 abort
   （`bch2_check_for_deadlock`、`break_cycle`）。

## 复用指南

- trylock 失败必须报告是否需补唤醒，禁止静默丢唤醒。
- 唤醒必须定向（最早等待者），禁止无脑广播。
- 死锁检测遍历必须用 RCU 快照 + 无睡分配，禁止持锁遍历。
