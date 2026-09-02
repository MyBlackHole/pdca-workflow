---
schema: pdca.asset/v1
id: ontology:entity/TEMPLATE-ENTITY
type: entity
layer: Knowledge
status: active
summary: 【填】一句话摘要（含核心职责与可测边界）
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/scientific-research-methodology
  # 如为系统子叶，另加： composed_of 反向由 system 指向本实体
attributes:
  - name: 【填】属性1（如 c4_l3_coverage / state_lifecycle / throttle）
    desc: 【填】可测职责描述
    constraint: 【填】约束/阈值/分支（如覆盖 X/Y/Z 且 C4 L3 可一图建模）
    testable_signal: "运行 grep -q '关键字' records/<record>/research-*.md 且 grep -q '关键字' /tmp/zfs/module/zfs/<file>.c 命中"
  - name: 【填】属性2
    desc: 【填】
    constraint: 【填】
    testable_signal: "运行 grep -q '关键字' records/<record>/research-*.md 且 grep -q '关键字' /tmp/zfs/module/zfs/<file>.c 命中"
  - name: 【填】属性3
    desc: 【填】
    constraint: 【填】且时序/状态机可一图建模
    testable_signal: "运行 grep -q '关键字' records/<record>/research-*.md 且 grep -q '关键字' /tmp/zfs/include/sys/<file>.h 命中"
---

# 【填】实体名（中文+英文）

一句话定位：【填】该实体在全栈中的位置与上下游衔接（ZPL→DMU→DSL→SPA→ZIO→VDEV 横切 ARC 等）。

## C4 L3 Component — 【填】容器与关系

描述：`【填】结构体` 核心字段 `【填】` 与 `【填】` 的层级与持久化（`【填】` 序列化），`C4 L3` 图以 `【填】 → 【填】 → 【填】` 三层呈现。

```mermaid
graph TD
    A[ContainerA] --> B[ComponentB]
    B --> C[SubComponentC]
    %% Source: openzfs/zfs/include/sys/<file>.h:20-60
```

Source: `openzfs/zfs/include/sys/<file>.h:20-60`（含 `【填】` 定义）+ `openzfs/zfs/module/zfs/<file>.c:20-60`

## 时序 — 【填】完整链

1) `【填】` → 2) `【填】` → 3) `【填】` → 4) `【填】` → 5) `【填】`，时序图覆盖 `【填】 → 【填】 → 【填】` 全链。

```mermaid
sequenceDiagram
    participant U as ZPL/DMU
    participant E as 本实体
    participant V as 下游VDEV/ZIO
    U->>E: request()
    E->>V: dispatch()
    V-->>E: done
    %% Source: openzfs/zfs/module/zfs/<file>.c:100-200
```

Source: `openzfs/zfs/module/zfs/<file>.c:100-200`（`【填】` 时序）

## 状态机 — 【填】生命周期

五态：`S1 → S2 → S3 → S4 → S5`，关键变迁 `【填】` 需 `【填】` 触发，状态机图覆盖全部变迁与 `【填】` 分支。

```mermaid
stateDiagram-v2
    [*] --> S1
    S1 --> S2: trigger
    S2 --> S3
    S3 --> S4
    S4 --> [*]
    %% Source: openzfs/zfs/include/sys/<file>.h:40-80
```

Source: `openzfs/zfs/include/sys/<file>.h:40-80`（`【填】` 枚举）+ `openzfs/zfs/module/zfs/<file>.c:300-400`

## 决策树

```mermaid
flowchart TD
    START([入口]) --> Q1{分支1?}
    Q1 -- 是 --> A1[处理A]
    Q1 -- 否 --> Q2{分支2?}
    Q2 -- 是 --> A2[处理B]
    Q2 -- 否 --> A3[处理C]
    A1 --> END([完成])
    A2 --> END
    A3 --> END
    %% Source: openzfs/zfs/module/zfs/<file>.c:400-500
```

Source: `openzfs/zfs/module/zfs/<file>.c:400-500`（`【填】` 分支）

## 正例

```c
// 正例：正确的配对与时序
// 【填】先 hold 再 assign，transform 压弹配对，taskq 分发
【填】示例代码，体现三属性配对正确
// 验证：【填】与【填】配对，【填】一致
```

命中：【填】配对正确，【填】边界一致。

## 反例

```c
// 反例1：【填】缺配对导致【填】
// 错：漏 【填】，结果 【填】
// 正确：【填】

// 反例2：锁序反转
// 错：先 A 锁再 B 锁，与正例 ABBA 死锁
// 正确：先 B 再 A
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' records/<record>/research-*.md` ≥3
- **溯源门禁**：`grep -c 'Source:' records/<record>/research-*.md` ≥3 且每图附 `openzfs/zfs file:line`
- **正文门禁**：`wc -l ontology/entity/<entity>.md` ≥60 且 `grep -q '决策树' && grep -q '正例' && grep -q '反例' && grep -q '门禁'`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 动词+判定且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/<entity> --out /tmp/x.py` 可产且 `pytest --collect-only` 可收集
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/<entity>` GATE OK

Source: `openzfs/zfs/module/zfs/<file>.c` + `openzfs/zfs/include/sys/<file>.h`
