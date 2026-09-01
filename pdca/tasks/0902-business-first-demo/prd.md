# 业务首演练：新路径首单

## 背景
T0471/T0477/T0478 已完成本体叶→根树与 CI 硬门禁，但尚未有真实业务需求完整走 `拆分映射→tree_split→scaffold→frontier→convergence` 新路径。

## 目标
选一个最小可逆业务增量（ReportCenter 新增一个只读报表查询接口示例），完整演练新流程，产出首个业务侧本体即调度案例。

## 范围
- 输入：`ontology:entity/report-center-system` 树（T0477 已建，2叶1根）
- 输出：1个业务接口骨架（`report-web` 侧 `GET /api/report/demo` 桩）+ 对应本体 `attributes` + 测试 + 证据链
- 不做：不接真实 DB，不改 `collection-service` 调度，仅桩接口 + 本体沉淀

## 功能需求
1. PRD 含 `## 拆分映射`：`Demo 报表接口 -> ontology:entity/report-center-web-entity`，`tree_split` 输出 1叶1根验证
2. 为 `report-center-web-entity` 补 1条 `attributes`（含 `testable_signal`），跑 `ontology_test_scaffold` 生成测试骨架
3. 实现桩接口 `report-web/src/report_demo.py`（返回固定 JSON），加 `tests/test_report_demo.py` 契约测试
4. 登记 `test-result` + `convergence-map`，`validate-convergence valid:true`

## 非功能
- 桩接口可 `pytest` 直通，单任务本体数≤3

## 验收标准
- [ ] AC-1 拆分可调度：PRD 映射经 `tree_split` 输出 candidates 且 `frontier` `batches [[叶],[根]]`
- [ ] AC-2 本体即测试：`report-center-web-entity` 的 `attributes.testable_signal` 经 `scaffold` 生成骨架且测试通过
- [ ] AC-3 业务桩可验证：`GET /api/report/demo` 桩返回 `{"demo":1}` 且 `validate / graph / convergence` 全绿

## 关联本体节点
```
ontology:entity/report-center-system
ontology:entity/report-center-web-entity
ontology:domain/report-center
```

## 拆分映射
- Demo 报表接口 -> ontology:entity/report-center-web-entity
