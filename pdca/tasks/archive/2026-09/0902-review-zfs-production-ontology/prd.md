# 审查ZFS生产本体合理性 + 科学方法论保障下一次一次做对

## 背景
当前 ZFS 生产本体（`ontology/entity/zfs-system` 聚合六叶 + `domain/zfs-crypto`，T0503/T0513-T0518/T0522-T0524）已通过 `ontology-validate 0` 与 `islands:0`，但审查发现 `zfs-system:43行`单薄、`VDEV/ZIL` 未独立、`module/zfs` 30%面降级、100% Rule 不严格、`testable_signal` 半可回归。用户纠偏：**不做单点补丁，要以科学方法论保障下一次生产即满足本体要求**。需从 `METHONTOLOGY + NeOn + Ontology101 + OOPS!41 + OntoClean + PMI 100%/Yo-Yo + testable_signal→test` 全链提炼为可复用的生产门禁与模板，使后续任何生产本体（不限 ZFS）在 Plan 即被约束、Do 即被引导、Check 即被度量。

## 目标
- **审查**：以可复核命令完成六叶健康度/OOPS/100% Rule/可测性/生产完整性五维判定，输出分级缺口（已在 `records/T0525-*/report.md` 预检版完成 70%）
- **保障**：产出 **生产本体科学保障三件套**，使下一次生产本体满足 SSOT v3 七维门禁一次通过：
  1. **Checklist**（`pattern/production-ontology-scientific-gate` 结构化 `attributes + testable_signal`）
  2. **Gate 脚本**（`scripts/production-ontology-gate.py` 一键跑 validate+graph+scaffold+signal回放+100% Rule校验）
  3. **模板**（`templates/production-entity.md` 含决策树/正反例/门禁四件套占位 + `templates/production-system.md` 聚合模板）

## 范围
- 输入：`ontology/entity/zfs-*.md` 7 + `domain/zfs-crypto` + `pattern/scientific-research-methodology`/`research-diagram-methodology`/`scientific-research-lifecycle` + `domain/ontology-hybrid-methodology` + `pattern/ontology-evaluation-oops`/`ontology-metrics` + `scripts/ontology-validate.py`/`ontology_graph.py`/`ontology_test_scaffold.py`
- 输出：
  - 审查报告终版（补方法论根因：为何本次未一次做对）
  - 三件套实物（pattern + gate脚本 + 双模板）且被 `ontology-validate` 与 `ci-ontology-gate` 集成
  - 演示：以缺口 `zfs-vdev` 为例走一遍三件套，证明一次做对
- 不做：不实际补全全部 P0 实体（仅用 `zfs-vdev` 作走通演示，余缺口由后续 development 子任务按三件套自证）

## 功能需求
1. **五维审查终版**：在预检版上增“方法论根因”一节，解释缺口为何发生（缺 100% Rule 事前校验、缺 Yo-Yo 粒度门禁、缺 signal 双源可回归约束）
2. **科学门禁 Checklist（pattern）**：对齐 METHONTOLOGY 生命周期（specify→conceptualize→formalize→implement→evaluate）+ NeOn 9场景 + Ontology101 三准绳 + OOPS 41 + OntoClean + 100% Rule + testable_signal 七维，每维 `constraint + testable_signal` 可独立 `grep -q` 或 `gate.py` 单项校验
3. **Gate 脚本**：一键输出 `health: validate/islands/scaffold | structure: 100% Rule + 正交度 | testability: signal回放 | coverage: module/zfs文件覆盖率 | oops: critical` 的 JSON 与 `GATE OK/FAIL`，供 `ci-ontology-gate` 调用
4. **双模板**：`production-entity.md` 含 `attributes(≥3) + C4 L3 + 时序 + 状态机 + 决策树 + 正例 + 反例 + 门禁` 八段占位；`production-system.md` 含 `composed_of 100%声明 + 聚合决策树 + 正交度检查`，均含 `Source: file:line` 占位
5. **走通演示**：用三件套新建 `entity/zfs-vdev` 稿（≥60行+三属性+决策树+正反例），跑 `gate.py --node zfs-vdev` 一次通过，证明机制有效

## 非功能需求
- 全文中文；每条约束附 `Source: ontology/pattern/...:line` 或 `METHONTOLOGY/NeOn/OOPS` 原典
- 三件套本身需过 `validate 0` 且 `islands:0`，`gate.py` 可被 `ci-ontology-gate` 复用
- 不破坏现有六叶 `islands:0`，新增 pattern 的 `guides` 指向 `concept/domain-entity` 满足 AC-6

## 验收标准
- [ ] AC-1 五维审查终版已产且含方法论根因，每结论有 `Source: file:line`，`validate 0` 可复核
- [ ] AC-2 Checklist pattern 已落 `ontology/pattern/production-ontology-scientific-gate.md`，≥5 attributes 每条 `testable_signal` 含 `grep -q`/`gate.py` 动词且 `validate 0`
- [ ] AC-3 Gate 脚本已落 `scripts/production-ontology-gate.py`，`--help` 可见五维单项开关，`--node zfs-vdev` 与 `--all` 均 `GATE OK/FAIL` 可判定
- [ ] AC-4 双模板已落 `templates/production-entity.md` 与 `templates/production-system.md`，`wc -l ≥40` 且含八段占位与 `Source:` 占位
- [ ] AC-5 走通演示：`entity/zfs-vdev` 稿经三件套一次通过（`gate.py --node zfs-vdev` PASS + `validate 0` + `scaffold` 可产）
- [ ] AC-6 收敛：`validate-convergence.py --task-dir pdca/tasks/0902-review-zfs-production-ontology` valid:true 且 `disposition` 指向新 pattern

## 关联本体节点
```
ontology:pattern/scientific-research-methodology
ontology:pattern/research-diagram-methodology
ontology:pattern/scientific-research-lifecycle
ontology:domain/ontology-hybrid-methodology
ontology:pattern/ontology-evaluation-oops
ontology:pattern/ontology-metrics
ontology:entity/zfs-system
ontology:concept/domain-entity
（新增）ontology:pattern/production-ontology-scientific-gate
```

## 拆分映射
- 审查终版 -> 补根因一节
- Checklist pattern -> 独立 pattern 节点
- Gate 脚本 -> 独立脚本 + ci 集成
- 双模板 -> templates/
- 走通演示 -> zfs-vdev 稿
