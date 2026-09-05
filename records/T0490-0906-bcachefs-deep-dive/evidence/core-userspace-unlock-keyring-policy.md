---
schema: pdca.asset/v1
id: ontology:domain/core-userspace-unlock-keyring-policy
type: domain
layer: Knowledge
status: active
summary: 用户态解锁四档策略 + keyring 优先 + systemd 桥接
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 加密盘解锁交互、自动化与手动并存、开机无 TTY 场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 src/key.rs 在仓库中存在且含 UnlockPolicy 定义"
- name: constraints
  desc: 解锁策略的前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认显式策略独占、keyring 命名隔离、终端硬化三条前提在引用代码中有对应实现"
---

# 用户态解锁四档策略 + keyring 优先

沉淀自 T0490（纵深分析，按现树旧形态核实；v1.39.3 mount 重构
尚未合入本地 main）。对照 bcachefs `src/key.rs`、
`src/commands/mount.rs:handle_unlock`、`src/commands/key.rs`。

## 核心概念

1. **三路输入路由**：is_terminal → 交互提问；/dev/null →
   systemd-ask-password；非终端管道 → stdin 直读。开机无 TTY
   不卡死，脚本不误弹交互（`StdinType::detect`）。
2. **解锁四档策略 + keyring 优先**：显式策略独占不回退；默认
   先 SESSION→USER→USER_SESSION 搜 `bcachefs:<uuid>`，命中
   直接挂载，解决重复输口令与自动化冲突
   （`UnlockPolicy::apply`、`KeyHandle::new_from_search`）。
3. **systemd 桥接**：首轮用缓存，后两轮重试，NUL 切分多口令
   逐个 check，打通 Plymouth/开机会话
   （`ask_from_systemd_and_check`）。
4. **终端输入硬化**：关 ECHO 强制 ICRNL+ICANON（修 initramfs
   回车变 `\r` 致口令恒错）；Zeroizing 防内存残留；双次输入
   防误设；`unlock --check` 三态退出码供 initramfs 决策
   （`cmd_unlock`）。

## 复用指南

- 交互/自动化/开机三场景必须显式路由，禁止"猜"输入源。
- 密钥缓存按"服务:标识"命名隔离，命中即免问；显式策略
  必须独占，静默回退是安全隐患。
- 口令内存必须清零类型 + 双次确认；只读检查命令用退出码
  而非输出文本做决策。
