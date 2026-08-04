# CDM 报表中心落地拆解 — 规格文档

## 问题陈述

- **现状**: 需求 140 的最终技术方案 `cdm-report-center-final-technical-solution.md`（1580 行）已经冻结一期边界，但仍是单一文档，未转成可执行的工程任务；其引用的三个子方案契约文档（web_api / collection_service / cli）尚不存在，落地无契约基线。
- **目标**: 把该方案拆解为可逐个执行 PDCA 周期的独立子任务树，每个子任务有独立 PRD 与可测验收标准，并给出两侧仓库（aio-cdm / report-center）的落地路径。
- **差距**: 方案 → 任务树的映射未建立；子任务粒度、依赖关系、落地仓库均未定义。

## 解决方案

按交付域把方案拆成 8 个一级子任务（每个粒度为一次完整 PDCA 周期），补足首个子任务（三份子方案契约文档）作为全部实现任务的对齐基线；给出每个子任务的：目标、范围、仓库落地路径、依赖、验收标准。

## Seam 分析

### 测试接缝
- 主任务是"拆解"，本身以交付物（子任务树 + 各子 PRD + 验收标准）的可审阅度、与主方案的可追溯性为验收边界。
- 每个子任务的测试接缝（API / Repository 契约 / JSONL 校验 / RPyC Job 契约 / 模板 Handler golden 响应）由该子任务的 PRD 定义；本任务不写代码实现测试。

### 验收可测性
- 每个子任务 PRD 的验收标准用 checkbox `- [ ] AC-x:` 表达，可在该子任务 Do 阶段独立判定 pass/fail。
- 主任务验收：8 个子任务 `task.json`（parent 指向本任务）+ 各 `prd.md` + 依赖拓扑逐条可追溯回主方案章节（3.x / 4.x / 5.x / 6.x / 7.x / 8.x）。

## 用户故事

1. 作为报表中心工程负责人，我想要得到一份子任务树与每家 PRD 验收清单，以便把需求 140 拆成分阶段可交付、可直接进入各子任务 Do 的工单。
2. 作为契约维护者，我想要三份子方案文档先补齐，以便 report-web / collection-service / cdm-data-cli 各自实现有唯一契约输入。
3. 作为架构评审者，我想要子任务与主方案的逐条追溯，以便评审每个工单是否落在已确认的一期边界内。

## 实现决策

- 主任务 `scenario_type: development`，产出物为 8 个 plan 态子任务（`meta.phase: plan`，不进入 Do）。
- 子任务 ID 自当前最高 T0213 递增（T0214 起）。
- 每个子任务 `parent` 指向本任务 `T0140-0804-cdm-report-center-analyse`；本任务 `children` 列出全部 8 个 ID。
- 仓库归属（ADR-0013 修订版）：
  - aio-cdm 本仓：①契约文档、③cdm-data-cli、⑧验收压测中的 CLI/JSONL 侧。
  - 新建 report-center 仓库：②Report DB Adapter、④collection-service、⑤report-web、⑥报表模板+查询导出、⑦部署安装。
- 各子任务验收标准必须引用主方案章节号，确保可追溯。

## 测试决策

- 主任务本身不做代码测试；以 checklist 校验：8 子任务目录存在、task.json 字段合规、children 双向一致、每个子 PRD 含 `## 验收标准` 且为 `- [ ] AC-x:` 格式（供 P6 门禁扫描）。

## 验收标准

- [ ] AC-1: `pdca/tasks/` 下存在 8 个一级子任务目录，每个含 `task.json` 与 `prd.md`，`meta.phase=plan`、`status` 初始合规。
- [ ] AC-2: 每个子任务 `task.json.parent` 指向 `T0140-0804-cdm-report-center-analyse`，且父任务 `children` 反向包含全部 8 个 ID，双向一致。
- [ ] AC-3: 每个子 PRD 含 `## 验收标准` 段，条目为 `- [ ] AC-x: ...` checkbox 格式，且逐条引用主方案章节号。
- [ ] AC-4: 子任务无重复、粒度不小于一个 PDCA 周期，首个子任务为"补齐三份子方案契约文档"。
- [ ] AC-5: 每个子 PRD 明确仓库落地路径（aio-cdm 或 report-center）与依赖子任务列表。
- [ ] AC-6: 澄清日志 `clarifications.jsonl` 完整记录决策（grilling + direction_confirm），ADR-0013 反映修订归属。

## 范围外

- 不实施任何编码（子任务全部停留在 plan 态，P6 前禁止调度）。
- 不重写或修改主方案文档本身的内容结论。
- 不创建 report-center 空仓库实体（仅作为落地路径声明；实际建仓属子任务实施范围）。

## 备注

- 关联主方案章节索引：契约(1/3.4)、DB(3/3.5)、CLI(6/CLI子方案)、collection-service(2/4/5/6/7)、report-web(3.1/3.2/3.4)、报表(8)、部署(2.2/2.3)、压测(6.1.1)。
- 术语表已更新（报表中心/report-web/collection-service/cdm-data-cli/既有rpc工具/Report DB/JSONL采集/Topic）。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/ADR-0013`。*