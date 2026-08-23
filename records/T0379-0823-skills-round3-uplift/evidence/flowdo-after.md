---
name: flow-do
description: |
  执行阶段执行流。根据 meta.scenario_type 选择执行路径。
  覆盖 development（编码）、bugfix（诊断修复）、research（调研）、
  documentation（文档）、design（设计）、review（审查）六种场景。
---

# 执行阶段执行流（PDCA — Do）

## 入口条件
- `task.json` 的 `meta.phase` 为 `do`
- `prd.md` 存在，含验收标准
- `meta.scenario_type` 已标记（无标记时默认 `development`）

## 路径索引

| 场景 | 路径 | 步骤 |
|------|------|------|
| development（编码） | A | A1–A5 + 通用收尾 |
| bugfix（修复） | B | B1–B4 + 通用收尾 |
| research（调研） | C | C1–C2 + 通用收尾 |
| documentation（文档） | D | D1–D2 + 通用收尾 |
| design（设计） | E | E1–E4 + 通用收尾 |
| review（审查） | F | F1–F3 + 通用收尾 |

读取 `meta.scenario_type`，直接跳转到对应路径。

### 可执行导航（AI）

路由决策的唯一机器可读来源是
`$PDCA_HOME/pdca/ai-friendliness-route-contract.json`，不要从 Markdown 标题猜测路径。
执行前运行：

```bash
python3 "$PDCA_HOME/scripts/resolve-ai-friendliness-route.py" --scenario "<meta.scenario_type>"
```

维护流程文档或合约后运行
`python3 "$PDCA_HOME/scripts/resolve-ai-friendliness-route.py" --verify-document`。
该检查只验证人类文档锚点；实际导航以 resolver JSON 输出为准。

## 通用：执行器容错

先读取 doctor 的 `agent.spawn` 能力结果。可用时通过当前环境 Adapter 调用；不可用时降级为主 session 顺序执行。执行器失败（超时/工具错误/拒绝）时：
1. 记录失败信息：`echo '{"task_id": "<id>", "path": "<路径步骤>", "error": "<描述>", "at": "<时间>"}' >> evidence/failed-tasks.jsonl`
2. 评估影响：判断是否为 Blocking
3. **Blocking**：主 session 接管该子任务手动完成
4. **非 Blocking**：跳过该子任务，在最终 evidence 中注明缺失

---

## 路径 A：development（软件功能开发）

### A1. 原型验证（可选）
技术风险高或方案不确定时，加载 `$PDCA_HOME/skills/prototype/SKILL.md`。

### A2. 测试优先实现循环
先加载 `$PDCA_HOME/skills/tdd/SKILL.md`，再按 `prd.md` 验收标准实施。复杂变更（5+ 文件）在 `agent.spawn` 可用时按独立模块分配；否则主 session 按模块顺序执行。

每个垂直切片严格按以下顺序：
1. 确认预先约定的 Seam。
2. 先写失败的行为测试。
3. 再写最小实现。
4. 完成每个垂直切片后运行定向测试或 typecheck，并保留结果供 evidence 使用。

子代理失败按「通用：执行器容错」处理。重构留到 review 阶段。

### A3. 最终验证
所有切片完成后运行项目支持的全量验证；项目没有独立全量命令时，运行现有最宽覆盖的验证并在 evidence 中说明限制。

### A4. 代码审查（双轴）
进入双轴代码审查。
加载 `$PDCA_HOME/skills/code-review/SKILL.md`（双轴并行子代理）：
- **标准轴**：编码标准 + Fowler 坏味基线。安全/质量领域注入 `$PDCA_HOME/skills/secure-coding/SKILL.md` 和 `$PDCA_HOME/skills/testing-strategy/SKILL.md`
- **规范轴**：对照 `prd.md` / issue 原始需求审查

合并报告，Blocking = 0 通过门禁。

### A5. 架构检查（可选）
技术债重或跨模块时加载 `$PDCA_HOME/skills/improve-codebase-architecture/SKILL.md`。

---

## 路径 B：bugfix（Bug 修复）

### B1. 根因诊断
加载 `$PDCA_HOME/skills/diagnosing-bugs/SKILL.md` 执行诊断循环。

