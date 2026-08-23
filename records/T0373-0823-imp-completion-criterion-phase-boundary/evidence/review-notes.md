# 新杠杆回审记录：completion criterion 应用于 3 个高流量技能

杠杆定义：clarity（可判定边界，两级防御）+ demand（措辞驱动 legwork，穷尽性）。

## 回审 1：skills/grilling/SKILL.md Exit 节

- **Before**: "User revises → continue grilling until aligned."（aligned 无边界，何时算对齐由 AI 临场判断）
- **After 建议**: "User revises → 追问修订点所属分支并重算 frontier；Exit 仅当用户对五要素摘要回答'正确'，部分认可视为 revise 继续。"
- **杠杆归因**：clarity↑（"部分认可=revive"消除灰色地带）；demand 持平。
- **裁定**：值得在下一次动该文件时采纳（当前超预算 +1410B，单独为它豁免不值）。

## 回审 2：flows/flow-do/SKILL.md A2 切片循环

- **Before**: "先写失败的行为测试。再写最小实现。"（未要求观察红色状态——AI 可能写出即过的"伪失败测试"直接进实现）
- **After 建议**: "先写失败的行为测试并运行观察到红色输出，再写最小实现使其转绿；跳过红观察的切片不计入完成。"
- **杠杆归因**：clarity↑（红观察成为可检验事件）；demand↑（"每个切片都曾红过"是穷尽性措辞）。
- **裁定**：高价值。但 flow-do 是持平 baseline 锚点文件——按 T0371 约束留待 P9 试点任务一并处理，本任务不动。

## 回审 3：skills/write-conclusion/SKILL.md 完成判据行

- **Before**: "Completion criterion: conclusion.md exists and verdict is recorded."（verdict 记录了但可能缺字段/缺逐条 AC 判定——已知坑 T0265 正是这个缺口的事后补救）
- **After 建议**: "Completion criterion: conclusion.md 含 verdict 四字段（outcome/reason/verdict_id/at）且每个 AC 有 ✅/❌ 判定指向证据 ID；缺任一即未完成。"
- **杠杆归因**：clarity↑（四字段+逐条判定可 grep 验证）；demand↑（"每个 AC"穷尽性）。已知坑条款可随之退役（预防优于事后坑位）。
- **裁定**：采纳建议记入该技能下次修改时的待办。

## 结论

新杠杆在三个样本上均产出可操作改进：1 条立即价值（write-conclusion）、1 条需搭车（flow-do A2）、1 条低成本可选（grilling Exit）。理论有效性初步成立；配对实验级验证留待 P9 试点。
