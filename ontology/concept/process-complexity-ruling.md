---
schema: pdca.asset/v1
id: ontology:concept/process-complexity-ruling
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/process-complexity-ruling/1.0.0
summary: 流程复杂度判定规则（可维护性判据与执行层简化边界）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/meta-ontology
  - ontology:concept/ontology-creation-gate
  - ontology:domain/skill-research
attributes:
- name: maintainability_criterion
  desc: 复杂以可维护性为判据而非脚本数量
  constraint: 门禁可回归测试且职责可定位即不判复杂；75脚本为43条以上规则投射
  testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 断言OK，且统计 grep -l 本体投射 scripts/*.py 断言覆盖过半
- name: execution_only_simplification
  desc: 简化只动执行层不动门禁语义
  constraint: 合并脚本与统一入口允许；删减判定语义须另立改进任务授权
  testable_signal: 检查历次简化提交仅 upstream 执行层文件且门禁测试全绿，断言语义断言数不减少
---

# 流程复杂度判定规则（process-complexity-ruling）

来源：T2111，记录 `records/T2111-0910-process-complexity-review/conclusion.md`。Grounding：`scripts/transition-phase.py:142`、`scripts/pdca_core.py` 门禁段。

## 背景问题
脚本数量增长引发复杂性质疑，需明确判据与简化边界。

## 核心机制
1. 可维护性判据：可回归测试+职责可定位。（依据：`ontology:concept/meta-ontology`）
2. 投射解释：本体声明语义，脚本执行验证。（依据：`ontology:concept/ontology-creation-gate`）
3. 执行层简化：统一入口与合并校验逻辑。（依据：`ontology:domain/skill-research`）

## 适用边界
判定口径本身；简化实施另立项。

## 违反后果
以数量砍语义导致门禁退化为文档呼吁。

## 执行记录（T2127）
按分级裁决删25脚本与2测试文件、剪1测试6法：X4运行时导入、resolve×2被调、CI链、他人在途保留；全量失败集前后一致（仅少已删文件5旧失败），可revert。

## 关联导航
- 元本体：`ontology:concept/meta-ontology`
- 门禁：`ontology:concept/ontology-creation-gate`
