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
---

# 等待图环检测加幂等重启

来源：T0505 提炼；源节点 `core-six-intent-seq-deadlock-free-locking`、
`core-six-slowpath-wakeup`；对照 bcachefs `fs/btree/locking.c`、
`fs/util/six.c`。

## 问题

多事务多锁并发时锁序无法静态保证，传统方案靠全局锁序（限制并发）
或超时重试（误杀正常等待）。

## 方案

睡眠前走事务等待图 DFS，成环选一事务全放锁重启：不可败优先保，
否则最年轻者 abort。遍历用 RCU 快照加无睡分配；trylock 失败报告
是否需补唤醒防伪唤醒丢事件；唤醒定向最早等待者。

## 后果

死锁自愈，无需全局锁序；前提是事务层全幂等可重启，否则重启即
corrupt；检测仅阻塞时运行，不污染快路径。
