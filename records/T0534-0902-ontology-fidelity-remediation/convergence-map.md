# Convergence Map — T0534 本体保真度治理

> 逐条回链 `task.json:meta.convergence` → `prd.md:验收标准` → `evidence/manifest.jsonl` 已登记证据

| # | convergence (task.json) | PRD AC | evidence id | 验证 |
|---|-------------------------|--------|-------------|------|
| 1 | 本体“完整性”定义与可证伪度量已确立且门禁可执行（AC-1） | AC-1 | fidelity-criterion `ontology/concept/ontology-fidelity-criterion.md` | `grep -q '七项清单' ontology/concept/ontology-fidelity-criterion.md && grep -q 'fidelity score' ontology/concept/ontology-fidelity-criterion.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 \| grep -q 'OK'` |
| 2 | 存量本体空洞抽样审计完成：量化泛化signal/空正文/不可实现节点并分类分级（AC-2） | AC-2 | audit-report `records/T0534-0902-ontology-fidelity-remediation/audit-report.md` | `python3 scripts/audit-ontology-fidelity.py --ontology-dir ontology --out /tmp/audit.md --jsonl /tmp/f.json && grep -q 'fatal' /tmp/audit.md` |
| 3 | 至少1个示范域按“完整”标准重做为标杆：其attributes可独立派生实现且scaffold可证伪（AC-3） | AC-3 | demo-domain `ontology/domain/ai-efficiency-ticket-dag-ready-set.md` | `grep -c 'mermaid' ontology/domain/ai-efficiency-ticket-dag-ready-set.md \| awk '{exit !($1>=4)}' && python3 scripts/ontology_test_scaffold.py --node ontology:domain/ai-efficiency-ticket-dag-ready-set --out /tmp/x.py && python3 -m pytest /tmp/x.py -q` |
| 4 | 本体生产门禁已加固：拒绝泛化signal/空正文/无mermaid溯源/不可scaffold（AC-4） | AC-4 | gate-fidelity `scripts/ontology-validate.py` | `python3 /tmp/test_incremental_gate.py 2>&1 \| grep -q 'PASS'` |
| 5 | 存量本体分批修复路径与优先级已明确且首批修复可验证（AC-5） | AC-5 | roadmap `records/T0534-0902-ontology-fidelity-remediation/remediation-roadmap.md` | `grep -q 'P0' records/T0534-0902-ontology-fidelity-remediation/remediation-roadmap.md && grep -q '124' ontology/.fidelity-exempt.json` |
| 6 | 证据收敛可验证：convergence map逐条回链PRD验收与已登记证据且valid:true（AC-6） | AC-6 | convergence-map `records/T0534-0902-ontology-fidelity-remediation/convergence-map.md` | `python3 scripts/validate-convergence.py --task-dir pdca/tasks/0902-ontology-fidelity-remediation 2>&1 \| grep -q 'valid.*true'` |

**登记证据数**：5（fidelity-criterion, audit-report, demo-domain, gate-fidelity, roadmap）+ 本文件 convergence-map 即将登记 = 6

Source: `pdca/tasks/0902-ontology-fidelity-remediation/task.json:meta.convergence` + `pdca/tasks/0902-ontology-fidelity-remediation/prd.md:验收标准` + `records/T0534-0902-ontology-fidelity-remediation/evidence/manifest.jsonl`
