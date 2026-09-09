# 结论（T2115 修复本体缺口三原因）

## AC核验

- AC-1 AC规范：通过。证据`fix-ac-doc`（`pdca-acceptance-criterion`新增章节映射规则与禁用词，子agent T2116实现，`ontology-validate` OK）。
- AC-2 Grill必问：通过。证据`fix-grill-doc`（`grilling-methodology`新增覆盖必问轮，子agent T2117实现，`ontology-validate` OK）。
- AC-3 覆盖脚本：通过。证据`fix-coverage-script`（新脚本76行，`py_compile`过）+`fix-coverage-run`（严格词表跑出现本体3项缺失`nfs独立表达/密钥轮换/旧挂载点清理`，exit=1，子agent T2118实现）。
- AC-4 门禁引用：通过。证据`fix-gate-ref`（`scenario-research-first-gate`新增第5条Act覆盖自检，母票执行，编号已修正无重号）。
- AC-5 回归：通过。证据`fix-regression`（`ontology-validate` OK、T2107沉淀校验仍通过、723 signals refined）。

## 偏差与诚实说明

- 脚本是关键词触发器（tripwire）不是语义证明：宽松关键词会被R1/R2旧文本兜底命中（如本轮正例曾7/7全过），灵敏度取决于词表严格度；词表须逐源章节编制才有意义，已写入门禁引用条目。
- 3个叶票（T2116-2118）由子agent并行实现、母票集成验证；子票随母票交付不单独流转（`active=false`+留痕，沿用T2100-2102先例）。
