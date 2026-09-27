---
schema: pdca.asset/v2
id: ontology:process/independent-work-review
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: REVIEW-01：独立 reviewer 只产生可核验 findings/claims
---

# REVIEW-01：独立审阅边界

REVIEW-01 只定义“**什么叫独立 review，以及它能产出什么**”。
它不定义 pdca-verify 的场景语义，不替代当前 task 的 Check，也不拥有最终 verdict。

## 独立性

reviewer 只接收 minimum sufficient review context：

- 固定 subject/version；
- requirement / AC / oracle；
- 必要 authority；
- diff/artifact/mapping；
- 已有 evidence 与明确 limitation。

默认不继承实现者完整 conversation、调试历史、临时假设或未采用 reference。
reviewer 对被审对象只读，不修改 implementation/model/oracle，不启动返工。

## 输出

review 输出是 findings/claims，不是“第二个权威结论”。每个 finding 至少指出：

- 被审位置/subject；
- 依据的 requirement/authority；
- 观察或需进一步核实的事实；
- counterexample / existing protection；
- limitation。

当前 Check 必须按 EVIDENCE-01 核验这些 claims；reviewer 数量、共识或置信度不能替代 evidence。

## 两种使用方式

- **一次性第二视角**：当前 Check 内部的只读 review pass，不创建 task/attempt；其 finding 回到当前 Check。
- **正式 pdca-verify**：用户显式创建独立 verification task；生命周期与 requirement→model→implementation→behavior 验证链只以 SCENE-01 / TASK-01 为准。

两者都可使用本页的独立性要求，但一次性 review 不得冒充正式 verification，
正式 verification 也不能用“独立 Agent”本身证明对象符合。
