---
schema: pdca.asset/v1
id: ontology:concept/pdca-architecture-review-metrics
type: concept
layer: Knowledge
status: active
summary: 架构审查的可证明指标与 HTML 可视化报告（热点扫描、#metrics JSON、arch-report 证据序列）
relations:
  specializes:
  - ontology:concept/pdca-acceptance-criterion
  relates_to:
  - ontology:concept/pdca-acceptance-criterion
---

# 架构审查的可证明指标与 HTML 可视化报告（pdca-architecture-review-metrics）

来源：T0264。

## 核心机制

1. **热点定位**：`scripts/arch_review.py::hotspots(root, days, limit)` 按近 N 天 git log 文件变更频次聚合，返回高变更路径；非 git 仓库返回 `[]`，调用方回退全量扫描。
2. **HTML 报告**：`render_html` 生成自包含 HTML（Tailwind + Mermaid CDN），每个候选一张卡片（files/problem/solution/benefits/before-after 图/recommendation badge）+ 末尾 Top recommendation，写入任务目录 `architecture-report.html`。
3. **结构化指标区**：`#metrics` 元素带 `data-metrics` JSON（`candidates/strong/worth/speculative/top`），可被 `re.search` + `json.loads` 机器解析。
4. **候选数据源**：`collect_candidates(root)` 按文件坏味（scripts/ 下 >200 行）自动生成深化候选。
5. **指标登记**：审查结果经 `register-evidence --kind arch-report` 登记，形成跨轮次可比证据序列。

## 经验教训

- CDN 依赖：离线时 HTML 退化为纯文本仍满足结构契约（测试不断言渲染细节）。
- **convergence 创建缺陷**：`task_identity.py` 原硬编码 `meta.convergence` 默认值为继承语境文本，已新增 `--convergence` 参数修复；创建任务必须显式传入收敛目标。
- 测试断言结构契约而非实现：热点用临时 git 仓库 fixture；HTML 只断言必选 section、字段齐全、Metrics 可解析。

## 关联

- （原 ADR-0025-html-architecture-review 已退役删除；相关决策未纳入本体）
- `skills/improve-codebase-architecture/SKILL.md`
- `scripts/arch_review.py`

## 来源

- `（原知识层）architecture-review-metrics.md`
