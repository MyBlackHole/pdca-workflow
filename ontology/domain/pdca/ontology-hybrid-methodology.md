---
schema: pdca.asset/v1
id: ontology:domain/ontology-hybrid-methodology
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/ontology-hybrid-methodology/1.0.0
summary: 混合方法论本体根：调研顶向下（top-down 100%）与开发底向上（bottom-up Work Package）双向，叶粒度middle-out
  Yo-Yo（对齐 Ontology101/METHONTOLOGY/NeOn/WBS/DDD）
relations:
  specializes:
  - ontology:concept/pdca
  composed_of:
  - ontology:entity/report-center-system
  relates_to:
  - ontology:domain/ontology-hybrid-research-topdown
  - ontology:domain/ontology-hybrid-develop-bottomup
  - ontology:domain/ontology-hybrid-leaf-middleout
  - ontology:pattern/ontology-modular-reference
  - ontology:pattern/testable-signal-to-test-derivation
attributes:
- name: hybrid_bidirectional
  desc: 调研根→叶全面记录，开发叶→根实现，同树反向闭环
  constraint: 项目实体为根 composed_of 树全面落盘；叶 dependencies:[] 根聚叶
  testable_signal: 运行 python3 scripts/ontology_graph.py --format summary 检查本根 composed_of
    可追且 islands:0，且 grep -R 'hybrid' ontology/domain/ontology-hybrid-*.md 可命中
- name: research_completeness
  desc: 调研全面性（100% Rule）
  constraint: 父实体 work = 子实体works之和，缺一叶即缺一维度，调研产出必须 100% 落盘
  testable_signal: 运行 python3 scripts/ontology_graph.py --format summary 检查 report-center-system
    树叶数≥2 且 grep -R 'composed_of' ontology/entity/report-center-system.md 可命中，且经 validate
    通过
- name: develop_assignability
  desc: 开发可分配性（Work Package）
  constraint: 叶任务可分配至1人且可独立验证（1 leaf = 1 testable_signal → 1 scaffold → 1 pytest）
  testable_signal: 运行 python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-hybrid-methodology
    --out /tmp/hybrid_demo.py 可产且 pytest --collect-only 可命中，且经 validate 通过
- name: leaf_governance
  desc: 叶治理（middle-out Yo-Yo）
  constraint: 过粗按正交度split，过细按 relates_to 合并，满足三准绳任一即叶
  testable_signal: 检查本文件含 '过粗' 与 '过细' 且 grep -R '三准绳' ontology/domain/ontology-hybrid-leaf-middleout.md
    可命中，且经 validate 通过 且运行 grep -q 'fix' ontology/domain/ontology-hybrid-methodology.md
    && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q
    'OK'
---

# 混合方法论本体根（Hybrid Research→Dev）

> 综合 `Ontology101 top-down/bottom-up/combination` + `METHONTOLOGY evolving prototype` + `NeOn 9场景` + `WBS 100%/Yo-Yo` + `DDD bounded context`，解决“调研一层层往下拆到叶子，开发一层层往根实现”的本体叶粒度与双向一致性。

## 双向同树（同树反向）

- **调研（根→叶，生产本体）**：项目实体为根，`composed_of` 逐层拆至叶，调研产出即 `ontology/<type>/<slug>.md` 全面落盘。**全面性**：`100% Rule` 父=子之和，缺一叶即缺一维度，`middle-out` 中层显著概念优先（先取 `report-center-web` 再特化），`grep -R 'composed_of' ontology/entity/report-center-system.md` 可命中。`flow-plan##拆分映射` 即此检查点。
- **开发（叶→根，消费本体）**：叶→根实现，`python3 scripts/ontology_tree_split.py --ontology-dir ontology --prd <prd>` 叶→根生 `candidates`（`slug_base/ontology_node_type/dependencies`），`python3 scripts/compute-frontier.py` 算 `ready-set [[叶],[根]]`，叶并行根串行，Work Package可分配至1人。`flow-do#3.5` 默认启用。

### 决策树

```
调研：根是否存在？─否─→ 拆子节点 → 每叶 ≥1 testable_signal → 落盘为本体
开发：本体是否存在？─是─→ 读 composed_of 树 → 生叶任务 → 叶 dependencies:[] 根聚叶
粒度：三准绳任一满足？─是─→ 定叶；否→ 继续拆/合
```

## 叶粒度（middle-out Yo-Yo）与反模式

**三准绳**（`ontology-modular-reference:21`）：可独立验证 / 可独立演进（维度正交） / 可独立复用（≥2复用或≥3 attrs或方法论类），满足任一即叶。

- **过粗反模式**：1叶含多 `constraint` 无法单 `testable_signal` 派生（如 `report-center-system` 单叶含 web+collection 双约束）→ 按正交度 `split` 为 `web` + `collection`
- **过细反模式**：叶无 `constraint` 可测或仅1行描述 → 按 `relates_to` 合并

**Yo-Yo校正**：调研top-down定框架→开发bottom-up补细节→失衡时跳变，`ontology_graph --format dot` 可导出叶边。

## 应用（`report-center-system` 正例）

`report-center-system(composed_of: web, collection)` 2叶正交满足三准绳：`web` 可独立验证（HTTP鉴权）、`collection` 可独立验证（调度入库），各 `testable_signal` 可 `scaffold`，`tree_split` 可调度，叶即任务1:1 硬映射 `T0477:archive`。反例：单叶 `report-center` 含双约束为过粗，需 `split`。

## PDCA对接与门禁

- **Plan**：`meta.ontology_fragment=ontology` 声明根，`ontology-ready` 硬拦缺 `fragment`
- **Do**：`tree_split` 默认 + `clash-check` 阻断 + `task_identity` 继承 `fragment/node_type`
- **Check**：`validate-convergence` 回链 `meta.convergence → AC → evidence`
- **Act**：`disposition` 含 `ontology:` 硬拦 `archive`

## 命令

```bash
python3 scripts/ontology_graph.py --root ontology --format summary # islands:0
python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-hybrid-methodology --out /tmp/x.py
python3 scripts/ontology_tree_split.py --ontology-dir ontology --prd <prd_with_拆分映射>
```

## 来源

- Stanford Ontology101 (Noy & McGuinness 2001) top-down/bottom-up/combination
- METHONTOLOGY (Gómez-Pérez et al. 1997) evolving prototype
- NeOn Methodology (Suárez-Figueroa et al. 2012) 9场景
- PMI WBS Practice Standard (Yo-Yo, 100% Rule)
- DDD bounded context (Evans)
