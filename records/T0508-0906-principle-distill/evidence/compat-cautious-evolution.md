---
schema: pdca.asset/v1
id: ontology:principle/compat-cautious-evolution
type: principle
layer: Knowledge
status: active
summary: 兼容审慎演进原则
source_task: T0508
relations:
  specializes: [ontology:principle]
  relates_to:
  - ontology:domain/core-format-compat-stable-evolution
  - ontology:domain/core-superblock-readback-validation
  - ontology:domain/core-sb-error-persistence-display
attributes:
  - name: applicability
    desc: 磁盘格式与跨版本互操作演进
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-format-compat-stable-evolution 存在
  - name: violations
    desc: 违反本原则的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# 兼容审慎演进

来源：T0508 提炼；源节点 `core-format-compat-stable-evolution`、
`core-superblock-readback-validation`、`core-sb-error-persistence-display`；
对照 bcachefs `fs/bcachefs_format.h`、`fs/sb/downgrade.c`、
`fs/sb/io.c`、`fs/opts.c`、`fs/errcode.h`。

## 背景问题

文件系统磁盘格式要演进十年以上，新旧内核混用是常态。演进一旦
出错就是静默 corrupt：老内核把新字段当旧语义读，写回去即永久
破坏。bcachefs 用四层防线把"误认"变成"拒挂"。

## 约定

1. **新特性显式位加兼容位门控**：每个新特性占 FEATURE 位，
   行为变更另占 COMPAT 位；老内核见不识别位直接拒挂，绝不
   尝试解释。依据：`BCH_COMPAT_stripe_frag_accounting` 门控碎片
   会计，老盘零值与新盘 stale 由位区分。
2. **内存枚举与磁盘位显式映射**：内存 enum 随意增删，磁盘只存
   stable 位，双向表重映射。依据：`passes_to_stable_map` 让恢复
   pass 随便加而不污染盘上位。
3. **升级降级表驱动**：按版本声明所需 pass 与静默错误，写前校验
   版本；超块读写全拷贝仲裁取最优，写后读回比对，变小判静默
   丢弃、变大判篡改。依据：`downgrade_table`、`read_back_super`。
4. **多后端单源生成**：选项表、错误码、校验表凡 N 后端消费必单
   宏源生成；未知输入默认拒绝或兜底，未知码不崩
   （`BCH_OPTS`、`X(class,err)`、codegen 生成 Rust 绑定）。
5. **错误段严格校验**：拒零计数与乱序，展示拷贝后排序不改盘序，
   饱和钳位不回绕。依据：`bch2_sb_errors_validate`。

## 违反后果

- 无门控位：老内核静默 corrupt 新格式，无法回退。
- 内存枚举直落盘：一次重排即全版本不兼容。
- 多后端手写同步：必漂移，mount/sysfs/sb 三处选项打架。
- 未知输入误判成功：错口令给垃圾密钥之类后移爆炸。