### B2. 测试优先修复循环
先加载 `$PDCA_HOME/skills/tdd/SKILL.md`，再按最小改动原则修复。每个修复切片严格按以下顺序：
1. 确认回归 Seam。
2. 先复现并写出失败的回归测试。
3. 再做最小修复。
4. 完成每个修复切片后运行定向回归测试或 typecheck，并保留结果供 evidence 使用。

### B3. 最终回归验证
所有修复切片完成后运行项目支持的全量验证；项目没有独立全量命令时，运行现有最宽覆盖的验证并在 evidence 中说明限制。

### B4. 代码审查（双轴）
进入双轴代码审查。
同路径 A4。

---

## 路径 C：research（需求调研/技术调研）

### C1. 调研执行 + 撰写报告
加载 `$PDCA_HOME/skills/research/SKILL.md`。
Done when：报告落盘且每条关键结论附可复核验证途径（无途径的结论已降级标注）。

### C2. 调研报告审查
对照 `prd.md` 验收标准逐条检查报告完整性、引用格式，且每条关键结论含可复核验证途径（缺失即退回 C1 补齐）。
Done when：全部 AC 可映射到报告章节且引用格式零缺失。

---

## 路径 D：documentation（需求转技术文档）

### D1. 文档编写
按 `prd.md` 结构和 `$PDCA_HOME/templates/to-spec/SPEC.md` 模板编写 design.md、spec.md、ADR 等。
Done when：文档章节完整覆盖 PRD 全部验收标准，无待补占位符。

### D2. 文档审查（双轴）
- **内容轴**：对照原始需求确认覆盖完整、术语一致
- **格式轴**：结构清晰、Mermaid 图可读、无遗漏章节
Done when：双轴各自零 Blocking 发现，术语与 `pdca/CONTEXT.md` 一致。

---

## 路径 E：design（架构设计）

### E1. 方案编写
加载 `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`，产出 design.md + ADR，更新 CONTEXT.md。

### E2. 设计评审
对照 `prd.md` 逐条验证，评估备选方案 trade-off，通过后基线化。

### E3. 架构基线化
确认 ADR 和 CONTEXT.md 已更新，若有代码骨架则提交基线代码。

### E4. 基线代码提交
```bash
git add -A && git commit -m "feat(arch): <id> <描述>"
```

---

## 路径 F：review（代码审查）

### F1. 审查执行
加载 `$PDCA_HOME/skills/code-review/SKILL.md` 执行双轴审查，安全/质量领域注入 `$PDCA_HOME/skills/secure-coding/SKILL.md`。

### F2. 编写审查报告
写入 `review-report.md`：审查范围 / 标准轴发现 / 规范轴发现 / 风险评级 / 建议。

### F3. 架构检查（可选）
审查范围涉及架构层面时加载 `$PDCA_HOME/skills/improve-codebase-architecture/SKILL.md`。

---

## 通用收尾（所有路径）

所有路径（A–F）在本路径特有步骤完成后，统一执行以下收尾：

### Z1. 登记证据
加载 `$PDCA_HOME/skills/register-evidence/SKILL.md`。

### Z2. 建立收敛映射
按 `$PDCA_HOME/skills/verify-convergence/SKILL.md` 生成并登记
`convergence-map`，再运行可执行验证器。映射只描述
`meta.convergence → AC → evidence ID` 关系，本身不能作为验收通过证据。

### Z3. 提交代码（如有变更）
A 路径（development）和 B 路径（bugfix）执行 git commit。
E 路径（design）若已有代码基线也执行提交。
C/D/F 路径无代码变更则跳过。

### Z4. 进入 Check 阶段
加载 `$PDCA_HOME/skills/advance-phase/SKILL.md`，目标 phase: `check`。

---

## 退出
- 完成: `meta.phase` = `"check"`
- 假设不成立 / 发现新信息: 回到 Plan 重新设计（`meta.phase` = `"plan"`）

## 生效自检

- 每条关键结论/切片都有 evidence 登记且 digest 可复核
- C/D 路径产出满足各步 Done when；子代理失败按容错规则留痕于 failed-tasks.jsonl
