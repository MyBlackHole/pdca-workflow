# AC-4 证据：register-evidence 技能文档同步（T0414 锚定逻辑）

## 改动
- `skills/register-evidence/SKILL.md` 新增「--kind 与本体的锚定（来自 T0414 闭环）」：
  - `--kind` 必须命中允许集合，否则报错。
  - `pdca-evidence` 子类型短名（节点 `ontology:entity/evidence-<short>`，specializes `pdca-evidence`）→ 条目写入 `evidence_type_ref` 锚定本体（如 `convergence-map`/`review`/`test-result`）。
  - 支持型 kind（向后兼容）接受但不强制锚定。
  - 新证据类型优先定义为 `evidence-<short>` 节点后从 `--kind <short>` 登记。

## 验证
- 与 `scripts/register-evidence.py` 的 `evidence_subtype_map`/`LEGACY_SUPPORT_KINDS` 行为一致（人工复核通过）。
