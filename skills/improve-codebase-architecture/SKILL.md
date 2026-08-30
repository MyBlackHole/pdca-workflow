---
name: improve-codebase-architecture
description: 架构审查——先按近 30 天 git 变更热点聚焦扫描范围，检测 ontology/process/skills/pdca 结构的深化机会，生成含 Mermaid before/after 图与 Metrics 指标区的 HTML 报告到任务目录，选定候选后接 grilling + design-it-twice 走完设计树。使用场景：审查时或开发末尾捕捉结构漂移。
invocation: manual
---

# Improve Codebase Architecture — PDCA 版

对 PDCA 项目结构做架构审查，产出深化候选并走设计闭环。本技能可被"证明"：每次审查的候选/采纳/测试 seam 改善经 evidence 登记，形成跨轮次可比序列。

## 词汇（契约）

只使用 `skills/design-it-twice/SKILL.md` 的强制词汇：**module / interface / seam / adapter / depth / leverage / locality**。禁止 component/service/API/boundary。

## 流程

### 1. 热点定位（YAGNI——扫描前先定范围）

```bash
python3 "$PDCA_HOME/scripts/arch_review.py" --root "$PDCA_HOME" --out "$PDCA_HOME/pdca/tasks/<slug>/architecture-report.html" --days 30
```

- `arch_review.py` 先输出近 30 天 git log 高变更路径（`hotspots`）；有热点 → 以其为优先扫描起点；无热点（空列表）→ 全量扫描。
- 结合 `CONTEXT.md` 词汇与 `ontology/` 已有决策节点，不重新挑起已定案的架构决策。

### 2. 候选扫描（保留四维静态基线）

在原四维分析基础上，用热点路径优先：

1. **Flow coverage** — `scenario_type` 值是否缺对应 flow 路径？对照 `ontology/process/flow-do.md`。
2. **Skill consistency** — `ontology/process/flow-*/flow-*.md` 引用的 `skills/<name>/SKILL.md` 是否存在？报告孤儿与未引用。
3. **Knowledge–process mapping** — `ontology/domain/` 的原则在 `ontology/process/`/`skills/` 有无对应实现？
4. **File smells** — 超过 200 行的文件、重复步骤模式、混合职责。

对每个怀疑模块用 **deletion test**："删掉它会让复杂度集中还是只是搬家？"集中 → 深化候选。
对浅模块（interface 几乎与实现一样复杂）标注 locality 缺失：纯函数被抽取仅为可测试，但真实 bug 藏在调用方式里。

### 3. 生成 HTML 报告

调用 `scripts/arch_review.py` 把候选写入任务目录的 `architecture-report.html`：

- 每个候选一张卡片：files / problem / solution / benefits / before-after 图（Mermaid） / recommendation badge（Strong / Worth exploring / Speculative）。
- 末尾 `Top recommendation`。
- 报告内置 `#metrics` 数据块（candidates / strong / worth / speculative / top），机器可解析。

### 4. 指标登记（可证明性）

```bash
python3 "$PDCA_HOME/scripts/register-evidence.py" \
  --record <record-id> \
  --source <task-dir>/architecture-report.html \
  --id arch-review-<round> \
  --kind arch-report \
  --criterion <AC-id>
```

指标序列沉淀为 evidence，跨轮次可比：候选数 / 采纳数 / 采纳后测试 seam 改善数。

### 5. 设计闭环

用户选定候选后：

1. 跑 `skills/grilling/SKILL.md` 走设计树（约束、依赖、深化模块形状、seam 背后、存活测试）。
2. 需要对比接口时用 `skills/design-it-twice/SKILL.md`（并行产出 2+ 候选方案）。
3. 新模块名不在 `CONTEXT.md` → 加入；术语变模糊 → 就地更新。
4. 用户以关键理由否决候选 → 提供记 ADR 供未来审查不再重提。

## 输出位置

- HTML 报告写任务目录 `architecture-report.html`（可提交、可作 evidence），非 `/tmp`。
- 打印绝对路径；不在无头环境强制打开浏览器。

## 完成标准

- [ ] 报告已生成并含 Metrics 区（候选数、Strong/Worth/Speculative、Top 推荐）
- [ ] 指标已登记 evidence
- [ ] 选定候选已走完 grilling/design-it-twice 设计树

## 已知坑

- 审查先按近 30 天 git 变更热点聚焦扫描范围，勿全仓摊大饼；范围过大会稀释结论。
