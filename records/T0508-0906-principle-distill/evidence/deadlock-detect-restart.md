---
schema: pdca.asset/v1
id: ontology:pattern/deadlock-detect-restart
type: pattern
layer: Knowledge
status: active
summary: 等待图环检测加幂等重启消灭死锁模式
source_task: T0505
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:domain/core-six-slowpath-wakeup
attributes:
  - name: applicability
    desc: 多锁多事务并发、锁序无法静态保证场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-six-slowpath-wakeup 存在
  - name: consequences
    desc: 死锁自愈、要求事务幂等、检测仅阻塞时运行
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
  - name: violations
    desc: 不用本模式的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# 等待图环检测加幂等重启

来源：T0505 提炼，T0508 扩充；源节点
`core-six-intent-seq-deadlock-free-locking`、
`core-six-slowpath-wakeup`；对照 bcachefs `fs/btree/locking.c`、
`fs/util/six.c`。

## 问题

多事务多锁并发时锁序无法静态保证，传统方案靠全局锁序（限制并发）
或超时重试（误杀正常等待）。

## 方案

1. **睡眠前走等待图**：成环选一事务全放锁重启；仅阻塞时运行，
   不污染快路径（`bch2_six_check_for_deadlock`）。
2. **中止偏好**：不可败优先保，否则最年轻者 abort
   （`break_cycle`、`btree_trans_abort_preference`）。
3. **RCU 快照遍历**：解引用加无睡分配，防并发唤醒抖动；双校验
   去非等待者（`lock_graph_remove_non_waiters`）。
4. **trylock 回补唤醒**：失败且有对立等待者返回要求调用方补唤醒，
   防伪唤醒丢事件（`__do_six_trylock`）。
5. **定向唤醒**：读唤醒全部同类，写按等待时间选最早者单唤；发布
   配对内存屏障（`__six_lock_wakeup`）。
6. **幻影防护**：检测前比对哈希快照，不等强制重遍历，加内存屏障
   防双漏检（`locking.c:636-660`）。

## 后果

死锁自愈，无需全局锁序；前提是事务层全幂等可重启，否则重启即
corrupt；检测仅阻塞时运行。

## 违反后果

- 全局锁序：并发度锁死，扩展性到头。
- 超时重试：正常长等待被误杀，抖动雪崩。
- 丢唤醒：等待者永睡，表现为随机挂死，极难排查。
