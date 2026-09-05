---
schema: pdca.asset/v1
id: ontology:domain/core-dio-read-engine
type: domain
layer: Knowledge
status: active
summary: DIO读对齐截断 + 分片闭包 + 脏旗防回挂
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-dio-write-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 直接 IO 绕页缓存读取、对齐整形、分片下发场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/vfs/direct.c 在仓库中存在且含 __bch2_direct_IO_read 定义"
- name: constraints
  desc: 直通读取前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认对齐门槛、尾部归还、防回挂三条前提在引用代码中有对应实现"
---

# DIO 读直通引擎

沉淀自 T0500（内核第十二轮）。对照 bcachefs `fs/vfs/direct.c`、
`fs/vfs/direct.h`。

## 核心概念

1. **对齐截断与回补**：入口要求整块对齐；尾部非整块暂扣，末尾
   归还（`__bch2_direct_IO_read`）。
2. **分片闭包**：首 bio 内嵌，超限循环拆分，计数器同步；同步
   等待，异步经完成回调（`bch2_direct_IO_read_endio`）。
3. **脏旗防回挂**：用户回写迭代器置脏防 loop 回挂死锁
   （`should_dirty`）。
4. **与既有节点边界**：写引擎节点管写入，本节点管读取；直接
   读裁剪是其子集特写。

## 复用指南

- 直通读必须对齐整形 + 尾部归还，禁止静默截断。
- 分片必须计数器同步，异步经完成回调。
