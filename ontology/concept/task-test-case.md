---
schema: pdca.asset/v2
id: ontology:concept/task-test-case
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: CASE-01：执行前固定 case 与 oracle
---

# CASE-01：执行前固定可判定用例

CASE-01 只回答：**准备验证什么，以及在看到 actual 之前，什么结果算满足/违例。**
它不执行测试、不记录 actual，也不生成最终 verdict。

每个 case 固定：

- acceptance / requirement ref；
- subject 及其固定 version/digest；
- setup / input / precondition；
- 可观察 action；
- expected oracle；
- failure condition；
- 适用范围与 limitation。

正例验证允许/期望行为；反例验证违规输入、错误路径或保护机制是否能被观察。
静态规则扫描只能声明为 static control case，不能冒充动态行为 case。

oracle 必须先于 actual 固定。看到结果后若发现 case 定义错误，应保留旧 case/run，
创建新的 case/version；不得修改 expected 去让现有 actual 变 PASS。

CASE 是 TEST-01 的输入，也是 EVIDENCE-01 解释 actual/expected 的依据。
