---
schema: pdca.asset/v1
id: ontology:domain/core-ec-stripe-geometry
type: domain
layer: Knowledge
status: active
summary: 条带几何结构：变长段与拓宽计数
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-rs-algorithm
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 条带磁盘结构解析、拓宽计数理解场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文结构字段与 format.h 对应"
- name: constraints
  desc: 结构解析前提
  constraint: 见正文
  testable_signal: "通读正文三节，确认字段语义、变长顺序、拓宽饱和三条在引用代码中有对应"
---

# 条带几何结构

沉淀自 T0543。对照 bcachefs `fs/data/ec/format.h`
（`struct bch_stripe`）。

## 算法原理

1. **固定头**：扇区数、算法 4 位、待重整标志、拓宽计数 3 位、
   总块数、冗余数、校验粒度与类型、盘标签。一次读出全部几何，
   免二次寻址。
2. **变长三段**：指针数组、校验二维数组（按粒度分片）、每块扇
   计数组。顺序固定，作者自注校验应垫后（XXX 注释）。
3. **拓宽计数**：3 位饱和 0-7，记本条在当前更宽几何下可增数据
   块数；写者须钳制。以读写成员视图为准，瞬时上下线不触发全
   盘重写（`bch2_disk_label_ec_rw_member_devs`）。

## 解决了什么问题

- **一次读出全几何**：指针、校验、块大小全在一条键里，重建时
  零额外寻址。相对分开存三处，少两次 btree 查询。
- **在线拓宽不断服**：加盘后旧条带可增数据块，无需全量重写。
  拓宽计数让新几何复用旧条带，扩容平滑。
- **瞬时抖动不扰民**：以配置态而非在线态算拓宽，盘闪断不触发
  全盘重写风暴。

## 引入了什么问题

- **变长解析脆弱**：顺序错一位全错，且是静默 corrupt。缓解靠
  固定顺序加 XXX 技术债标记，但标记不等于修复。
- **3 位太小**：0-7 上限，超宽几何表达不了。作者自承 targets
  应 16 位（XXX 注释），v2 格式才能解。
- **校验垫后是债**：校验在中段导致块计数不可达（未知校验类型时），
  布局失误的长期代价。

## 实际问题与修复

1. **超大目标组误判可建**：目标组超 u8 折叠为无标签门，误判全盘可建（`9281beaa2`）。修复：前置拒绝超大组。防复发：门控与执行用同一拒绝谓词，不各算各的。
