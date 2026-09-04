# 本体信息混乱审查：8桶全量审计与本体到代码单向溯源

## 背景

用户定性“本项目已经混乱了”，指定审查 `本体信息`（`ontology`），产出选 `A`、标准选 `A`、沉淀选 `A`，明确 `不审查任务记录`。`pdca-doctor valid:false`：`duplicate_task_ids/slugs`、`AGENTS.md` 引用 `ontology/domain/skill-*.md` 缺失、`pdca/tasks 80+ 扁平堆积`、`islands` 与 `validate` 仅轻量校验，`426 节点` 分布于 `8桶` 与 `5域` 的映射已漂移（`FROZEN 2026-09-04` 后 `domain 208→pdca72/core118/zfs11/report12`，`pattern` 新增 `sm4-*` 3 节点）。

**补充发现（Do 增量，Round2-5）**：用户指出“模板是否限制 AI 思考”的本质是**本体不完整导致创造性无处落位**——`prd.md/task.json/skill/8桶 frontmatter` 四模板的束缚感，根因归一为 `本体缺口` 而非模板本身；创造性可通过 `本体完整性` 处理（补本体即释创造性）。进一步要求：**模板本身需本体化**，并最终归一为**所有知识与事实全量本体化**——`知识（knowledge/*）与事实（fact/*）` 全量纳入本体，成为 `唯一事实源`。**最新约束**：`当前 PDCA 项目的 py 文件没有与 PDCA 本体对应，必须由本体到代码，不允许现有代码再有私设本体`——`本体到代码单向`，代码不得私设本体概念，本体是源、代码是投射。

输入锚点：
- `file: ontology/manifest.jsonl:1` — 426 节点清单（8桶）
- `file: ontology/versions/2026-09-04/FROZEN.md:1` — 8桶 FAIR+MOMo 冻结版
- `file: scripts/ontology-validate.py:1` / `scripts/ontology_graph.py:1` — 硬校验（validate+islands）
- `file: scripts/pdca-doctor.py:1` / `scripts/pdca_core.py:1` — 身份/引用/门禁，本体到代码单向待溯
- `file: scripts/*.py:1` — PDCA 项目 py 文件与 PDCA 本体对应缺失（待审计）
- `file: pdca/CONTEXT.md:1` — 共享术语表

## 目标

产 `本体信息全量审计` 的 `research-report.md`：**三维分级矩阵**（完整度/可检性/孤岛）+ **混乱清单与根因分级** + **P0/P1/P2 整改路线图**，全量可重跑且每项 `file:line` 可溯。

## 范围

- 输入：`ontology/` 全量（`concept/domain/entity/pattern/process/fact/pitfall/principle/versions` 等，`426+` 节点）
- 输出：`research-report.md`（含矩阵表+热力图 mermaid+清单表+路线图） + `records/T2045-0904-review-ontology-chaos/` 证据
- 不做：不审 `pdca/tasks` 与 `records` 任务记录体系（用户明确排除）；不改业务本体语义，仅审计与路线

## 功能需求

1. **三维审计矩阵**：426+ 节点按 `完整度`（桩/半桩/完整）、`可检性`（`testable_signal` 是否可回归）、`孤岛`（`ontology_graph islands`）三维分级，可 `python3 scripts/ontology_graph.py --format summary` 与 `ontology-validate` 重跑
2. **混乱清单与根因**：按 `结构漂移`（8桶 vs 5域映射）、`引用失效`（AGENTS.md 缺失引用）、`身份重复`（duplicate_task_ids/slugs）、`桩节点膨胀`（testable_signal grep桩）四类分级，每项含 `file:line` Source 与影响面
3. **热力图**：`pdca/core/zfs/bcachefs/report-center` 等域的完整度热力（mermaid），每域 ≥1 Source
4. **路线图**：`P0 本体结构`（8桶路由修复）/`P1 门禁对齐`（validate/islands + pdca-doctor 硬门禁）/`P2 增量规范`（新增节点 testable_signal 模板）三级，每级含 repair 策略与验证命令
5. **模板束缚度**：`prd.md/task.json/skill/8桶 frontmatter` 四模板按 `无束缚/轻度/中度/高度` 四级评级，`a填空化+b门禁过严` 为主因，`c词汇收敛` 为次因；对比 `模板约束 vs 无模板` 的方案多样性/假设覆盖度/HITL 次数，给 `3 条松绑策略`（可选章节/自由扩展区/模板豁免标记），并论证“本体完整性释创造性”（本体缺口为根因，补本体即释创造性）
6. **全量本体化**：`模板/知识/事实全量本体化`——模板四件套 + `knowledge/* + fact/* + pitfall/principle` 全量纳入 `ontology` 8桶本体，纳入版本与 `ontology-validate/islands/pdca-doctor` 门禁；给出 `frontmatter + relations + testable_signal` 统一规范与 `validate OK + islands:0` 可检路径，论证 `本体即唯一事实源，知识与事实全量本体化即完整性闭环`
7. **本体到代码**：`scripts/*.py` 与 PDCA 本体对应矩阵（`py 文件 ↔ ontology 节点` 溯源表），审计“代码私设本体”反向污染；立 `本体到代码单向` 原则——本体是源、代码是本体的 `testable_signal` 投射，不允许现有代码再有私设本体概念，给出 `本体驱动生成/校验` 的可检路径（`grep -r "class.*Gate\|def.*gate" scripts/ ↔ ontology:process/flow-*` 对应）

## 验收标准

- [ ] AC-1 矩阵已产：426+ 节点三维分级表可重跑，`grep -c` 可检桩节点数，`validate OK + islands:0` 可重跑
- [ ] AC-2 清单已产：四类混乱清单含根因与影响面，每项 ≥1 `file:line` Source
- [ ] AC-3 热力图已产：按域分，mermaid 可渲染且每域 ≥1 Source，`python3 scripts/ontology_graph.py` 可复核
- [ ] AC-4 路线图已产：P0/P1/P2 三级，每级含 repair 策略、testable_signal 模板与验证命令（`ontology-validate`/`pdca-doctor --json` 可检）
- [ ] AC-5 模板束缚已评：四模板四级评级已产，主因 `a+b` 次因 `c` 已分级，含对比与 3 条松绑策略，且“本体完整性释创造性”已论证（`本体缺口为根因` 可溯 `file:ontology/...`）
- [ ] AC-6 全量本体化已产：模板/知识/事实全量本体化规范已产（`frontmatter/relations/testable_signal` 统一三件套），纳入 `8桶` 版本与门禁可检（`ontology-validate OK + islands:0`），`本体即唯一事实源` 可溯
- [ ] AC-7 本体到代码已溯：`scripts/*.py ↔ PDCA 本体` 对应矩阵已产，每 `py` 文件可溯至本体节点，`代码无私设本体` 已检（`本体到代码单向`，本体是源、代码是投射可检）

## 关联本体节点

```
ontology:concept/pdca-task
ontology:concept/pdca-architecture
ontology:concept/knowledge-artifact
```

## 拆分映射

- 三维矩阵+热力图 -> research-report.md#审计
- 混乱清单+根因 -> research-report.md#清单
- P0/P1/P2 路线图 -> research-report.md#路线
- 模板束缚度+本体完整性论证 -> research-report.md#模板束缚
- 模板/知识/事实全量本体化规范 -> research-report.md#全量本体化
- py-本体对应矩阵+单向原则 -> research-report.md#本体到代码
