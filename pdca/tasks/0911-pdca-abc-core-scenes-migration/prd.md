# A/B/C 核心场景与 skill 路由迁移

## 目标

将 PDCA 任务核心场景统一为 A/B/C，并移除六个旧 `scenario_type` 作为核心字段或兼容分支的使用。

## 验收标准

- [ ] AC-1: `ontology/concept/pdca.md` 与 `ontology/process/flow-do.md` 使用统一的 A/B/C 名称和分层语义。
- [ ] AC-2: task schema、任务创建、阶段门禁和场景检查统一接受 A/B/C，并拒绝旧六值。
- [ ] AC-3: 相关测试和 ontology 校验通过，且新增映射证据可复核。

## 变更范围

权威本体、Do 流程、schema、生产脚本及对应测试；不迁移或改写历史归档任务。
