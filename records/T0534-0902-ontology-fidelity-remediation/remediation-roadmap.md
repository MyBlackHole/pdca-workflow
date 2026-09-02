# 分批修复路线图 — T0534 本体保真度治理

> **策略（Q5/Q8确认）**：分 P0/P1/P2 三批，P0首批≥5已验证；增量零容忍，存量限期清零；fidelity score 与七项清单为优先级依据。

## 审计基线（2026-09-02）

- 全量413节点（ontology 409 md + 4 fidelity新增）
- `fatal` 236（57.1%）— 含泛化124 + 其他致命112（多为 MISSING_ATTRIBUTES/DIAGRAM 等）
- `泛化signal` 124（30.0%，已从129降至124，P0首批5清零）
- `无mermaid` 377（91.3%）、`无Source` 375（90.8%）、`正文<60行` 321（77.7%）

按类型均分：`domain` 16.4分 / `entity` 48.6分 / `concept` 12.9分 — domain空洞最严重。

## 优先级模型

```
优先级 = 高频复用 × 空洞严重 × 修复成本倒数
高频复用：按被 task.json/specs/skills 引用频次（ai-efficiency/core > backup > zfs/bcachefs > 长尾）
空洞严重：fatal > serious > minor；score越低越优先
修复成本：domain叶（~2h）< entity（~4h）< system聚合（~8h）
```

## 三批划分

### P0 — 高频复用域，致命泛化（2周，5+20节点）

| 批次 | 范围 | 数量 | 工时 | 验收 |
|------|------|------|------|------|
| P0-1 已完成 | `ai-efficiency` 泛化叶 5个 | 5 | 6h | 1个100分示范 + 4个80分轻量，validate 0 issues，fidelity 129→124 |
| P0-2 待 | `ai-efficiency` 剩余泛化 6个 + `core` 泛化 Top10 | 16 | 16h | 泛化清零，domain均分16→35 |
| P0合计 | 高频泛化全清 | 21 | 22h | `ATTR_GENERIC` 0，豁免清单清空 |

P0清单（剩余16）：
```
ontology:domain/ai-efficiency-ai-friendliness-review-methodology
ontology:domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms
ontology:domain/ai-efficiency-skills-candidate-review
ontology:domain/ai-efficiency-unified-entrypoint-discipline
ontology:domain/ai-efficiency-uplift-assessment-before-adoption
ontology:domain/ai-efficiency-writing-for-agents-levers
ontology:domain/core-btree-node-rewrite-key-extent-contract
ontology:domain/core-btree-random-op-consistency-proptest-pattern
ontology:domain/core-btree-split-proptest-enomem-restart-pattern
ontology:domain/core-combined-op-domain-model
...（按score升序取Top16）
```

### P1 — 中频业务域，缺图缺例（4周，80节点）

| 范围 | 数量 | 工时 | 验收 |
|------|------|------|------|
| `backup`/`benchmark`/`build-config` 等中频domain 40个 + `entity` 空洞15个 + `pattern` 5个 | 60 | 60h | mermaid≥1且Source齐全，score 35→60 |

### P2 — 长尾与元本体（6周，剩余）

| 范围 | 数量 | 工时 | 验收 |
|------|------|------|------|
| 剩余domain长尾 120个 + `concept`/`principle`/`pitfall`/`fact` 补齐 | 155 | 80h | 全量 pass ≥50%，islands:0，scaffold可产 |

## 首批验证（P0-1 已完成）

- **示范**：`ai-efficiency-ticket-dag-ready-set` 15→100分（3 attributes可执行 + 5 mermaid + Source行号 + 正反例 + 门禁，167行）
- **轻量**：`ai-efficiency-ai-execution-*`/`contract-scope`/`frontier-batch`/`lever-audit` 15→80分（去泛化+1图+Source+正反例）
- **门禁**：`ontology-validate` 对增量泛化 `ATTR_GENERIC` 拒绝已验证（`_test-generic-incremental` 用例 PASS）；存量豁免清单 129→124
- **审计**：`audit-report.md` 与 `/tmp/fidelity.jsonl` 已产出，`--check fidelity` 可回归

## 工时估算

- P0: 22h（已投6h，剩余16h）
- P1: 60h
- P2: 80h
- **合计**：162h（约20人日），建议按“每任务5节点”拆为32个子任务并行。

## 校验方式

```bash
# 每批次后
python3 scripts/audit-ontology-fidelity.py --ontology-dir ontology --out records/T0534/audit-report.md --jsonl /tmp/fidelity.jsonl
python3 scripts/ontology-validate.py --ontology-dir ontology  # 0 issues（含豁免）
python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0'
# 增量门禁冒烟
python3 /tmp/test_incremental_gate.py  # PASS
```

Source: `records/T0534-0902-ontology-fidelity-remediation/audit-report.md` + `scripts/audit-ontology-fidelity.py` + `ontology/.fidelity-exempt.json`
