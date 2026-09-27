---
schema: pdca.asset/v2
id: ontology:process/flow-check
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: Check：审查 scope/consistency/adversarial evidence，再由 VERDICT 聚合
---

# Check：AI 直接审查事实与符合性

## 方法边界

Check 的授权、predecessor、subject freshness 与 phase lifecycle 由 CONFIRM/GATE/TRANSITION/STATE 处理。
本页只定义 **Check run 已开始之后** 的审查方法。

Check 读取当前 subject、固定 Plan/AC/oracle、必要 authority、真实 diff/artifact/mapping 和已有 evidence。
不得新增项目专用 semantic validator 去复制 PDCA 规则。

## 四遍审查

### 1. Scope Review

先核对“实际对象是什么、实际改了什么”：

- Plan required actions / non-goals / write scope 与真实 diff/artifact 是否一致；
- 是否有遗漏或未批准范围膨胀；
- subject/version/digest 是否仍是本次 Check 固定对象；
- stale evidence 是否被错误用于新对象。

### 2. Consistency Review

交叉核对当前需要的 authority、Plan/AC、model/mapping、implementation 与 records。
链接存在、字符串相同、命令退出 0 都不能证明语义一致。
当前 authority 或固定 reference 相互冲突时保持 unknown/blocking，不由 Check 自选“更喜欢”的版本。

### 3. Adversarial Review

主动尝试推翻当前 claim：

- 边界/失败/并发路径是否遗漏；
- 授权、scope、resource、state 是否可被绕过；
- 是否存在旧对象、stale evidence 或“两个错误互相证明”；
- 是否已有保护使表面问题不可达；
- 是否有与当前结论相反的 observation。

没有找到反例不自动 PASS。

### 4. Evidence Review

对每个会影响 AC/verdict 的 claim，按 [EVIDENCE-01](../concept/pdca-evidence.md) 绑定真实 observation。

- 需要预先定义行为 oracle/case 时读 CASE-01；
- 需要实际运行工具/行为时按 TEST-01 保存 observation；
- 直接代码/模型/配置检查也必须固定 subject/source，并作为 observation 进入 evidence；
- reviewer finding 只按 REVIEW-01 当待核验 claim；
- 缺 actual、来源冲突或覆盖不足时保持 unknown/not_run/error。

本页不再复制 Evidence 字段表；精确 evidence record 以 EVIDENCE-01 与 record-shape 为准。

## 工具边界

Git、搜索/读取、解析器、编译器、TARGET_ROOT 已有 test/build/static-analysis 与获准外部来源都只是事实工具。
测试成功证明测试执行事实，不自动证明业务符合；测试器错误也不能直接归因 subject。

## 独立第二视角

需要一次性独立 reviewer 时按 [REVIEW-01](independent-work-review.md)：
只给 minimum sufficient review context，只读 subject，不创建新 task/attempt。
其 findings 回到当前 Check 经 EVIDENCE-01 核验。

正式独立 verification 必须由用户创建 `pdca-verify` task，其场景语义只由 SCENE-01 定义；
一次性 reviewer 不能冒充正式 verify。

## Finding 与 Verdict

BLOCKING / NON_BLOCKING / UNKNOWN 只是当前报告中的 finding 标签，不新增持久化评分体系。
是否使某个 AC fail/unknown，必须能回链到 EVIDENCE-01。

最终 Check 只按 [VERDICT-01](../concept/pdca-verdict.md) 聚合当前 subject 的 acceptance_results / subject_conformance。
task_execution、delivery_usable、scene_coverage 分别由生命周期、Act 和真实 scene records 在最终 delivery 中汇总，Check 不提前推断。

## 结果包与后续候选

固定 evidence refs、counterevidence、findings、limitations、acceptance_results 与 subject_conformance。
它们作为当前 Check run 的 result package 交给 TRANSITION-01；Check 不修改冻结 subject，也不产生后续授权。

Check 可以基于 verdict **说明候选方向**：

- 当前 Plan/baseline/AC/identity 不变且修复仍在原边界：按 REWORK-01 判断是否可形成同-attempt 新 Do candidate；
- 需要终态接受、限制性使用、失败归档或发布：形成 Act disposition candidate；
- 需要改变目标/oracle/model identity/Agent 或已 terminal：说明需要新 attempt/task candidate；
- 已存在 fixed task seed 且 dependency ready：可由 SCHED-01 另行形成 creation candidate。

候选只是导航；用户下一条真实操作决定进入哪个入口。
