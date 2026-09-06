---
schema: pdca.asset/v1
id: ontology:domain/core-ec-rs-algorithm
type: domain
layer: Knowledge
status: active
summary: EC底层RS算法复用与分级恢复
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-read-replica-pick
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 纠删底层编解码、内核版本兼容、分级恢复场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 raid_gen/raid_rec 在仓库中存在"
- name: constraints
  desc: 算法复用前提
  constraint: 见正文
  testable_signal: "通读正文三段，确认复用内核库、冗余上限、分级恢复三条在引用代码中有对应实现"
---

# EC 底层 RS 算法复用与分级恢复

沉淀自 T0542 补充。对照 bcachefs `fs/data/ec/io.c:20-110`。
本节点讲调用封装层算法（复用什么、怎么分级），数学原理见
rs-principle 节点，条带生命期见 ec-repair 节点。

## 算法原理

1. **复用内核库加版本垫片**：XOR 与 syndrome 调内核 `raid/pq.h`、
   `raid/xor.h`；7.1 改名 xor_blocks→xor_gen、7.2 改 raid6 接口，
   自写 shim 抹平，调用方版本无关（`io.c:20-54`）。
2. **生成分两档**：1 parity 用 raid5 算法，2 parity 加 raid6
   syndrome；超 2 直接 BUG，上限 RAID6（`raid_gen:67`）。
3. **恢复按坏数分级**：0 坏直返；1 坏分数据坏与 parity 坏；2 坏分
   双数据、数据加 P、数据加 Q、双 parity 四分支；超 2 直接 BUG
   （`raid_rec:76`）。
4. **raid5 恢复三步**：换首、拷贝、异或（`raid5_recov:56`）。

## 解决了什么问题

- **数学正确性外包**：RS 域运算 bug 是静默 corrupt 级灾难，复用
  千万人审计的内核库，把最难验证的部分交给最可信的实现。
- **版本漂移隔离**：内核 7.1/7.2 两次改名接口，shim 层一次抹平，
  上层调用十年不变。
- **恢复路径完备**：坏数 0/1/2 全分支覆盖，每分支独立函数，漏分支
  编译期不可见但测试可覆盖。

## 引入了什么问题

- **信任传递风险**：内核库 bug 即 bcachefs bug，且无法本地修复，
  只能等上游或打补丁。缓解靠版本垫片层的回归测试。
- **上限锁死 RAID6**：超 2 冗余需求无法表达，想做 3 parity 得换
  库重写分级。bcachefs 认为双盘容错足够，锁死是刻意取舍。
- **垫片维护税**：每次内核改名加一层宏，shim 越堆越厚。缓解靠
  条件编译隔离旧版，新版直调。
