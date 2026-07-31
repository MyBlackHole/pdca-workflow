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

## 步骤

### 0. 识别场景类型
读取 `task.json` 的 `meta.scenario_type`，选择对应执行路径。

---

## 路径 A：development（软件功能开发）

### 1. 原型验证（可选）
技术风险高或方案不确定时，先做原型验证：
- 创建原型代码验证关键假设
- 确认可行性后继续

### 2. 编码实施
按 `prd.md` 验收标准实现。复杂变更（5+ 文件）派发子代理并行执行。

### 3. TDD（红绿循环）
```bash
# 红：写失败测试
cargo test / pytest / go test / npm test
# 绿：实现通过
# 重构：清理代码
```

### 4. 代码审查（双轴）
加载 `skills/code-review/SKILL.md`（双轴并行子代理模式）：
- **标准轴**：对照编码标准 + Fowler 坏味基线审查。安全/质量领域注入 `skills/secure-coding/SKILL.md` 和 `skills/testing-strategy/SKILL.md`
- **规范轴**：对照 `prd.md` / issue 原始需求审查

合并报告，Blocking = 0 才通过门禁。大变更派发子代理，小变更主 session 内完成。

### 5. 登记证据
加载 `skills/register-evidence/SKILL.md`。

### 6. 提交代码
```bash
git add -A && git commit -m "task <id>: <描述>"
```

### 7. 进入 Check 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `check`。

---

## 路径 B：bugfix（Bug 修复）

### 1. 根因诊断
- 查看 `git log` 定位引入 commit
- 分析复现路径，确认根因
- 记录诊断结果到 `clarifications.jsonl`（`source: "diagnosis"`）

### 2. 修复实施
- 按最小改动原则修复
- 评估影响范围（加载 `skills/code-review/SKILL.md` 辅助）

### 3. TDD
- 编写暴露 Bug 的回归测试
- 确认修复通过，旧用例不退化

### 4. 代码审查（双轴）
同路径 A 步骤 4。

### 5. 登记证据
加载 `skills/register-evidence/SKILL.md`。

### 6. 提交代码
```bash
git commit -m "fix: <id> <bug描述>"
```
提交信息格式参考 `skills/bug-commit-format/SKILL.md`。

### 7. 进入 Check 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `check`。

---

## 路径 C：research（需求调研/技术调研）

### 1. 调研执行
- 按 `prd.md` 列出的调研问题逐条推进
- 收集外部资料、代码分析、竞品对比等证据
- 调研过程记录追加到 `clarifications.jsonl`（`source: "research"`）

### 2. 撰写报告
写入 `research-report.md`：
```markdown
## 调研目标
## 方法
## 发现
## 结论与建议
## 参考资料
```

### 3. 登记证据
加载 `skills/register-evidence/SKILL.md`。

### 4. 进入 Check 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `check`。

---

## 路径 D：documentation（需求转技术文档）

### 1. 文档编写
- 按 `prd.md` 结构和 `templates/to-spec/SPEC.md` 模板编写
- 完成 `design.md`、`spec.md`、ADR 等文档

### 2. 文档审查（双轴）
- **内容轴**：对照原始需求，确认覆盖完整、术语一致
- **格式轴**：结构清晰、Mermaid 图可读、无遗漏章节

### 3. 登记证据
加载 `skills/register-evidence/SKILL.md`。

### 4. 进入 Check 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `check`。

---

## 路径 E：design（架构设计）

### 1. 方案编写
- 加载 `skills/domain-modeling/SKILL.md` 辅助设计
- 产出 `design.md` + ADR（`docs/adr/ADR-NNNN-标题.md`）
- 更新 `pdca/CONTEXT.md` 中的术语

### 2. 设计评审
- 对照 `prd.md` 验收标准逐条验证
- 评估备选方案 trade-off
- 评审通过后方案基线化

### 3. 登记证据
加载 `skills/register-evidence/SKILL.md`。

### 4. 架构基线化
- 确认 `docs/adr/` 和 `pdca/CONTEXT.md` 已更新
- 若有代码骨架，提交基线代码

### 5. 进入 Check 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `check`。

---

## 路径 F：review（代码审查）

### 1. 审查执行
- 加载 `skills/code-review/SKILL.md` 执行双轴审查
- 安全/质量领域注入 `skills/secure-coding/SKILL.md`

### 2. 编写审查报告
写入 `review-report.md`：
```markdown
## 审查范围
## 标准轴发现
## 规范轴发现
## 风险评级
## 建议
```

### 3. 登记证据
加载 `skills/register-evidence/SKILL.md`。

### 4. 进入 Check 阶段
加载 `skills/advance-phase/SKILL.md`，目标 phase: `check`。
无代码变更，直接推进。

---

## 退出
- 完成: `meta.phase` = `"check"`
- 假设不成立 / 发现新信息: 回到 Plan 重新设计（`meta.phase` = `"plan"`）