---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-journal-rewind
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/bcachefs-journal-rewind/1.0.0
summary: bcachefs Journal Rewind 实体 — rewind_limit 下界、JSET_NO_FLUSH 候选枚举与 overwrite 旧值回退
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: rewind_limit_floor_and_candidates
    desc: rewind_limit 下界（BCH_JSET_ENTRY_rewind_limit 14）与 [floor,latest] 内 JSET_NO_FLUSH==false 的 flush 条目候选枚举可测
    constraint: 覆盖 journal_rewind_info.rs:79 jset_rewind_limit 扫 payload entry_payload_le64 + floor_seq 为 min seq on disk 或 rewind_limit 值 + latest_p 为最大 seq + 枚举 [floor,latest] 内 JSET_NO_FLUSH==false 的 flush 条目为候选 + -n 截断取最近 N，经时序与决策树可一图建模
    testable_signal: "运行 grep -q 'jset_rewind_limit' /home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs && grep -q 'BCH_JSET_ENTRY_rewind_limit' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h && grep -q 'JSET_NO_FLUSH' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h 且 grep -q 'journal-rewind' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: overwrite_and_rewind_range
    desc: overwrite 旧值（type 10）与 rewind 区间（type 15 rewind range from/to）的回退语义可测
    constraint: 覆盖 BCH_JSET_ENTRY_overwrite 存被覆写旧 key + BCH_JSET_ENTRY_rewind 存 from/to range + rewind 时该区间内 key 均带 overwrite 供反向恢复，经 C4 L3 与状态机可一图建模
    testable_signal: "运行 grep -q 'overwrite' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h && grep -q 'BCH_JSET_ENTRY_rewind' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h && grep -q 'rewind' /home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs 且 grep -q 'journal-rewind' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: open_scan_and_journal_replay_rewind
    desc: open_scan 扫描与 journal replay 在 rewind 后的重放可测
    constraint: 覆盖 device_scan::open_scan → JournalEntries::collect(c_fs) → bch2_journal_entry_missing_range 处理空洞 → journal_replay_print 分事务边界 [log(level0) → 非事务] 高亮 经 rewind 后重新 replay 至 rewind seq，经时序与正例可一图建模
    testable_signal: "运行 grep -q 'open_scan' /home/black/Documents/bcachefs-tools/src/device_scan.rs && grep -q 'JournalEntries' /home/black/Documents/bcachefs-tools/src/commands/list_journal.rs && grep -q 'bch2_journal_read' /home/black/Documents/bcachefs-tools/fs/journal/read.c 且 grep -q 'journal-rewind' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
---

# Bcachefs Journal Rewind（日志回退）

`journal_rewind` 为 `bcachefs` 的时间回退：`journal_rewind_info`（`src/commands/journal_rewind_info.rs:119`）以 `open_scan` 扫 `super`，经 `jset_rewind_limit`（`79` 扫 `BCH_JSET_ENTRY_rewind_limit` payload `entry_payload_le64:44`）定 `floor_seq`（下界），`latest_p`（`153`）定 `latest_seq`（上界），枚举 `[floor,latest]` 内 `JSET_NO_FLUSH==false` 的 `flush` 条目为候选，回退区间 `rewind (15)` 内 `overwrite (10)` 存旧值供恢复。定位：`journal_rewind_info.rs:119 → device_scan::open_scan → journal/read.h:78 + journal/reclaim.c + bcachefs_format.h:1624 (14/15/10)`。

## C4 L3 Component — rewind_limit 下界 + flush 候选 + overwrite 旧值

`journal_rewind_info.rs:79` 的 `jset_rewind_limit` 扫描 `jset_entry type==rewind_limit (14)` 的 `payload le64` 得 `floor_seq`；无 `rewind_limit` 时回退到 `min seq on disk` 并警告；`latest_p:153` 取最大 `seq`；`JSET_NO_FLUSH`（`bch_sb field flags`）为 `false` 的 `flush` 条目即提交边界；`overwrite`（`10`）存被覆写前 `bkey` 旧值；`rewind`（`15`）存 `from/to` 区间标记回退中。C4 L3 图以 `open_scan → rewind_limit(14) → [floor,latest] → flush候选(JSET_NO_FLUSH) → overwrite(10)/rewind(15)` 五层呈现。

```mermaid
graph TD
    SCAN["open_scan<br/>device_scan.rs<br/>scan super"]
    SCAN --> LIMIT["jset_rewind_limit:79<br/>BCH_JSET_ENTRY_rewind_limit(14)<br/>entry_payload_le64:44"]
    LIMIT --> FLOOR["floor_seq<br/>rewind_limit 值或 min seq 警告"]
    SCAN --> LATEST["latest_p:153<br/>max seq"]
    FLOOR & LATEST --> ENUM["枚举 [floor,latest]<br/>JSET_NO_FLUSH==false<br/>flush 条目候选"]
    ENUM --> OW["overwrite(10)<br/>旧值"]
    ENUM --> RW["rewind(15)<br/>from/to 区间"]
    OW & RW --> REPLAY["journal_replay<br/>重放至 rewind seq"]
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:79 + src/commands/journal_rewind_info.rs:153 + fs/bcachefs_format.h:1624
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:79`（`jset_rewind_limit`）+ `/home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:153`（`latest_p`）+ `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1624`（`14 rewind_limit /15 rewind /10 overwrite`）+ `/home/black/Documents/bcachefs-tools/fs/journal/read.h:78`（`bch2_journal_read`）

