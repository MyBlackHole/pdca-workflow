# T0161 设计：执行循环与技能调用合约

## 架构边界

现有 `ai-friendliness-route-contract` 保持只负责 `scenario_type -> Do route`。T0161 增加两个并列 contract：

```text
flow-do.md ──document check──> ai-execution-contract ──> execution resolver
flows/skills ──frontmatter──> asset catalog ──┐
flows/skills ──explicit refs──> invocation contract ──> invocation resolver
```

JSON contract 是 alias、边和顺序的单一事实源；SKILL frontmatter 是 asset 名称和 invocation 类型的单一事实源。Markdown 保留给人类和 AI 阅读，resolver 负责证明其没有与 contract 分叉。

## Execution Contract

资产：

- `pdca/ai-execution-contract.json`
- `schemas/ai-execution-contract.schema.json`
- `scripts/resolve-ai-execution-contract.py`

每条 route 至少包含：`scenario`、`route_id`、`route_anchor`、有序 `loop` 阶段、`receipt_policy` 和用于文档校验的稳定 marker。仅允许 `development` 与 `bugfix`。

循环的语义固定为：

1. 选择或确认公共 Seam。
2. 先产生失败的测试（bugfix 为先复现/回归失败）。
3. 做最小实现或修复。
4. 对完成的垂直切片运行定向测试或 typecheck。
5. 在结束时运行项目支持的全量验证。
6. 进入双轴审查与现有 evidence/convergence 收尾。

resolver 的 `--scenario` 只返回 contract 中的结构化输出；`--verify-document` 读取实际 flow 文档，比较 route anchor 和 marker 的出现顺序。缺失、越界、重复、顺序漂移均 fail-closed，使用稳定 `EXECUTION_*` 错误码。

## Invocation Contract

资产：

- `pdca/skill-invocation-contract.json`
- `schemas/skill-invocation-contract.schema.json`
- `scripts/resolve-skill-invocation.py`

contract 包含两类对象：

- `aliases`：用户命令别名到 manual entry asset 的映射。
- `edges`：`from`、`to`、`document` 与显式 skill 路径引用。边不记录 invocation 类型。

resolver 建立 catalog 时解析 flows/skills 的 frontmatter。它验证 asset 存在、名称唯一、document 路径受 root 限制，并强制：

| source | target | 结果 |
|---|---|---|
| flow | automatic | 允许 |
| automatic | automatic | 允许 |
| manual | automatic | 允许 |
| flow/automatic | manual | 拒绝 |
| manual | manual | 拒绝 |

它还扫描每个 contract 指定 document 的 `$PDCA_HOME/skills/<name>/SKILL.md` 引用，确保每项都恰好有一个合法边，防止只更新 JSON 或只更新 Markdown。

## 迁移策略

保留外部 manual 名称，新增或抽取 automatic worker：

- `triage` -> `triage-work`
- `domain-modeling` -> `domain-modeling-work`
- `handoff` -> `handoff-work`

`flow-plan`、`flow-do`、`flow-act` 和 wayfinding 使用 worker。`grill` 继续是 manual 薄壳，但仅引用 `grilling` 与 `domain-modeling-work`。`wayfinding-work` 的 grilling 分支改为 automatic `grilling` 及所需 worker。`ask-matt` 从 invocation contract 的有效 alias 集选择入口，删除失效的 `/grill-me`。

## 验证拓扑

1. resolver 单元测试在最小临时根目录验证 schema、catalog 和稳定错误码。
2. 公共 fixture runner 对真实 resolver 执行正常路径，并注入顺序/边/别名/真实引用故障。
3. `audit-skill-content.py --check-budget` 调用新 contract 文档检查与 fixture，防止 baseline 更新掩盖行为漂移。
4. `generate-skills-index.py --check` 确认新增 worker 已可导航，doctor 与现有 lifecycle fixture 证明没有损坏门禁。

## 非目标与风险控制

新 contract 不读取、记录或伪造真实项目命令执行结果，不修改 `transition-phase.py`、task schema 或外部项目 task。文档 marker 只约束已声明的关键顺序，不尝试从任意自然语言推断 AI 的真实行为。
