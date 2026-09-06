---
schema: pdca.asset/v1
id: ontology:domain/core-userspace-device-scan
type: domain
layer: Knowledge
status: active
summary: 设备快扫补扫 + 无udev兜底 + 死SB过滤 + 显式信任
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 按 UUID/LABEL 找盘、udev 缺失兜底、陈旧副本过滤场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 src/device_scan.rs 在仓库中存在且含 get_devices_by_uuid 定义"
- name: constraints
  desc: 扫描前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认期望数回落、兜底条件、显式信任三条前提在引用代码中有对应实现"
---

# 设备扫描快扫补扫体系

沉淀自 T0502（20 轮第 1 轮）。对照 bcachefs
`src/device_scan.rs`。

## 核心概念

1. **快扫加期望数补扫**：先 udev 快扫取首超块期望数，够数返回，
   否则回落全块扫（`get_devices_by_uuid:273-292`）。
2. **无 udev 兜底**：仅 udev 报错或空时回落 procfs 枚举；注释修
   历史 issue；残余 TODO 为事件等待（`get_all_block_devnodes`）。
3. **死 SB 过滤归一**：装袋调内核过滤陈旧死亡副本，非零转错；
   再重归一路径；等盘每次判齐前重滤
   （`filter_current_sbs:240-266`）。
4. **显式列表信任用户**：含冒号直接逐个读超块，不扩散不补扫；
   单盘多盘分流；兼容 systemd 抢消费的旧 UUID 键
   （`scan_sbs:381-417`）。
5. **LABEL 二次归一**：先按截断标签初筛，再去重 UUID；零一多
   各走各路，多 UUID 直接错（`get_devices_by_label:302-336`）。

## 复用指南

- 快扫必须配期望数回落，禁止快扫不到即失败。
- 陈旧副本必须过滤归一，禁止首个命中即信。
- 显式列表必须信任用户，禁止自作聪明扩散。
