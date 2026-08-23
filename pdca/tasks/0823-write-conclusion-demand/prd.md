# 改进：write-conclusion 完成判据 demand 化与 AC 判定模板固化 — PRD

## 来源（三处汇聚）

1. T0373 回审产物：write-conclusion 完成判据"exists and verdict is recorded"过弱——verdict 记录了但可能缺字段/缺逐条 AC 判定，T0265 已知坑正是此缺口的事后补救
2. T0374 扫描：归档任务 conclusion 的 ac_judged 格式化率仅 40%（77/188）——判定内容存在但格式漂移，机器不可检索
3. T0372 衔接线索：research 可验证信号规则需在 conclusion 端有对应承接

## 方案（documentation 场景）

skills/write-conclusion/SKILL.md 单文件改造：
1. Completion criterion 升级为 demand 化判据："conclusion.md 含 verdict 四字段（outcome/reason/verdict_id/at）且每个 AC 有 ✅/❌ 判定并指向证据 ID；缺任一即未完成"
2. 模板固化：结论模板的"分析"节明确逐条 AC 判定行格式 `- **AC-x** ✅/❌ <一句话>（<evidence-id>）`
3. research 场景衔接：适用边界或分析节要求关键结论附可复核验证途径（与 skills/research 第 4 步呼应）
4. 已知坑 T0265 条款随判据前置化而更新（预防取代事后补救）
5. baseline 豁免同步

## 测试接缝声明

### 声明的测试接缝
- seam: 无独立测试文件——纯技能文档改造，验证方式为模板符合性抽查（见 AC-3），属 documentation 场景惯例

## 验收标准

- [ ] AC-1: write-conclusion SKILL 的 completion criterion 含四字段+逐条 AC 判定+证据指向三要素且声明"缺任一即未完成"
- [ ] AC-2: 模板含固定格式 AC 判定行示例（`- **AC-x** ✅/❌ ...（evidence-id）`）
- [ ] AC-3: 用新模板回查最近 3 个任务（T0372/T0373/T0375）的 conclusion 全部满足新格式（自反验证）
- [ ] AC-4: baseline 更新且 audit 零 budget issue；evidence 登记齐备 convergence valid

## 范围外

- 不改 transition-phase.py 校验逻辑（判据靠执行纪律，硬化留观察层）
- 不回溯改写历史 conclusion

## 备注

预期 +约500B 豁免，reason 引用三处来源。