## 时序 — journal_rewind_info 选点与 rewind 重放

1) `journal_rewind_info /dev/sda` → `open_scan` 读 `super` 与 `journal buckets`；2) `JournalEntries::collect`（`list_journal.rs:772`）收集并 `bch2_journal_entry_missing_range` 补空洞；3) `jset_rewind_limit` 定 `floor_seq`，`latest_p` 定 `latest_seq`；4) 枚举 `[floor,latest]` 内 `JSET_NO_FLUSH==false` 的 `flush` 条目为候选，`-n` 截断取最近 N；5) 选定 `rewind_seq` 后 `bch2_journal_read` 重放至该 seq，`overwrite` 供反向恢复旧 `bkey`。时序图以 `open_scan → floor/latest → 枚举 flush → 选 rewind → replay` 全链呈现。

```mermaid
sequenceDiagram
    participant U as journal_rewind_info
    participant S as open_scan
    participant J as JournalEntries
    participant L as jset_rewind_limit
    U->>S: open_scan()
    S->>J: collect(c_fs) + missing_range
    J->>L: 扫 rewind_limit(14) → floor_seq
    J->>J: latest_p → latest_seq
    J->>J: 枚举 [floor,latest] JSET_NO_FLUSH==false
    J-->>U: 候选 flush 表 (-n 截断)
    U->>J: 选 seq 重放至 rewind
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:119 + src/commands/list_journal.rs:772 + fs/bcachefs_format.h:1624
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:119` + `/home/black/Documents/bcachefs-tools/src/commands/list_journal.rs:772` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1624`

## 状态机 — rewind 区间与 overwrite

`rewind` 三态 `normal → rewinding → rewound`：`rewinding` 时 `[from,to]` 区间内所有 key 均带 `overwrite (10)`，`rewound` 后 `rewound_from/to` 记录。`jset` 二态 `NO_FLUSH true/false`：仅 `false` 的 `flush` 条目可为回退点。`floor` 二态 `rewind_limit → min seq`：有 `14` 即 `rewind_limit`，无则警告回落 `min seq`。状态机图覆盖 `normal→rewinding→rewound` 与 `floor` 分支。

```mermaid
stateDiagram-v2
    [*] --> Normal: 正常 journal
    Normal --> Rewinding: journal_rewind from/to
    Rewinding --> Rewound: 重放至 from 完成
    Rewound --> Normal: 正常提交覆盖 rewind(15)
    Normal --> FloorLimit: 有 rewind_limit(14)
    FloorLimit --> FloorMin: 无 rewind_limit 警告
    FloorLimit --> Candidates: 枚举 flush 候选
    FloorMin --> Candidates: 枚举 flush 候选
    Candidates --> Rewinding: 选 rewind seq
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:79 + fs/bcachefs_format.h:1624
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:79` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1624`

## 决策树

```mermaid
flowchart TD
    START(["journal_rewind_info 入口"]) --> Q1{"读 super 成功?"}
    Q1 -- 否 --> E1["EIO"]
    Q1 -- 是 --> Q2{"有 rewind_limit(14)?"}
    Q2 -- 是 --> FL["floor=rewind_limit"]
    Q2 -- 否 --> FM["floor=min seq<br/>警告"]
    FL & FM --> LAT["latest=max seq"]
    LAT --> ENUM["枚举 [floor,latest]<br/>JSET_NO_FLUSH==false 的 flush"]
    ENUM --> Q3{"-n 截断?"}
    Q3 -- 是 --> TR["取最近 N"]
    Q3 -- 否 --> ALL["全部候选"]
    TR & ALL --> Q4{"选 rewind?"}
    Q4 -- 是 --> RW["rewind(15) + overwrite(10) 重放"]
    Q4 -- 否 --> PRT["仅打印候选表"]
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:119 + fs/bcachefs_format.h:1624
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:119` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1624`

## 正例

```c
// 正例：枚举候选并回退
bcachefs journal_rewind_info /dev/sda -n 10
// → [floor=100,latest=500] 内 flush 候选 20 条，取最近 10 打印
bcachefs journal_rewind --seq 450 /dev/sda
// → rewind(15) from=450 to=500，overwrite(10) 恢复旧 bkey，replay 至 450
// 验证：floor 来自 rewind_limit(14)，非警告回落 min seq
```

命中：`rewind_limit` 与 `floor` 配对，`overwrite` 与 `rewind` 配对。

## 反例

```c
// 反例1：回退到低于 rewind_limit 的 seq
// 错：discard 已无效化早于 rewind_limit 的数据，回退后踩踏
// 正确：仅在 [floor,latest] 内选 JSET_NO_FLUSH==false 的 flush 点

// 反例2：忽视 overwrite 旧值
// 错：仅用 rewind(15) 不带 overwrite(10)，旧 bkey 丢失无法恢复
// 正确：rewinding 区间内每 key 均带 overwrite 旧值
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-journal-rewind.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-journal-rewind.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-journal-rewind.md` ≥80 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-journal-rewind --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-journal-rewind` GATE OK

Source: `/home/black/Documents/bcachefs-tools/src/commands/journal_rewind_info.rs:79` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1624` + `/home/black/Documents/bcachefs-tools/fs/journal/read.h:78`
