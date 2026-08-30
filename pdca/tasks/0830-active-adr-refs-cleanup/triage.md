# T0421 triage

- 触发：全仓最终扫描发现 3 个活动机制文件仍含已删 ADR 悬空引用（此前按 `docs/adr` 前缀 grep 漏掉，因这些引用不带路径前缀）。
- 范围：仅以下 3 个活动文件，不改本体、不删文件。
  - `pdca/CONTEXT.md:19,32,33`：术语表括号内 ADR-0018 / ADR-0029 溯源（已删）
  - `scripts/ontology-validate.py:14,226,255`：代码注释 ADR-0030（已删，同类问题 skills/ontology-check 已修）
  - `pdca/skill-content-baseline.json`：生成式基线的 `reason` 字段 ADR-0007（已删，约 25 处）
- 不处理：`ontology/concept/*`、`ontology/README.md`、`docs/ONTOLOGY_GUIDE.md` 中的"原 ADR-XXXX"属有意历史归属注记（新约定），保留。
- 风险：纯文本/注释改写，不影响脚本行为；本体校验不受影响。
- 验收：grep 全仓活动文件（排除 records/journal/tasks/health-audit）无 `docs/adr` 及已删 ADR 悬空引用，仅保留本体节点「原 ADR-XXXX」历史注记。
