# 半自动本体归纳辅助 — 规格文档

## 问题陈述

- **现状**：SSOT v3 知识归纳由 AI 在 Do 阶段手动完成（见 T0402 `design.md §8 归纳工作流（AI）`），无工具辅助；全量迁移（T0403）将大规模扩展本体，手动归纳易漂移、不可复现、难审计。
- **目标**：提供半自动归纳辅助，从多源输入按规则 / heuristic 抽取候选 frontmatter 骨架，生成 PR/差异供人工 review，复用 `ontology-validate` 闸门。
- **差距**：缺少从草稿 / 代码 / 资料到候选 frontmatter 的确定性抽取器；归纳过程不可复用、不可审计。

## 解决方案

新增 `scripts/ontology_induction.py`，分三层：

1. `adapter`：多源输入归一化为候选节点列表（首版实现 `knowledge/` 草稿适配器；代码 / web 适配器以接口预留）。
2. `induction`：heuristic 规则——`type` 推断（受控词汇）、`specializes` 候选（共性聚类 / 命名）、`guides` 候选（指向领域 / 过程实体）。
3. `output`：生成 frontmatter + PR/差异，不直接落盘 `ontology/`。

复用 `scripts/ontology-validate.py` 作候选落盘前闸门。

## Seam 分析

### 测试接缝

- 在 `scripts/ontology_induction.py` 的 `adapter` / `induction` / `output` 公共函数边界编写测试。
- 已有本体校验器可作 oracle：`ontology-validate` 断言候选图无环、引用非空悬、guides range 合法。
- Mock/Stub：以 fixtures 目录下的样例草稿与预期 frontmatter 快照隔离文件系统与外部源。

### 声明的测试接缝

- seam: tests/test_ontology_induction.py -> scripts/ontology_induction.py

### 验收可测性

- 每个 AC 均有 pass/fail 信号（脚本退出码 + 输出差异内容）。
- 边界：空输入、非法 frontmatter 源、跨环候选均可独立构造。
- 分层：单元测 induction 规则；集成测 adapter→output 端到端。

## 用户故事

1. 作为本体工程师，我想要从 `knowledge/` 草稿批量生成候选 frontmatter 骨架，以便减少手工归纳工作量并复现。
2. 作为迁移执行者（T0403），我想要归纳辅助产出 PR/差异，以便人工 review 后落盘，保持 HITL。
3. 作为 reviewer，我想要候选经 `ontology-validate` 闸门，以便不合规候选不会进入本体。

## 实现决策

- 新增模块 `scripts/ontology_induction.py`，CLI：`induce --source <path> --out <pr|diff>`。
- 接口：`Adapter` 抽象基类，`KnowledgeDraftAdapter` 首版实现；`induce(nodes)->candidates` 纯函数便于测试。
- `type` 推断：依据源文件名 / 标题关键词映射到受控词汇；未知回退 `concept`。
- `specializes` 候选：同形态实例按命名 / 目录共性聚类，提出抽象父节点 id。
- `guides` 候选：抽取源中出现的领域 / 过程实体 id（来自 `ontology/` 已有节点）作为候选目标。
- 不自动落盘；输出 PR/差异由人工 review 后合并。
- 架构决策：多源经适配器抽象承载"任何来源"承诺（首版仅 `knowledge/` 草稿），代码 / web 适配器为扩展点。

## 测试决策

- 行为测试为主，不测实现细节。
- 被测模块：`scripts/ontology_induction.py`。
- 先例：参考 `scripts/ontology-validate.py` 的故障注入测试范式。

## 验收标准

- [ ] AC-1: 给定 `knowledge/` 草稿目录，脚本产出候选 frontmatter 列表，每个候选的 `type` 属于受控词汇（TYPE_VOCAB）。
- [ ] AC-2: 候选 `specializes` 图经 `ontology-validate` 不报 `CYCLE` 或 `DANGLING_REF`（无环且引用存在）。
- [ ] AC-3: 脚本输出为 PR/差异格式（不修改 `ontology/` 目录内容，可由 git status 验证）。
- [ ] AC-4: 同输入产生同输出（确定性，无可变随机 / 外部网呼）。
- [ ] AC-5: 至少实现 `knowledge/` 草稿适配器；代码 / web 适配器以可导入的接口预留（导入点存在即可，不强制实现）。
- [ ] AC-6: 候选 `guides` 目标类型属于 DOMAIN_VOCAB（经 `ontology-validate` 的 `GUIDES_RANGE` 不报）。

## 范围外

- 自动生成 `attributes.testable_signal`（属性由人工补，避免自动失真）。
- 自动落盘本体（保持 HITL，须经 PR review）。
- 代码 / web 适配器完整实现（仅接口预留，首版不实现）。
- 全自动本体学习（ontology learning 的语义聚类）不在本期。

## 备注

- 依赖 T0402（已验证的本体基础架构 + 校验器强化）。
- 衔接 T0402 `design.md §8` 的"AI 归纳工作流"，将其工具化为"工具辅助 + 人工审核"闭环。
- 预期首个应用目标为 T0403 全量迁移的草稿归纳。
- 任务内部含 `adapter`/`induction`/`output` 三模块，作为单一 PDCA 周期交付，不拆子任务。

---
*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`。*
