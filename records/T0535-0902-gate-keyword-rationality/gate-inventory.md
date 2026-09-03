# 存量门禁清单（T0535 AC-2 实证 + 2026-09-03 增补审计）

> **增补说明**：T0535 原清单仅含 G6-G10 5 条（聚焦 fidelity），2026-09-03 全量审计 `scripts/*.py` 59 脚本（含 14 blocking 候选），扩展为全量门禁清单。节点基线 413（与 T0535 一致），实测时间 2026-09-03。

## 原清单（T0535）

| ID | 脚本 | 检查 | 触发率 | 判定 |
|----|------|------|--------|------|
| G6 | validate | ATTR_GENERIC | 30.0% (124/413) | 脆性但豁免可控 |
| G7 | audit | MISSING_DIAGRAM | 56.7% (234/413) | 过度（超10%阈值）但当前仅统计 |
| G8 | audit | MISSING_SOURCE | 56.4% (233/413) | 同上 |
| G9 | audit | BODY_TOO_SHORT | 44.6% (184/413) | 同上 |
| G10| audit | MISSING_EXAMPLES | 56.7% (234/413) | 同上 |

## 增补：全量门禁清单（2026-09-03 实测 413 节点）

| ID | 脚本 | 检查 | 模式 | 触发率（实测） | 分层 | 处置 | 合规性 |
|----|------|------|------|---------------|------|------|--------|
| G1 | validate | TYPE_DIR_MISMATCH/TYPE_VOCAB | 精确 | 0% | 精确层 | 保留硬阻断 | ✅ L3 0%阈值 |
| G2 | validate | DANGLING_REF | 精确 | 0% | 精确层 | 保留硬阻断 | ✅ |
| G3 | validate | CYCLE | 精确 | 0% | 精确层 | 保留硬阻断 | ✅ |
| G4 | validate | ATTR_NO_TEST_SIGNAL | 精确 | 0% | 精确层 | 保留硬阻断 | ✅ |
| G5 | validate | NO_GUIDES/GUIDES_RANGE | 精确 | 0% | 精确层 | 保留硬阻断 | ✅ |
| **G6** | **validate** | **ATTR_GENERIC** | **关键字双条件** | **0%（115 含 phrase 但 115 均含 verb → 0 阻断；audit 误判 115 为 fatal）** | **脆性层** | **保留但已优化** | **✅ 双条件生效** |
| G7 | audit | MISSING_DIAGRAM | 计数阈值 | 51.8% (214/413) | 统计层 | 降级：统计不阻断 | ✅ 已降级 |
| G8 | audit | MISSING_SOURCE | 计数阈值 | 51.6% (213/413) | 统计层 | 降级：统计不阻断 | ✅ 已降级 |
| G9 | audit | BODY_TOO_SHORT | 计数阈值 | 42.9% (177/413) | 统计层 | 降级：统计不阻断 | ✅ 已降级 |
| G10| audit | MISSING_EXAMPLES | 计数阈值 | 51.8% (214/413) | 统计层 | 降级：统计不阻断 | ✅ 已降级 |
| G11| validate | KNOWLEDGE_REF_CLEANUP | 精确 | 0% | 精确层 | 保留硬阻断 | ✅ |
| G12| production-gate | hundred/diagram/signal 等七维 | 混合（精确为主） | 抽样（仅 production 节点） | 精确层 | 保留（抽样 gate） | ✅ L2 外门聚合 |
| G13| check-design-vocab | FORBIDDEN_TERMS(4) 词边界 | 关键字窄域 | 按 doc-type 隔离 | 脆性层 | 保留（窄域+类型隔离） | ✅ T0234 教训已治理 |
| G14| check-research-ontology-settlement | GENERIC_PHRASES(2) 沉淀检查 | 关键字窄域 | 仅 act/archive research | 脆性层 | 保留（窄触发面） | ✅ |
| G15| resolve-skill-invocation | 调用契约校验 | 结构化 | 仅 skill 调用 | 脆性层 | 保留 | ✅ |
| G16| check-skill-structure | skill 结构校验 | 精确 | — | 精确层 | 保留 | ✅ |
| G17| ontology-clash-check | 图谱冲突 | 精确 | — | 精确层 | 保留 | ✅ |
| G18| generate-skills-index | 索引生成校验 | 精确 | — | 精确层 | 保留 | ✅ |

> **注**：G16-G18 等为低频精确校验，未计触发率但 0% 误报；全量 59 脚本中仅 14 个含 blocking 潜力，其余 45 个为工具类无阻断。详见 `research-report.md` 附录 C。

## 处置建议增补（L7-L12 启示）

| 门禁 | 原处置 | 增补处置（L7-L12 后） | 成本 |
|------|--------|----------------------|------|
| G1-G5 精确 | 保留 | **保留**，并为每条补充 1 个 negative test（L8/L10） | 0.5h |
| G6 脆性 | 保留+双条件 | **保留**，已验证双条件 0 阻断；补 negative test（注入纯泛化必失败） | 0.5h |
| G7-G10 统计 | 降级统计不阻断 | **保持降级**，后续可试点 L9 的 score→retry/queue 路由细化 | 0（现状） |
| G13 窄域关键字 | 保留 | **保留**，样板：类型隔离+词边界为脆性层最佳实践 | 0 |
| 新增语义类 | 替换候选（LLM-judge） | **替换候选**，需先以 L12 CALM 做偏见基线，固定 judge/rubric 版本 | 3人日（试点，含偏见基线） |
| 全量门禁 | — | **新增**：为 14 blocking 脚本建立“见过失败”回归套件（L10），豁免清单增 reason 审计（L11） | 1人日 |

Source: T0535 413 节点实证 + 2026-09-03 全量审计（`scripts/*.py` 59 脚本 + `ontology-validate --format json` + `audit-ontology-fidelity --jsonl`）
