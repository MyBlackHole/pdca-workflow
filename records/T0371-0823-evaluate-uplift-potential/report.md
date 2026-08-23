# mattpocock/skills 机制对本项目的提升潜力评估报告

> 任务：T0371 | 场景：research | 输入：records/T0370-0823-skills-ai-enhancement/report.md 第6节 P1-P9 及候选建议
> 日期：2026-08-23 | 方法：逐项现状核实（file:line）→ 五维评估 → 优先级综合

## 0. 总体判定（AC-4）

**判定：部分能提升——3 个候选项达到立项标准，2 个已被既有工作覆盖，其余应观察或放弃。**

依据链：

1. 初查即推翻上轮两条建议：code-review 的 repo-overrides 条款**已存在**（skills/code-review/SKILL.md:32 "项目标准优先于基线；基线坏味为 judgement call"），writing-great-skills 已由 T0245 增补双负载/锚定词/no-op/negation 转正向理论（:27,:49,:62,:111）——照 T0370 报告直接实施会造成重复建设。
2. 剩余候选中 **P3（research 可验证信号）** 成本最低收益直接，进"立即"；**P7（phase-boundary 决策树）与 P8c（completion-criterion 理论）** 是经核实后仍然成立的最大真实空白，进"短期"。
3. 结构性结论：本项目与对方的差距集中在**上下文经济学与完成判据理论**，而非流程刚性；且 T0230（frontier 问法）/T0245（写作四杠杆）已消化对方理论大半——剩余可落地增量比 T0370 报告估计的更小、更聚焦。

---

## 1. 现状核实表（AC-1）

| # | 候选项 | 核实结果 | 本项目证据 |
|---|--------|---------|-----------|
| 1 | P5 code-review 补 repo-overrides 条款 | **already-done** | skills/code-review/SKILL.md:32 |
| 2 | grilling 问句协议强化 | **already-done** | skills/grilling/SKILL.md:15-16 格式模板已在 |
| 3 | P8 双负载核算合入 writing-great-skills | **mostly-done**（缺 completion criterion 一节，拆出为 P8c 单独评估） | skills/writing-great-skills/SKILL.md:27/:49/:62/:111 |
| 4 | P1 Check 阶段 frontier 硬门禁化 | **partial** | flow-check Ch2 已要求加载 grilling 且有场景感知问题清单；无 round 记录的机器校验 |
| 5 | P3 research 场景补可验证信号要求 | **partial** | skills/research/SKILL.md 已有 primary-source 规则与置信度坑位；缺"结论须附可复核验证途径"；flow-do C2 仅查完整性与引用格式 |
| 6 | P4 执行器容错 Blocking 二分清单 | **partial** | flow-do 执行器容错节已有 Blocking/非Blocking 分支动作；缺显式判定标准 |
| 7 | P6 prototype-branch 证据类型惯例化 | **gap(小)** | register-evidence.py:38 kind 为自由字符串无需改码；缺惯例文档条目 |
| 8 | P7 phase-boundary 决策树入收尾 | **gap** | flow-do 收尾仅 Z1-Z4；grep boundary/compact/clear/smart zone 零命中 |
| 9 | P9 完成判据 demand 化 | **gap** | writing-great-skills 无 completion criterion 章节；flow 六路径步骤叙述式 |
| 10 | P2 子域术语块拆分 | **gap(暂缓)** | pdca/CONTEXT.md 单文件 38 词条尚可控 |
| 11 | wizard 人机分工向导 | **gap(低值)** | PDCA 场景少有纯人工流程 |

**成本约束发现**：pdca/skill-content-baseline.json 对 44 个资产设 bytes 基线。实测偏差——flow-do 持平（6783=6783），flow-check +46B、grilling +1410B（T0230 豁免）、research +122B、writing-great-skills +161B。**任何增补现有技能的建议都触发预算豁免流程**，是全部增补类候选项的共同成本。

---

## 2. 五维评估（AC-2）

评估对象 = 核实后有实施意义的 7 项。维度：预期收益 / 实施成本 / 风险 / 依赖 / 验证方式。

### E-1 P3 research 可验证信号

