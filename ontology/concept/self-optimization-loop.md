---
schema: pdca.asset/v1
id: ontology:concept/self-optimization-loop
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/self-optimization-loop/1.0.0
summary: PDCA 自我优化反馈链：记录→分析→决策→受控实施→效果验证，审计发现不是自动变更授权
relations:
  specializes:
  - ontology:concept/pdca-continuous-improvement
  relates_to:
  - ontology:concept/pdca-continuous-improvement
  - ontology:concept/knowledge-provenance
---

# 自我优化反馈链（self-optimization-loop）

## 核心认识

流程问题记录只是自我优化的观测层。完整闭环必须同时具备：

1. **记录**：在流程事件发生时保存结构化问题、阶段、时间和证据。
2. **分析**：跨任务聚合问题代码、频次、影响和趋势，区分偶发执行错误与系统性流程缺陷。
3. **决策**：形成可追溯的改进候选，说明依据、影响范围、风险和预期效果。
4. **受控实施**：候选仍进入正常 Plan、Grill 和 final confirmation，不能由审计器直接修改权威流程。
5. **效果验证**：在后续周期比较问题发生率或门禁失败模式，判断改善/无效/退化，并作为下一轮输入。

## 设计边界

- 审计发现是诊断信号，不是自动变更授权。
- 单次 fail 不足以证明流程规则需修改；需结合频次、影响和根因。
- 控制产物不能循环自证：改进效果必须由后续周期的新执行证据支持。
- 自我优化不能绕过 final confirmation、Check verdict 或 Act disposition。

## 最小反馈模型

`flow-audit records → issue backlog → improvement candidate → confirmed PDCA task → post-change observations → effectiveness verdict`

## Act 回顾检查清单（对接 retrospective 七分类）

Act 阶段执行回顾时，纵向仍沿用上述最小反馈模型完成 occurrence 到 verdict 的闭环；横向则按 `ontology:concept/retrospective` 定义的七类逐项扫描候选，避免自由文本遗漏：

- **Navigation**：是否缺少导航指针或入口映射导致寻址阻力
- **Automated checks**：是否有可拦截同类失误的 lint/类型/测试/文件系统校验缺口
- **Coding standards**：是否有可供审查视角强制执行的新规范
- **Global AGENTS.md**：是否有应从全局指令下沉至规范或检查的条目
- **Tool economy**：是否有可合并或轻量替代的高成本调用序列
- **No-ops**：是否存在无行为差异的无效转向条目
- **Information access**：是否有在只读边界内可扩展的信息可达性（如日志分流、只读观测）

扫描产出的候选不直接改写权威流程，仍进入“候选→确认的 PDCA 任务→跨周期效果验证”分支，由后续周期的新证据判定改善/无效/退化。

## 首次实现护栏

1. **事实不可变且可重试**：每个 occurrence 独立文件；调用方稳定幂等键确定事件 ID；相同内容重试返回 `unchanged`，不同内容必须拒绝。
2. **投影可删除重建**：issue backlog 按 versioned fingerprint 派生；稳定排序/规范化/输入 digest 让两次聚合可比较；损坏事实输入 fail-closed。
3. **确认必须精确绑定治理对象**：decision receipt 绑定 action/issue ID/candidate ID；candidate 先 dry-run，promotion 只创建 `phase=plan` 严格任务。
4. **cutover 是显式事实**：历史 `flow-audit/v1` 保持不变，仅全局 cutover receipt 存在后新 occurrence 写入。
5. **效果是下一周期判定**：冻结 baseline/指标/观察计划后 verdict 仅 `improved`/`neutral`/`regressed`；仅 improved 可形成 verified decision。

## 来源

- `（原知识层）self-optimization-loop.md`
- `（原知识层）real-usage-effectiveness-audit.md`
