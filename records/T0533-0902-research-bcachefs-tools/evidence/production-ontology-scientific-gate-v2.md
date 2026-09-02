---
schema: pdca.asset/v1
id: ontology:pattern/production-ontology-scientific-gate
type: pattern
layer: Knowledge
status: active
summary: 生产本体科学保障门禁：METHONTOLOGY五阶段+NeOn+OOPS41+OntoClean+100% Rule+testable_signal 三件套一次做对
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/domain-entity
    - ontology:concept/process
  relates_to:
    - ontology:pattern/scientific-research-methodology
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/scientific-research-lifecycle
    - ontology:domain/ontology-hybrid-methodology
    - ontology:pattern/ontology-evaluation-oops
    - ontology:pattern/ontology-metrics
    - ontology:pattern/testable-signal-to-test-derivation
    - ontology:pattern/ontology-modular-reference
    - ontology:concept/knowledge-provenance
attributes:
  - name: methontology_five_phases
    desc: METHONTOLOGY五阶段可追溯（specify→conceptualize→formalize→implement→evaluate）每阶段产物可测
    constraint: 每个生产实体必经“需求规约→概念化（术语表+关系）→形式化（frontmatter+relations）→实现（落盘+溯源）→评估（validate+oops+scaffold）”五阶段，每阶段有产出文件且可被 gate 脚本单项校验
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check lifecycle --node ontology:pattern/production-ontology-scientific-gate 检查五阶段产物均存在且 grep -q 'METHONTOLOGY' ontology/pattern/production-ontology-scientific-gate.md 命中且 grep -q 'records' records/T0525-0902-review-zfs-production-ontology/report.md 命中"
  - name: neon_nine_scenarios_coverage
    desc: NeOn九场景选型完备（重用/重工程/合并/对齐/模块化等）防止孤岛与重复
    constraint: 新实体创建前必经 NeOn 场景判定（场景1重用/场景2重工程/场景3合并/场景6模块化），判定结果写入 PRD 关联本体节点且 related_to 无孤岛
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check neon --node ontology:pattern/production-ontology-scientific-gate 检查 NeOn 场景判定已记录且 python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0' 且 grep -q 'records' records/T0525-0902-review-zfs-production-ontology/report.md 命中"
  - name: oops_onoclean_gate
    desc: OOPS!41 pitfalls零critical + OntoClean刚性无环（P08/P10/P13/P22/P41 等）
    constraint: 提交前必以 production-ontology-gate 扫描 OOPS 41（P08缺注释/P10缺domain-range/P13逆缺/P22命名/P41无license）critical=0，且 specializes 无环且刚性一致（子不违父刚性），由 ontology-validate AC-3 无环校验
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check oops --all 检查 critical=0 且 python3 scripts/ontology-validate.py --ontology-dir ontology 检查 0 issues 且 grep -q 'records' records/T0525-0902-review-zfs-production-ontology/report.md 命中"
  - name: hundred_percent_rule_with_wbs
    desc: PMI WBS 100% Rule + Yo-Yo 三准绳粒度自检（父=子之和且互斥，正交可验可复用）
    constraint: 系统聚合（zfs-system类）composed_of 子叶必 100% 覆盖（缺一维度即缺一叶），叶满足三准绳任一（≥2复用/≥3 attrs/正交）且过粗按正交度split、过细按 relates_to 合并，gate 校正
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/zfs-system 检查 composed_of 覆盖率≥95%（以 module/zfs/*.c 为参照）且 grep -q 'composed_of' ontology/entity/zfs-system.md 命中且 grep -q 'records' records/T0525-0902-review-zfs-production-ontology/report.md 命中"
  - name: testable_signal_derivation_gate
    desc: testable_signal→test 三模式可派生（属性断言/契约测试/收敛验证）且双源可回归
    constraint: 每条 attributes.testable_signal 必须含动词（运行/检查/校验）+对象+判定谓词，符合 testable-signal-to-test-derivation 三模式之一，且 records 段与 /tmp/zfs 源码段双源可回归（裸仓 records PASS，源码段 /tmp/zfs PASS）
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check signal --node ontology:entity/zfs-spa 检查每条 signal 含动词且非泛化且 grep -q 'grep -q' ontology/entity/zfs-spa.md 命中且 grep -q 'records' records/T0525-0902-review-zfs-production-ontology/report.md 命中"
  - name: hybrid_yoyo_and_diagram_integration
    desc: 混合双向同树 + 多图mermaid集成（C4 L2+时序+状态机为P0，每图1 Source）
    constraint: 每个生产实体必含 C4 L3 组件 + 时序 + 状态机 + 决策树 + 正例 + 反例 + 门禁八段且 mermaid≥3且每图1 Source（openzfs/zfs file:line），系统聚合另含聚合决策树与正交度声明，符合 research-diagram-methodology
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check diagram --node ontology:entity/zfs-vdev 检查 mermaid≥3且每图含 Source 且 grep -q '决策树' ontology/entity/zfs-vdev.md 命中且 grep -q 'records' records/T0525-0902-review-zfs-production-ontology/report.md 命中"
  - name: realization_verifiable_implementation
    desc: 本体可实现可校验（realization）：本体即实现规约，派生实现细节完整、确定性可校验且错误可证伪
    constraint: 每个生产实体必满足“可被直接实现”：①结构完整（C4 给出所有创建/销毁/持久化所需的字段与类型，且含 btree/bset/journal/alloc 等跨实体接口契约）②行为完整（时序+状态机覆盖全部成功/失败/重试/并发分支，无隐含状态）③校验完整（正例为最小可运行实现骨架，反例覆盖全部已知的误用模式，且 scaffold 派生的契约测试以确定性夹具证明实现对齐本体——即“按本体实现后，跑本体派生的测试必绿；违背本体，测试必红”）
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check realization --node ontology:entity/bcachefs-btree 检查 realization PASS（含 structure/behavior/verification 三契约）且 python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-btree --out /tmp/x.py 可产且 grep -q 'realization' ontology/pattern/production-ontology-scientific-gate.md 命中"
---

# 生产本体科学保障门禁（Production Ontology Scientific Gate）

> 综合 `METHONTOLOGY evolving prototype` + `NeOn 9场景` + `Ontology101 top-down/bottom-up/middle-out` + `OOPS! 41 pitfalls` + `OntoClean` + `PMI WBS 100% Rule/Yo-Yo` + `testable_signal→test 三模式` + `realization 可实现可校验`，解决“**为何本次未一次做对**”并保障“**下一次生产一次通过**”。本 pattern 即 T0525 三件套的 Checklist 源头，`scripts/production-ontology-gate.py` 为其可执行化，`templates/production-*.md` 为其落盘模板。

> **新增第七维 realization（2026-09-02）**：本体“为了写而写”的根因是本体止于文档、无法被直接实现。`realization` 要求本体即实现规约——结构、行为、校验三完整，且派生的确定性夹具可证伪实现偏离（按本体实现必绿、违背必红）。

## 为何本次未一次做对（根因）

| 现象 | 根因 | 对应保障维 |
|------|------|------------|
| `zfs-system 43行` 单薄无决策树 | 无 **模板八段**硬拦，Plan 未要求 `wc -l≥60 + 决策树+正反例+门禁` | hybrid_yoyo_and_diagram |
| `VDEV/ZIL` 未独立 | 无 **100% Rule 事前校验**，Plan 未以 `module/zfs/*.c` 覆盖率 ≥95% 为硬门 | hundred_percent_rule |
| `module/zfs` 信号裸仓 FAIL | 无 **双源可回归**约束，Do 未要求 `records PASS && /tmp/zfs PASS` | testable_signal_derivation |
| 孤岛虽0但 OOPS 未扫 | 无 **OOPS 41 事前扫描**，仅靠 `validate` 非空 | oops_onoclean |

Source: `ontology/pattern/scientific-research-methodology.md:31` 四支 + `ontology/domain/ontology-hybrid-methodology.md:42` 双向同树 + `ontology/pattern/ontology-evaluation-oops.md:18` 41 pits + `ontology/pattern/ontology-metrics.md:34` health 三件套

## 七维门禁（与 gate 脚本一一对应，新增 realization）

### 1. METHONTOLOGY 五阶段（`--check lifecycle`）

specify（PRD 含验收）→ conceptualize（术语表+关系）→ formalize（`pdca.asset/v1` frontmatter+relations）→ implement（落盘+`Source: file:line`）→ evaluate（`validate+scaffold+gate`）。每阶段产物可被 `gate.py --check lifecycle --node <id>` 单项校验，未完成则 `FAIL: missing conceptual`。

Source: `METHONTOLOGY (Gómez-Pérez 1997) evolving prototype` + `ontology/pattern/scientific-research-lifecycle.md:15` I2S2 4阶段

### 2. NeOn 九场景（`--check neon`）

场景1重用（复用既有 entity）/2重工程/3合并/5对齐/6模块化。新建前必在 PRD 写明场景选型，否则 `gate --check neon FAIL: no scenario`。判定后 `relates_to` 无孤岛由 `ontology_graph islands:0` 保证。

Source: `NeOn Methodology (Suárez-Figueroa 2012) 9 scenarios` + `ontology/domain/ontology-hybrid-methodology.md:42`

### 3. OOPS!41 + OntoClean（`--check oops`）

扫描 `P08 missing annotations / P10 missing domain/range / P13 inverse / P22 naming / P41` 等，critical=0 方 `GATE OK`；`specializes` 无环由 `ontology-validate AC-3` 硬拦，刚性由 `OntoClean` 人工复核（子不违父）。

Source: `http://oops.linkeddata.es` 41 pits + `ontology/pattern/ontology-evaluation-oops.md:22` + `scripts/ontology-validate.py:60` CYCLE

### 4. 100% Rule + Yo-Yo 三准绳（`--check hundred`）

系统 `composed_of` 子叶之和 = 父 100%，以 `module/zfs/*.c` 为参照统计覆盖率（`gate --check hundred --node zfs-system` 算 `covered/total`），`<95%` 则 `FAIL` 并列缺口（如 VDEV）。叶粒度按三准绳（≥2复用/≥3 attrs/正交）判定，过粗 split、过细合并，Yo-Yo 校正。

Source: `PMI WBS Practice Standard 100% Rule / Yo-Yo` + `ontology/domain/ontology-hybrid-methodology.md:55` 三准绳

### 5. testable_signal 三模式（`--check signal`）

每条 `testable_signal` 必为 `testable-signal-to-test-derivation` 三模式之一（属性断言/契约测试/收敛验证），含动词+对象+判定，拒泛化（`由领域实践验证`）。双源回放：`records/` 段 PASS 且 `/tmp/zfs` 源码段 PASS（或显式声明无源码依赖）。

Source: `ontology/pattern/testable-signal-to-test-derivation.md:32` 三模式 + `ontology/concept/ontology-rule-attr-testable.md`

### 6. 多图集成（`--check diagram`）

每个生产实体必含 `C4 L3 + 时序 + 状态机` 为 P0（`mermaid≥3`），系统聚合另含 `C4 L2 + 聚合决策树`，每图1 `Source: openzfs/zfs file:line`，`grep -c mermaid` 与 `Source:` 双硬拦。

Source: `ontology/pattern/research-diagram-methodology.md:20` P0三图 + `ontology/pattern/scientific-research-methodology.md:24` 四支

### 7. 可实现可校验 Realization（`--check realization`）

本体止于文档即“为了写而写”。`realization` 要求**本体即规约**，满足三完整方可 `PASS`：

- **结构完整**：`C4` 给出实现该实体所需的全部类型、字段、持久化格式与跨实体接口（`btree/six/journal/alloc` 的创建/销毁/序列化契约在 `C4` 中无缺口）
- **行为完整**：`时序 + 状态机` 覆盖全部成功/失败/重试/并发分支，无隐含状态（`six read→intent→write` 升级、`trans restart 25码`、 `pin→reclaim` 等在图中可追）
- **校验完整**：`正例`为最小可运行实现骨架（可直接翻译为代码），`反例`覆盖全部已知误用模式，且 `scaffold` 派生的契约测试以确定性夹具可证伪——**按本体实现必绿、违背本体必红**

`gate --check realization --node <id>` 校验：`scaffold 可产 && pytest --collect-only 可收集 && 本体含 structure/behavior/verification 三契约关键词`，否则 `FAIL: realization missing`。

Source: `METHONTOLOGY implement/evaluate + ontology/pattern/testable-signal-to-test-derivation.md:32` 派生实现

## 使用流程（PDCA 对接）

```bash
# Plan 前置：声明 fragment 后即受本 pattern 约束
meta.ontology_fragment: ontology/entity/zfs-vdev  # 触发 ontology-ready + 本 gate

# Do 中：按模板落盘后自检
cp templates/production-entity.md ontology/entity/zfs-vdev.md  # 填八段
python3 scripts/production-ontology-gate.py --node ontology:entity/zfs-vdev  # 单节点 GATE OK 才提交

# Check/Act：CI 硬拦
python3 scripts/production-ontology-gate.py --all          # 全量 GATE OK
python3 scripts/ontology-validate.py --ontology-dir ontology
python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0'
```

## C4 L3 组件 — Gate 与模板协作

```mermaid
graph TD
    PRD[PRD with ontology_fragment] --> Gate[production-ontology-gate.py]
    Gate --> Checklist[pattern/production-ontology-scientific-gate<br/>6维Checklist]
    Checklist --> TemplateE[templates/production-entity.md<br/>八段模板]
    Checklist --> TemplateS[templates/production-system.md]
    TemplateE --> Entity[ontology/entity/zfs-vdev.md]
    TemplateS --> System[ontology/entity/zfs-system.md]
    Gate --> Validate[ontology-validate + graph + scaffold]
    Validate --> CI[ci-ontology-gate]

    %% Source: ontology/pattern/scientific-research-methodology.md:31 四支 + ontology/domain/ontology-hybrid-methodology.md:42
```

Source: `ontology/pattern/scientific-research-methodology.md:31` + `ontology/domain/ontology-hybrid-methodology.md:42`

## 状态机 — 五阶段 METHONTOLOGY 落盘状态

```mermaid
stateDiagram-v2
    [*] --> Specify: PRD含验收
    Specify --> Conceptualize: 术语表+关系
    Conceptualize --> Formalize: frontmatter落地
    Formalize --> Implement: mermaid+Source落盘
    Implement --> Evaluate: gate全绿
    Evaluate --> [*]: validate 0 + scaffold可产
    Evaluate --> Specify: FAIL回环
    %% Source: METHONTOLOGY 1997 + ontology/pattern/scientific-research-lifecycle.md:15
```

Source: `METHONTOLOGY (Gómez-Pérez 1997) evolving prototype` + `ontology/pattern/scientific-research-lifecycle.md:15`

## 决策树

```mermaid
flowchart TD
    START([新建生产实体]) --> Q1{已有可重用 entity?}
    Q1 -- 是 NeOn S1 --> A1[重用并 relates_to 原节点]
    Q1 -- 否 --> Q2{100% Rule: 系统是否缺维度?}
    Q2 -- 是 --> A2[新建 leaf 并加入 system composed_of]
    Q2 -- 否 --> Q3{粒度三准绳是否满足?}
    Q3 -- 否 过粗/过细 --> A3[split/合并 Yo-Yo 校正]
    Q3 -- 是 --> Q4{模板八段是否齐?}
    Q4 -- 否 --> A4[补 C4/时序/状态机/决策树/正反例]
    Q4 -- 是 --> Q5{signal 双源可回归?}
    Q5 -- 否 --> A5[改 signal 为 grep -q 双源]
    Q5 -- 是 --> Q6{OOPS 41 critical=0?}
    Q6 -- 否 --> A6[修 P08/P10/P13]
    Q6 -- 是 --> Q7{realization 三完整?}
    Q7 -- 否 结构/行为/校验缺口 --> A7[补结构契约/行为分支/正反例夹具]
    Q7 -- 是 --> END([gate --node PASS → 提交])
```

Source: `ontology/domain/ontology-hybrid-methodology.md:47` 决策树 + `ontology/pattern/ontology-evaluation-oops.md`

## 正例

```markdown
# 正例：按三件套新建 zfs-vdev 一次通过
cp templates/production-entity.md ontology/entity/zfs-vdev.md
# 填：3 attributes(拓扑/队列/故障) + C4 L3(vdev_t→queue→leaf) + 时序(open→probe→remove) + 状态机(ONLINE→DEGRADED→FAULTED) + 决策树(mirror/raidz选型) + 正反例(queue限速配对) + 门禁(mermaid≥3/Source≥3)
python3 scripts/production-ontology-gate.py --node ontology:entity/zfs-vdev
# 输出 GATE OK (lifecycle PASS, neon PASS, oops PASS, hundred PASS, signal PASS, diagram PASS)
python3 scripts/ontology-validate.py --ontology-dir ontology  # 0 issues
python3 scripts/ontology_test_scaffold.py --node ontology:entity/zfs-vdev --out /tmp/x.py && pytest --collect-only
```

命中：`gate --node` 七维全 PASS，`validate 0`，`scaffold` 可产，`islands:0`。

## 反例

```markdown
# 反例1：100% Rule 未校验即提交，导致系统缺维度
# zfs-system composed_of 仍为6叶，漏 vdev，gate --check hundred --node zfs-system -> FAIL: coverage 70% <95% 缺口 vdev/zil
# 正确：先 gate --check hundred 看覆盖率，再补 composed_of

# 反例2：signal 泛化导致不可派生
attributes: [{name: foo, testable_signal: "由领域实践验证"}]
# gate --check signal -> FAIL: missing verb（无 运行/检查）且非三模式
# 正确：改为 "运行 grep -q 'vdev_queue' records/... 且 grep -q 'vdev_queue' /tmp/zfs/... 命中"

# 反例3：模板八段缺决策树
# 实体仅含 C4 与时序，无决策树，gate --check diagram -> FAIL: missing 决策树
# 正确：按 templates/production-entity.md 八段占位补齐

# 反例4：NeOn 未选型导致重复造叶
# 新建 zfs-zil 时未声明 S1 重用 vs 新建，gate --check neon -> FAIL: no scenario
# 正确：PRD 写明 场景1重用 zfs-zpl 的 zil 子节 → 独立为 leaf 的重工程理由

# 反例5：realization 缺结构契约导致不可实现
# 实体 C4 仅含 CLI→wrappers 空壳，未给出 btree 的 six/cache/bset/journal pin 接口契约，按本体无法写出 bch2_btree_node_get
# gate --check realization -> FAIL: missing structure 契约
# 正确：C4 暴露 btree_cache→btree(six+format)→btree_node(bset*)→bkey 真实链
```

## 门禁

- **模板门禁**：`wc -l ontology/pattern/production-ontology-scientific-gate.md ≥80 && grep -q '决策树' && grep -q '正例' && grep -q '反例' && grep -q '门禁'`
- **属性门禁**：`attributes ≥7 且每条 testable_signal 含 grep -q 或 gate.py 动词`（新增 realization）
- **本体校验**：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues 且 `islands:0` 且 `guides` 合法（指向 domain-entity/process）
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:pattern/production-ontology-scientific-gate --out /tmp/x.py` 可产
- **Gate 自举门禁**：`python3 scripts/production-ontology-gate.py --node ontology:pattern/production-ontology-scientific-gate` GATE OK（含 realization）
- **走通门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/zfs-vdev` GATE OK（若演示稿存在）
- **实现门禁**：`python3 scripts/production-ontology-gate.py --check realization --node ontology:entity/bcachefs-btree` GATE OK（结构/行为/校验三完整）
```