| 维度 | 评估 |
|------|------|
| 收益 | 高：research 是本项目高频场景（T0165、T0370 等先例），"结论附可复核验证途径"直接提升 Check 结论可信度，堵住纯叙述性结论绕过实证的口子 |
| 成本 | 低：skills/research/SKILL.md 加一条规则（约 150B 豁免）+ flow-do C2 加半句（约 80B） |
| 风险 | 低：不新增门禁脚本，靠 C2 审查执行 |
| 依赖 | 无 |
| 验证方式 | 回溯抽查最近 5 个 research 任务的 conclusion，按新规则尝试补写验证途径；若 4/5 以上可补出，证明规则可执行且历史确有缺口 |

### E-2 P7 phase-boundary 决策树

| 维度 | 评估 |
|------|------|
| 收益 | 高：活跃任务目录 57 个，跨 session 续作频繁；journal/handoff 已存在但"何时清窗/如何带上下文"无指引（对方以 smart zone 约 150k token 为界） |
| 成本 | 中低：**写入 handoff-work 技能而非 flow-do 主文件**——flow-do 的持平 baseline 最珍贵，handoff-work 本就是跨会话主题归属地（一次约 900B 豁免） |
| 风险 | 低：五选项树是决策参考非门禁，无脚本改动 |
| 依赖 | 无 |
| 验证方式 | 配对场景评测：构造两个需中途换焦点的长任务剧本，对比有无该节时 agent 清窗/交接选择正确率（参照 ai-friendliness-review-methodology） |

### E-3 P8c completion-criterion 理论合入 writing-great-skills

| 维度 | 评估 |
|------|------|
| 收益 | 高：premature completion 是 LLM 最高发失败之一；"clarity 防赶工 + demand 驱动 legwork"双性质是现有四杠杆未覆盖的第五杠杆，惠及全部 44 资产的后续编写与审查 |
| 成本 | 低：单文件 +约 700B 豁免（可与既有 +161B 超额合并陈述豁免理由） |
| 风险 | 低 |
| 依赖 | 建议先行于 P9 试点（先理论后应用） |
| 验证方式 | 用新杠杆回审 3 个高流量技能（grilling/tdd/register-evidence）步骤措辞，产出 before/after 对照确认行为描述更可判定 |

### E-4 P9 六路径 Done when 化

| 维度 | 评估 |
|------|------|
| 收益 | 高但分散 |
| 成本 | 高：flow-do 是路由合约锚点（resolve-ai-friendliness-route.py --verify-document 校验），六路径逐步改写工作量大且挤占持平预算；部分路径已有隐性判据（A2 切片顺序即判据） |
| 风险 | 中：大改锚点文件回归面宽 |
| 依赖 | P8c 理论先行 |
| 验证方式 | 故障注入（参照 ai-execution-and-invocation-contracts）：构造提前宣布完成的执行轨迹检验新判据拦截率 |

**裁定**：暂缓整体实施。降级为"P8c 落地后仅对 research/documentation 两低风险路径试点 Done when"，其余路径等试点证据再扩散。

### E-5 P1 check-grill 硬门禁化

| 维度 | 评估 |
|------|------|
| 收益 | 存疑：Ch2 软要求已明确且实践中 round 记录自然发生（T0370 即如此）；硬化边际收益低 |
| 成本 | 中：transition-phase.py 门禁逻辑扩展或新校验脚本 |
| 风险 | 中高：与本项目"必要处硬门禁、其余纪律软引导"分层哲学冲突；对方 issue #449 反面教训同样适用——给参考型环节加流程诱发机械执行 |
| 依赖 | 无 |
| 验证方式 | 先统计 10 个已归档任务 clarifications.jsonl 的 check 阶段 grill 记录率，低于 50% 才值得硬化 |

**裁定**：观察层，设触发条件后再立项。

### E-6 P2 子域术语块拆分

| 维度 | 评估 |
|------|------|
| 收益 | 中：38 词条尚可控，CDM/rpc/tls 密集但单屏内仍可导航 |
| 成本 | 高于表面：CONTEXT.md 被 doctor 引用检查（references_checked=60）与多技能 grep 引用，拆分涉及引用面迁移 |
| 风险 | 中：引用漂移 |
| 依赖 | 建议设触发阈值：词条超 60 或单域词条超 15 再拆 |
| 验证方式 | 拆分前后跑 pdca-doctor 全绿 + 技能 grep 引用零断链 |

