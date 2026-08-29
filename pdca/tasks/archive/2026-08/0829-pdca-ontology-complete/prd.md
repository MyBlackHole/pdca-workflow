# T0411 PRD：补全 PDCA 元本体不完善节点使其完善

## 背景
T0410 校正了 PDCA 元本体与经典方法论的 2 处偏差（archive 扩展化、补循环概念、PDSA 注记）。但审计发现仍有"不完善"处（用户问"PDCA 方法论的本体是否完善"）：
- **G1**：根概念 `ontology/concept/pdca.md` 正文为空，方法论根缺定义性文字。
- **G2**：`ontology/concept/pdca-transition.md` 正文为空，转换元概念无说明（合法边清单/登记表在哪）。
- **G3（本次不处理）**：act→plan 循环仅概念节点 `pdca-continuous-improvement`，非可执行 transition 边——属设计取舍（保任务生命周期有终点 + ontology-validate 无环），不在本任务范围。
- **G4（可选深度）**：经典 PDCA 的"科学方法内核"（Plan=预测/假说、Do=小试验证、Check=比对预测与观测、Act=采纳/放弃）未在阶段定义显式体现，`phase-do`/`phase-check` 偏"按 AC 实现 / 对照 PRD"。

## 验收标准
- [ ] AC-1 `pdca.md` 正文补齐：定义 PDCA（Plan-Do-Check-Act / Deming Cycle / Shewhart Cycle）、起源（Shewhart→Deming，战后日本推广）、经典四阶段指针、持续改进循环指针，并枚举子概念（pdca-phase / pdca-transition / pdca-gate / pdca-evidence / pdca-verdict / pdca-acceptance-criterion / pdca-task / pdca-ontology-ready / pdca-continuous-improvement）。frontmatter 不变。
- [ ] AC-2 `pdca-transition.md` 正文补齐：说明合法 phase→phase 边由 `transition-*.md` 实体节点（specializes=pdca-transition，`composed_of:[phase-X,phase-Y]`）编码；列出当前合法边（plan→do / do→check / check→act / act→archive）；说明方法论循环 act→plan 由 `pdca-continuous-improvement` 概念承载而非 transition 边（保持无环）。
- [ ] AC-3 `phase-do.md` 与 `phase-check.md` 注入科学方法内核：Do=按预测做小试验证；Check=比对观测结果与 Plan 的预测/假说。保留既有任务执行语义，不删改既有字段。
- [ ] AC-4 测试：在 `tests/test_pdca_ontology_correct.py` 增断言 `pdca.md` 与 `pdca-transition.md` 正文非空且含关键标识（如 "Deming"、"composed_of" 或 "PDCA"）；`pytest` 全绿。
- [ ] AC-5 `docs/ONTOLOGY_GUIDE.md` 第 12 节补"PDCA 元本体完善说明（T0411）"；`verify-document` 自检 ok；`ontology-validate` 通过。

## 范围与边界
- 仅补内容与文档，不改 `ontology_reason.py` 算法、`task.schema.json`、`ontology-validate.py`、关卡判定规则。
- 不新增 `transition-act-plan.md`（G3 不处理）。
- 不改 `pdca-phase.md` 既有四阶段界定（T0410 已定）。
