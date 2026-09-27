---
schema: pdca.asset/v2
id: ontology:concept/task-unit-test
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: TEST-01：执行 case 并保存可复核 observation
---

# TEST-01：测试执行只产生 observation

TEST-01 只回答：**固定 case/subject 是否实际执行，以及观察到了什么。**
用例/oracle 由 CASE-01 固定，claim/evidence 解释由 EVIDENCE-01 完成，最终结论由 VERDICT-01 聚合。

每次实际 run 保存：

- case ref 与 subject/version；
- 实际 input/setup；
- tool/runtime/environment；
- 原始 command/action；
- raw output/result refs；
- exit/transport/infrastructure 状态；
- actual observation；
- limitation / 未覆盖范围。

没有真实执行就是 not_run。基础设施或测试器故障记录 error/unknown，
不能推定被测对象 pass/fail。命令退出 0、文件存在、字符串命中或多个 Agent 同意都只是 observation，
不能单独成为业务符合结论。

产品/模型改变后，只重跑受影响 case 与 Plan 明确要求的回归集合；旧 run 保留对应旧 subject 的历史事实。
TEST 不通过新增专用 PDCA validator 来解释流程语义；通用工具与 TARGET_ROOT 既有测试只提供事实。
