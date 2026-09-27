---
schema: pdca.asset/v2
id: ontology:process/flow-act
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: Act：执行当前 attempt 的终态处置并封存
---

# Act：Terminal disposition

## 方法边界

Act 的授权、Check predecessor、subject freshness、started receipt 与 running 状态由
CONFIRM-01 / GATE-01 / TRANSITION-01 / STATE-01 处理。
本页只定义 **Act run 已开始之后，对当前 attempt 的终态处置**。

如果用户在 Check 后选择 REWORK-01 判定成立的同-attempt Do rework，**不要启动 Act**；
直接等待新的 Do phase_start。Act 一旦完成并 archived，当前 attempt 不再回到 Do。

## 本阶段自主执行

只执行此次 Act request 明确列出的终态处置，例如：

- 接受/限制性接受当前交付；
- 对 fail/unknown 结果做诚实归档；
- 按授权发布当前 artifact/model/mapping；
- 结清或 retained 隔离资源；
- 用户明确要求时，按 LEARN-01 提炼/持久化/共享 learning candidate。

Act 不重新计算 Check verdict，不把风险接受改写为 subject_conformance PASS。
`delivery_usable` 只按这次明确处置的真实结果、限制和使用范围记录。

若当前 Check 指向需要**新 attempt/task** 的后续修复，Act 可以在归档说明中保留该候选，
但不创建它、不调用 SCHED 派发，也不把“未来要修”伪装成当前 attempt 的返工。

## 知识与发布

经验、项目 context、共享 reference/ontology 的写入都不是默认 Act 副作用。
只有 request 明确包含具体对象、写域和处置时才执行：

- learning extraction → LEARN-01；
- ontology revision → EVOLVE-01；
- shared reference publication 成功后仅进入 REUSE candidate pool；
- 其他 task 的 adoption 仍由其 ADOPT-01 决定。

## 结果包

固定最终 delivery、Act decision/operation evidence、真实发布结果、资源 released/retained 事实和实际 scene coverage。
随后按统一 completion 链记录 `phase_completed(act)`，同一 Act 授权下完成 terminalization 并写 `archived`。

归档不是第五阶段，也不产生下一 task/scene/attempt/rework 的授权。
