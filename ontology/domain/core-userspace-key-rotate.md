---
schema: pdca.asset/v1
id: ontology:domain/core-userspace-key-rotate
type: domain
layer: Knowledge
status: active
summary: 密钥多盘校验 + 原子替换 + 魔数判别 + 内存清零
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-userspace-unlock-keyring-policy
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 口令改去、多盘校验、密钥内存卫生场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 src/commands/key.rs 在仓库中存在且含 cmd_set_passphrase 定义"
- name: constraints
  desc: 密钥轮换前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认未挂载校验、持锁直写、哨兵验证三条前提在引用代码中有对应实现"
---

# 密钥轮换原子替换

沉淀自 T0504（20 轮第 3 轮）。对照 bcachefs
`src/commands/key.rs`、`src/key.rs`。

## 核心概念

1. **多盘解析加未挂载校验**：兼容单参与多参；禁启动打开；无
   加密直接错；明文格式直接读密钥，否则问询得明文
   （`parse_device_list`、`open_and_verify`）。
2. **改去原子替换**：新口令加密后持锁直写超块并吊销旧钥；去
   口令回写明文魔数（`cmd_set_passphrase`、
   `cmd_remove_passphrase`）。
3. **魔数判别加哨兵验证**：魔数字段判加密；派生后加解密并以
   解密后哨兵验对错（`sb_is_encrypted`、`encrypt_key`）。
4. **内存清零卫生**：口令密钥类型级清零；双输比对；非终端回
   落；去尾换行（`ZeroizeOnDrop`）。
5. **与既有节点边界**：解锁节点管开锁问询，本节点管改去轮换；
   无独立新增命令由改口令承担（现树实况）。

## 复用指南

- 改去密钥必须未挂载校验加持锁直写加吊销旧钥三连。
- 对错必须哨兵验证，禁止以加解密成功推断口令正确。
