# T0421 引用清理证据

## 编辑清单
- `pdca/CONTEXT.md:19`：（ADR-0018）→「（历史决策，已随 docs/adr/ 退役删除）」
- `pdca/CONTEXT.md:32,33`：（ADR-0029）→「（历史决策，已随 docs/adr/ 退役删除）」（2 处）
- `scripts/ontology-validate.py:14`：ADR-0030 注释 → 指向 `ontology:concept/ontology-creation-gate` 决策背景（formerly ADR-0030）
- `scripts/ontology-validate.py:226,255`：同上（2 处）
- `pdca/skill-content-baseline.json`："Initial ADR-0007 baseline" → "Initial baseline"（25 处）

## 全仓最终校验（排除 records/journal/tasks/health-audit）
剩余 ADR-[0-9] 仅出现在：ontology/concept/*、ontology/README.md、docs/ONTOLOGY_GUIDE.md、skills/ontology-check/SKILL.md、scripts/ontology-validate.py 中的「原/formerly ADR-XXXX」历史归属注记（新约定，非悬空文件链接）。无任何 `docs/adr/` 前缀引用，无指向已删 ADR 文件的链接。
