# Conclusion — T0243 增强 diagnosing-bugs 技能（D1-D6）

## 结论

**已解决。** `skills/diagnosing-bugs/SKILL.md` 按 T0242 审查结论补齐 6 处差异
（D1-D6），并新建 HITL 模板与契约测试守护。全量测试 157 passed + 13 subtests，
seam 门禁通过，内容预算豁免已记录。

## 对照 PRD

| AC | 描述 | 状态 |
|----|------|------|
| AC-1 | Redact 前置约束（D1） | ✅ Phase 0 — Read context + Redact |
| AC-2 | 无环显式停止门禁（D3） | ✅ Phase 2 Explicit stop |
| AC-3 | 非确定性 bug 指引（D2） | ✅ Phase 2 Non-deterministic |
| AC-4 | HITL 模板路径（D4） | ✅ hitl-loop.template.sh（可执行） |
| AC-5 | post-mortem 架构移交（D5） | ✅ Phase 6 handoff |
| AC-6 | CONTEXT 前置 + 双向预测（D6） | ✅ Phase 0 + Phase 3 two-sided |
| AC-7 | 契约测试守护 | ✅ 10 测试（test_diagnosing_bugs_enhance.py） |
| AC-8 | 全量测试 + 内容预算豁免 | ✅ 157 passed，baseline 更新 2341→3908 |

## 关键实现

1. **Phase 0 前置**：合并 D1（Redact）+ D6（CONTEXT 读取），在触碰系统前
   先对齐共享语言并脱敏，一句"leak 凭据的 bug 比 bug 本身更糟"强化安全。
2. **Phase 2 门禁**：D3 显式停止（列尝试、要权限、无环不进 Phase 3）+ D2
   非确定性（100×/并行/时序窗，1% 不可调试 50% 可调试）。
3. **Phase 3 双向预测**：假设格式从单向改为 "disappear / make it worse"
   双分支，增强可证伪性。
4. **Phase 6 移交**：post-mortem 若指向架构问题，明确转
   improve-codebase-architecture，不在循环内丢失。
5. **HITL 模板**：可执行脚本，结构化驱动人工点击并记录结果。

## 验证

- 契约测试 10 passed（D1-D6 各有机器可读断言）
- 全量 157 passed + 13 subtests
- seam 门禁 checked=1, issues=0
- 内容预算 delta=0（baseline 豁免已显式更新）

## 收敛条件

CC-1 ✅ 全部 AC 满足
CC-2 ✅ baseline 豁免记录（pdca/skill-content-baseline.json, 2341→3908）
CC-3 ✅ D1-D6 均有契约断言守护