**裁定**：观察层，阈值触发式。

### E-7 P6 prototype-branch 惯例文档化 + P4 Blocking 清单

| 维度 | 评估 |
|------|------|
| 收益 | 低中：prototype 使用频率低；Blocking 判定已有分支逻辑只缺显式标准 |
| 成本 | 极低：各自一行级增补（register-evidence 已知坑区 / flow-do 容错节） |
| 风险 | 极低 |
| 依赖 | P4 建议随下次动 flow-do 时搭车（避免单独豁免） |
| 验证方式 | 下一个含子代理失败的任务中观察 Blocking 判定是否一致 |

---

## 3. 优先级路线图（AC-3）

| 层 | 项 | 理由 |
|----|-----|------|
| **立即** | P3 research 可验证信号 | 成本最低（两处一行级增补）、收益直接（高频场景结论可信度）、验证方式现成（回溯抽查即可立项即验） |
| **短期** | P8c completion-criterion 合入 writing-great-skills；P7 phase-boundary 入 handoff-work | 经核实仍成立的最大真实空白；两者都刻意避开 flow-do 主文件与硬门禁，豁免成本各一次、无脚本改动 |
| **观察** | P1 check-grill 硬化（触发：记录率<50%）；P2 子域术语块（触发：词条>60 或单域>15）；P9 六路径 Done when（触发：P8c 落地后 research/documentation 试点通过）；P4 Blocking 清单（搭车：下次动 flow-do） | 全部设了明确触发条件，避免为改而改 |
| **不做** | P5 repo-overrides 条款（已存在）；grilling 问句协议强化（已存在）；wizard 向导引入（场景稀少，收益不抵维护） | 重复建设零容忍；低频能力不入主流程 |

路线图设计原则：每项"立即/短期"动作都绕开 flow-do 主文件或以最小增量进入，尊重内容预算机制；每个观察项带量化触发条件，把"要不要做"从主观判断转为可测量决策。

---

## 4. 总体判定的支撑依据链（AC-4 汇总）

判定"部分能提升"的三层依据：

1. **实证层**：11 个候选项中 2 个 already-done + 1 个 mostly-done——证明 T0370 报告的落地建议必须经现状核实才能执行，本评估直接避免了 3 处重复建设。
2. **机制层**：剩余真实空白（P3/P7/P8c）全部集中在上下文经济学与完成判据理论维度，恰好是本项目门禁体系覆盖不到的软性区域——互补而非重叠，提升逻辑成立。
3. **约束层**：内容预算基线使一切增补有真实成本，路线图因此收敛为 1 立即 + 2 短期，而非 T0370 报告暗示的 9 条并进——**聚焦后的实施概率远高于全面铺开**。

预期幅度（定性）：P3 落地后 research 任务结论可复核率从当前约 60%（估）升至 100%；P7/P8c 对长任务与技能编写质量的改善需按各自验证方式实测，不在本评估承诺范围内。

---

## 5. 后续动作建议

若用户批准路线图：
1. 为 P3 创建 Improvement Task（development 场景，改动 skills/research/SKILL.md + flow-do C2，含回溯抽查验证）。
2. P8c 与 P7 可合并为一个 documentation 场景任务（两文件增补+理论移植）。
3. 观察层各项登记到 journal 待触发条件出现时再评估。

## 6. 引用清单

| 本项目文件 | 用途 |
|-----------|------|
| records/T0370-0823-skills-ai-enhancement/report.md | 候选集来源 |
| skills/code-review/SKILL.md:32 | already-done 证据 |
| skills/writing-great-skills/SKILL.md:27,49,62,111 | mostly-done 证据 |
| skills/grilling/SKILL.md:15-16 | already-done 证据 |
| flows/flow-check/SKILL.md Ch2 | partial 证据 |
| skills/research/SKILL.md:14-16 | partial 证据 |
| flows/flow-do/SKILL.md 执行器容错节/Z1-Z4/C2 | partial/gap 证据 |
| scripts/register-evidence.py:38 | gap(小) 证据 |
| pdca/skill-content-baseline.json + audit-skill-content.py | 预算约束证据 |
| knowledge/ai-efficiency/{frontier-batch-grilling,writing-for-agents-levers}.md | 防重复建设对照 |
