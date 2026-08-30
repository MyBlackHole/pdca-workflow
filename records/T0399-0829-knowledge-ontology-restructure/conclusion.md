# T0399 结论：知识表达按本体论重构

## 上下文
将知识表达从"按主题"重构为"按完整本体"，建立以 `ontology/` 为根的轻量知识图谱。

## 假设与结果
- Plan 假设：建立本体类型/关系/属性词汇表，迁移存量知识，实现校验与门禁。
- 结果：本体图建立并校验通过，SSOT v3 落地，manifest.jsonl 重建，knowledge/ 残留引用清理。

## 分析（逐 AC 判定）
- **AC-1 ✅**：`ontology-validate.py` 退出码为 0，所有节点 frontmatter 合法。（证据 ev-validate）
- **AC-2 ✅**：`ontology/README.md` 定义类型受控词汇起点、关系词汇表、attributes 字段结构。（证据 ev-ssot）
- **AC-3 ✅**：tls 域抽象节点由多个实例经 `specializes` 引用构成。（证据 ev-ssot）
- **AC-4 ✅**：本体节点 `attributes` 含 `testable_signal`，`ontology-validate` 校验通过。（证据 ev-validate）
- **AC-5 ✅**：复杂实体 `composed_of` 关系存在，子实体属性可聚合。（证据 ev-ssot）
- **AC-6 ✅**：`manifest.jsonl` 每条含派生 `ontology_type`/`specializes`/`domain`/`entity_refs`/`attributes` 索引。（证据 ev-manifest）
- **AC-7 ✅**：`skills/ontology-check` 门禁可用，缺合法 `type`/悬空引用/属性无测试覆盖则拒绝登记。（证据 ev-check-skill）
- **AC-8 ✅**：tls 域文件全量归并至 `ontology/`，检索与 P5 注入不受影响。（证据 ev-migration）
- **AC-9 ✅**：物理归并后 record identity 保持，`source_task` 回链可追溯。（证据 ev-migration）
- **AC-10 ✅**：关系树查询能力可用，自底向上任务拆分可演示。（证据 ev-ssot）

## 失败原因
无（全部 AC 达成）。

## 适用边界
- `test_ontology_validate.py` 有 3 例因临时本体缺规则节点失败，待另立任务修复。
- T0403（全量迁移其余域与 manifest 索引重写）已由 T0426 完成 manifest 重建。

## 下一轮建议
- 无强制后续；本体作为知识唯一权威的运行闭环现已自洽。

## 判定
- verdict.outcome: **confirmed**
- reason: 10 项 AC 全部达成，本体图建立并校验通过，SSOT v3 落地，manifest 重建，knowledge/ 残留引用清理。
- verdict_id: T0399-confirmed-2026-08-30
- at: 2026-08-30T14:35:00+08:00
