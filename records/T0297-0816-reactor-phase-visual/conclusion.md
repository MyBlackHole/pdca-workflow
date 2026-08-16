---
schema: pdca.asset/v1
id: T0297-0816-reactor-phase-visual
phase: check
source_ids:
  - backupstream-evolution-visual
  - reactor-phase-accounting-visual-v2
  - ac5-registration-receipt-v2
---

## 上下文

T0296 结论反馈「文字内容太多，缺少架构图、原理图与案例说明」。本任务对
T0295（backupstream v65-v101 演进学习）与 T0296（Reactor 相位会计）两份报告
分别产出独立图文版：Mermaid 为主 + ASCII 补充，案例用集成测试真实数据，
按各自主题配图，作为各自 evidence 新版本登记。

## 假设与结果

假设：以图为主、文字为辅的重写能提升报告可读性，同时不丢失源报告事实。

结果：
- 产出两份图文版报告（T0295 演进学习、T0296 相位会计），共 16 张 Mermaid 图
  全部通过 mmdc 渲染验证，每张 ≤20 行、中文标签、带图例（遵循 code-comments
  规范）。
- T0296 图文版含链路架构总览图、守恒分解原理图、会计域不相交时序图、
  三个诊断 finding（internal-phase-busy / residual-delay / phase-history-truncated）
  的真实数据数值案例与逐步演算。
- T0295 图文版含三条主线 timeline、架构分水岭图、四主线流程图、
  文档-代码漂移对照表。
- 经 Grill 补充方法论附录 A（守恒推导步骤、v100→v101 衔接、适用边界、
  五条改进建议完整清单）。

## 分析

逐条 AC 判定：

- **AC-1** ✓：T0295 图文版含演进时间线（拆三条 timeline，合计覆盖 36 提交
  v65-v101，v91 并入 v92）+ 分水岭图，提交信息不丢失。证据：
  `backupstream-evolution-visual`。
- **AC-2** ✓：T0296 图文版含链路架构图（flowchart LR）+ 守恒原理图
  （flowchart TD）+ 会计域不相交时序图（sequenceDiagram）。证据：
  `reactor-phase-accounting-visual-v2`。
- **AC-3** ✓：三个诊断 finding 均配真实测试数据（b-20/b-21/b-22 事件）数值案例
  与逐步演算，守恒等式与测试脚本逐值核验一致。证据：
  `reactor-phase-accounting-visual-v2`。
- **AC-4** ✓：16 张图全部 mmdc 渲染 OK、≤20 行、中文标签、图例、一张图一个
  意图。证据：`backupstream-evolution-visual` + `reactor-phase-accounting-visual-v2`。
- **AC-5** ✓：两份图文版分别登记为 T0295/T0296 evidence 新版本（register-evidence
  返回 registered/replaced），凭证见 `ac5-registration-receipt-v2`。
- **AC-6** ✓：文字压缩为图的必要补充（图例、关键结论、边界、方法论附录），
  不重复图已表达的信息。

收敛验证：`validate-convergence.py` 返回 `valid: true`，无 issues。

## 适用边界

- 图文版是源报告的**表现层重写**，未引入新分析，不改变 T0295/T0296 结论。
- 图文版事实以源报告、测试脚本（tests/backup_observe_diagnose_integration.sh）、
  源码行号为核验基准；36 提交条目沿用源报告（其已逐提交核验）。
- Mermaid timeline 语法较新，部分旧渲染器可能不支持（已验证 mmdc 可渲染）。
- 结论限于 v101（867da08）及当前 HEAD 状态。

## 下一轮建议

- 如需全项目级图形化，可将 T0295/T0296 之外的报告（如 T0265 等）纳入同规范改造。
- 若要在文档中嵌 Mermaid，建议统一约定渲染器（mmdc/GitHub/typora）以规避
  timeline 兼容性问题。
- 方法论附录 A 可作为「事件循环时间守恒分解」知识卡片的补充阅读材料。