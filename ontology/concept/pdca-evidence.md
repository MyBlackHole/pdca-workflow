---
schema: pdca.asset/v2
id: ontology:concept/pdca-evidence
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: EVIDENCE-01：把固定 claim 绑定到 observation 与反证
---

# EVIDENCE-01：Claim → Evidence

EVIDENCE-01 只回答：**某个固定 subject 上的某条 claim / AC，由哪些真实 observation 支持、反驳或仍无法判断。**
它不定义 case、不执行测试，也不汇总整个 task 的最终 verdict。

## Evidence binding

一条 evidence 至少绑定：

- subject/version；
- claim / acceptance ref；
- expected/oracle；
- actual observation；
- tool/raw result/source refs；
- counterevidence；
- local status；
- limitation。

`pass/fail/unknown/not_run/error` 是**这条 claim/AC 对当前 subject 的局部证据状态**：

- pass：actual 与固定 oracle 一致，且当前必要反证检查未推翻；
- fail：有可复核事实违反固定 oracle；
- unknown：证据不足、冲突或无法可靠解释；
- not_run：要求的观察没有实际发生；
- error：观察机制/基础设施失败，不能直接归因被审对象。

没有 run 不能补 PASS。测试器正确发现对象违例时，可以“测试执行成功 + claim fail”；
两者必须分开。

## Evidence hygiene

搜索不到名字不证明不存在；链接/摘要不证明语义；静态 observation 不自动证明动态行为；
未来设计风险与已观察违例分开。reviewer/Agent 的结论先是 claim，只有绑定可复核 observation 后才进入 evidence。

subject 变化会使相关 evidence 对新对象 stale；旧 evidence 不覆盖、不删除。
用户认可、风险接受或后续处置也不会改写 observed actual/local status。

整个 task 的 AC 聚合、subject_conformance、delivery_usable 与 scene coverage 只由 VERDICT-01 处理。
