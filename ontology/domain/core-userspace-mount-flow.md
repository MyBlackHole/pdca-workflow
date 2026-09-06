---
schema: pdca.asset/v1
id: ontology:domain/core-userspace-mount-flow
type: domain
layer: Knowledge
status: active
summary: 挂载只读重试 + 三路选项分流 + 无降级问答证伪
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
  desc: 用户态挂载流程、只读重试、选项分流场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 src/commands/mount.rs 在仓库中存在且含 mount_inner 定义"
- name: constraints
  desc: 挂载流程前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认只读重试条件、选项分流规则、无问答证伪三条前提在引用代码中有对应实现"
---

# 用户态挂载流程（现树旧形态）

沉淀自 T0502（20 轮第 1 轮；本地 main 落后，v1.39.3 mount 重构
未合入，按现树核实）。对照 bcachefs `src/commands/mount.rs`。

## 核心概念

1. **只读重试循环**：mount(2) 失败且写保护错、未带只读时自动
   加只读重试；已只读直接跳出（`mount_inner:41-59`）。
2. **EBUSY 特判**：仅忙定制提示，其余透传；外层补模块未加载
   提示（`mount_inner:63-73`）。
3. **三路选项分流**：宏一次拆分内核标志、fuse 选项、剩余交文件
   系统选项；双写项与独占项分别处理
   （`parse_mountflag_options:99-143`）。
4. **fstab 选项吞掉**：自动挂载类与注释类直接丢弃，不进内核
   （`parse_mountflag_options:134-136`）。
5. **无 degraded 问答证伪**：现树 mount.rs 零命中 degraded；缺盘
   不询问，直接拼残缺列表交内核，降级由内核裁决
   （`cmd_mount_inner:203-232`）。

## 复用指南

- 写保护失败必须自动只读重试，禁止直接报错。
- 用户态 fstab 兼容选项必须显式吞掉，禁止透传内核。
- 缺盘策略归属必须明确（用户态问 vs 内核裁决），禁止两边
  都假设对方处理。
