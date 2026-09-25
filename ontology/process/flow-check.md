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
dcterms_modified: '2026-09-25'
summary: Check：AI 直接依据权威、对象与证据审查，不用脚本重写 PDCA 语义
---

# Check：AI 直接审查事实与符合性

## 进入前

用户明确启动当前 Check run，绑定最新 Do 产物、固定 Plan、原需求、模型/映射及 AC/oracle。
同一任务保持原 Agent。检查对象变化使旧请求和旧 PASS 失效；不能复用旧证据证明新字节。

Check 的规则来源只读取当前动作需要的权威：当前 Skill、[按需读集](../LOAD-MAP.md)、
当前 phase/scene 方法、Plan 固定的 normative 规则，以及已经明确采用并固定版本的参考资产。
**禁止为了验证这些规则而再写一套项目专用 validator。**

## 四遍 AI 审查

### 1. Scope Review

先回答“实际改了什么”，不要先判断好坏：

- 对照 Plan 的目标、非目标、写域、required actions、AC/oracle；
- 查看真实 diff、最终产物、mapping、records 与 Do 证据；
- 标出 Plan 要求但未完成的遗漏；
- 标出 Do 实际产生但 Plan 未批准的范围膨胀；
- 对象、版本或摘要不一致时停止使用旧证据。

### 2. Consistency Review

直接阅读权威和实际内容，检查语义是否互相冲突：

- Skill ↔ phase 方法 ↔ scene 方法；
- authority ↔ Plan/AC ↔ implementation；
- model ↔ mapping ↔ target；
- task/request/response ↔ 实际阶段状态与授权；
- 当前规则 ↔ 已采用 reference 的版本和适用范围。

链接存在、字符串相同、命令退出 0 都不能替代语义一致性。发现两份权威互相冲突时记为 unknown/阻断，
不要由 Check 自行选择更喜欢的一份。

### 3. Adversarial Review

假设当前 Do 的结论是错的，主动寻找能够推翻它的反例：

- 是否有未覆盖的输入、边界、失败路径或并发路径；
- 是否能绕过授权、作用域、资源或状态约束；
- 是否存在 stale evidence、旧版本、错误对象或“两个错误互相证明”；
- 是否有上游保护使表面问题实际不可达，或表面正常路径隐藏真实违例；
- 是否存在与当前 claim 相反的证据。

找不到反例不是 PASS；必须再进入 Evidence Review。

### 4. Evidence Review

重要结论按 [EVIDENCE-01](../concept/pdca-evidence.md) 组织，不创建新的 ReviewContract：

- **subject**：被审对象及固定版本/位置；
- **authority / AC**：判断依据；
- **observation**：实际看到或执行得到的事实；
- **counterevidence**：主动寻找过的反证及结果；
- **reasoning**：事实为什么支持或不能支持结论；
- **limitation**：未覆盖范围、环境限制和不确定性。

缺少必需证据时使用 unknown/not_run；不得用“应该”“看起来”“另一个 Agent 也认为”补 PASS。

## 工具边界

AI 可以自主使用**通用事实工具**获取证据，例如：

- Git diff/status/show/log；
- 文本搜索、文件读取、JSON/YAML 解析器；
- shell/compiler 的语法检查；
- TARGET_ROOT 自己已有的 unit/integration/system tests、构建器和静态分析工具；
- 用户明确允许的外部事实来源。

这些工具只回答“事实是什么”。

**不得新增或依赖专门解释 PDCA 语义的验证程序**，例如用 Python/Shell 重新编码：
“必须有几个 Skill”“哪个 authority 必须是什么”“哪个阶段允许做什么”“哪些 ontology 能加载”等。
这类语义直接由 AI 读取当前权威进行审查。已有目标项目测试可以验证产品行为，但不能取代 PDCA 语义审查。

## 可选独立第二视角

当修改影响多个权威、授权边界、恢复语义或 Check 自身难以推翻原结论时，可使用宿主提供的独立 AI
作为**一次性只读第二视角**：

1. 只给 minimum sufficient review context：subject、固定 Plan/AC、相关 authority、diff/产物和已有证据；
2. 不把父任务完整活动历史作为默认输入；
3. 不创建新的 PDCA task/attempt，不让 reviewer 执行 Plan/Do/Act；
4. 不轮询、不监工；只消费一次原生返回；
5. reviewer 的结论只是待核验 claim，主 Check 仍按 EVIDENCE-01 验证其证据和反证。

需要真正独立的符合性场景时，仍由用户显式创建 [REVIEW-01](independent-work-review.md) / pdca-verify，
不能把一次性第二视角冒充正式 verification。

## Finding 与最终 Verdict

审查发现可在报告中用三个轻量标签表达，不新增持久化 schema：

- **BLOCKING**：有明确 authority/AC 和证据支持的违例；对应相关 AC 为 fail。
- **NON_BLOCKING**：不违反当前 AC 的维护性/设计建议；不能伪装成 fail。
- **UNKNOWN**：证据不足、权威冲突或环境无法核验；对应 AC 保持 unknown/not_run。

最终任务结论仍严格使用 [VERDICT-01](../concept/pdca-verdict.md) 的
pass/fail/unknown/not_run，以及 task_execution、subject_conformance、delivery_usable、scene coverage；
不要再建立一套平行评分系统。

## 完成与等待

保存真实证据、反证、Finding、局限和最终 verdict。向用户报告接受、返修、延期或失败归档选项，
然后停止。Check 不自动修改冻结业务对象，不自动回 Do，不自动进入 Act。
