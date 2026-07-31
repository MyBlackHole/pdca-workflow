# T0108 PDCA 流程完整性审查报告

## 审查范围

- `README.md`、`flows/flow-{plan,do,check,act}/SKILL.md`
- `skills/advance-phase/SKILL.md`、`register-evidence/SKILL.md`、`verify-convergence/SKILL.md`
- `scripts/init-external.sh`、`templates/PDCA_HOME.md`
- 当前任务图、`pdca/tasks/archive/`、历史 T0103/T0104/T0105 结论
- T0108 PRD 与已创建的 T0109–T0113 子任务

本次为仓库内流程资产审查，无待审查的业务代码 diff；标准轴以流程契约、状态门禁和不可变记录规则为基准，规范轴以 T0108 PRD 为基准。

## 标准轴发现

### 🟠 W1 — 父子任务没有统一的聚合与阶段协调门禁

`flow-plan` 规定创建 `parent` 和 `children` 引用，但 `advance-phase` 只校验当前任务自身的确认、证据、结论和 disposition，没有定义父任务是否必须等待子任务、子任务失败如何传播、父任务归档前如何处理活动子任务。当前 T0108 可进入 Do，而 T0109–T0113 仍为 Plan，说明状态允许父子阶段脱节。

证据：`flows/flow-plan/SKILL.md:85-93`、`skills/advance-phase/SKILL.md:8-34`、当前任务图检查结果。

### 🟠 W2 — 归档命令缺少目录目标和 receipt/恢复契约的执行校验

`flow-act` 规定先通过 disposition 门禁再 `mv` 到 `archive/<YYYY-MM>/`，但执行规则没有要求校验目标目录、保存 receipt、验证父子任务引用或处理中断恢复结果。知识库已有归档故障恢复契约，说明该风险曾被识别，但 flow-act 本身没有把恢复产物列为退出条件。

证据：`flows/flow-act/SKILL.md:67-76`、`knowledge/information-architecture/archive-failure-recovery.md:16-27`。

### 🟠 W3 — Plan→Do 门禁只检查 `source`，没有验证确认记录的语义

`advance-phase` 只要求存在 `source: "final_confirmation"` 的行，没有明确要求 `response == "confirmed"`、确认摘要非空、确认记录对应当前 PRD digest，亦未规定方案变更后旧确认必须失效。这使得错误来源、未确认响应或过期确认有潜在绕过路径。

证据：`skills/advance-phase/SKILL.md:8-14`；`flows/flow-plan/SKILL.md:103-117`。

### 🔴 B1 — 根目录缺少 README 声明的 `AGENTS.md` 入口

README 明确要求 AI 自动读取项目根目录 `AGENTS.md`，但当前仓库 `find . -name AGENTS.md` 无输出。外部项目脚本只负责目标项目初始化，不能替代本项目根入口。该缺口会让新会话无法稳定获得 PDCA 路由、门禁和任务目录约定。

证据：`README.md:26`、`scripts/init-external.sh:13-26`、本次文件存在性检查。

## 规范轴发现

### 🟠 S1 — PRD 要求的“父任务闭环”尚未映射为可执行聚合判定

T0108 PRD 要求覆盖父任务依赖、聚合、失败传播、父先归档等路径；当前五个子任务各自有范围，但没有一个子任务或父任务字段定义聚合 verdict、阻塞条件和完成顺序。T0109 的 PRD 只描述审查范围，尚未给出可验证输出 schema。

### 🟠 S2 — PRD 要求内容来源可追溯，但当前任务产物只注入读取引用

`implement.jsonl` 已登记五个知识文件的读取动作，但未定义本次 review 的 evidence ID、record ID、knowledge disposition 或 manifest 验证目标；这些必须在 Check/Act 阶段补齐，不能以读取记录代替证据。

### 🟢 S3 — `AGENTS.md` 已有明确建设方向，但尚未产生文件

T0113 已把入口职责限定为轻量路由，范围与 README、`templates/PDCA_HOME.md` 一致；实际文件建设和冲突验证仍待 T0113 执行。

## 已覆盖项

- Plan→Do 存在 `final_confirmation` 记录且当前 T0108 已通过门禁进入 Do。
- 父任务 `children` 与五个子任务的 `parent` 引用互相对应。
- 当前所有 `task.json` 均可由 `jq` 解析；archive 中存在历史任务目录。
- flow-act 已显式要求 Act→archive 前检查 disposition。
- evidence manifest、knowledge manifest 和不可变 records 的规则在流程与知识库中均有引用。

## 风险评级

| ID | 严重度 | 状态 | 建议处置 |
|---|---|---|---|
| B1 | Blocking | open | 由 T0113 建设根目录 `AGENTS.md` 并加入一致性检查 |
| W1 | Warning | open | 由 T0109 定义父子聚合、依赖和失败传播门禁 |
| W2 | Warning | open | 由 T0110 把 receipt、恢复和引用校验写入归档流程 |
| W3 | Warning | open | 由 T0112 校验 confirmed、摘要和方案 digest |
| S1 | Warning | open | 将父任务聚合 verdict 写入 task schema/验收 |
| S2 | Warning | open | 由 T0111 定义 evidence/record/knowledge manifest 证据链 |
| S3 | Info | open | T0113 执行后回归验证 |

## 建议

1. 先执行 T0113，补齐根入口，再以新入口启动一轮最小 Plan→Do 门禁回归。
2. 并行完成 T0109–T0112 的规则审查，但每个子任务必须拥有独立 PRD、evidence manifest 和结论。
3. 修复完成后重新检查父任务是否能阻止“子任务未完成即归档”及“过期确认继续推进”。

## 结论

当前 PDCA 具备主要阶段和局部门禁，但尚未达到“父子任务、归档、内容沉淀、需求交互和项目入口均闭环”的完整标准。发现 1 个 Blocking、5 个 Warning、1 个 Info；本阶段不直接修改流程实现，转入 Check 形成正式 verdict。
