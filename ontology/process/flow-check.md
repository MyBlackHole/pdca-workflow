---
schema: pdca.asset/v1
id: ontology:process/flow-check
type: process
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/flow-check/1.0.0
summary: Check 阶段流程实体：对照 PRD/证据/收敛条件、verify-convergence 门禁、证据与结论锚定
relations:
  specializes:
  - ontology:concept/process
  part_of:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-phase
  - ontology:entity/phase-check
  - ontology:concept/pdca-evidence
  - ontology:concept/pdca-verdict
  - ontology:concept/pdca-acceptance-criterion
  - ontology:concept/pdca-architecture-review-metrics
---

# PDCA Check 流程（flow-check）

Check 阶段对照 PRD、证据与收敛条件，判定任务是否达成，是 PDCA 中"判定"环节。

## 阶段步骤（权威描述）

1. **对照验证**：依据 `prd.md` 的验收标准、登记的证据与 `convergence.json` 收敛条件逐项核验。
2. **verify-convergence 门禁**：阶段 Decision 必须引用证据；结论须映射 `pdca-verdict` 三态节点（confirmed/rejected/partial）。
3. **证据锚定**：`register-evidence --kind` 须命中 `pdca-evidence` 子类型允许表，写 `evidence_type_ref`。
4. **结论确认**：用户 `check_confirmation` 确认 verdict 后，方经门禁进入 Act。

## 关键决策（已迁移自外部知识）

- **架构审查可证明指标**（详 `ontology:concept/pdca-architecture-review-metrics`）：`arch_review.py::hotspots` 按近 N 天 git 变更频次定位热点；`render_html` 生成自包含 HTML（每候选一张卡片 + `#metrics` 带 `data-metrics` JSON）；审查结果经 `register-evidence --kind arch-report` 登记成跨轮次可比证据；测试断言结构契约而非 CDN 渲染细节。
- **自我优化审计教训**（详 `ontology:concept/self-optimization-loop` 与 `（原知识层）real-usage-effectiveness-audit.md`）：审计须先建独立真实参照集再检查捕获，不能用 occurrence 自证；发现能力分四轴（覆盖/信噪/可行动性/转化及时性）；三层证据（实现正确性/运行数据可用性/效果闭环）不可互相替代；AI 效率证据仅记录一次成功/返工、交互轮次、门禁失败，结构化遥测缺失时写 `unknown` 不得冒充。

## 来源

- `（原知识层）architecture-review-metrics.md`
- `（原知识层）real-usage-effectiveness-audit.md`
