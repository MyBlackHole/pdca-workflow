# T0424 Triage（分诊）

## 触发
T0423 将 `knowledge/` 领域知识迁入 `ontology/domain/*` 并删除 `knowledge/`。收尾扫描发现：
- `scripts/out-of-scope-manager.py` 是被 `skills/triage-work/SKILL.md`（wontfix 分支）实际调用的在役工具，且有 `tests/test_out_of_scope.py`。
- 迁移后该工具 `--dir` 默认已改指 `ontology/domain/out-of-scope`，但其 `concept_file()` 仍按 `<concept>.md` 写子文件，会生成 `ontology/domain/out-of-scope/<concept>.md`：父目录 `out-of-scope` 不是合法本体 type，`type` 与父目录名不一致，`ontology-validate` 将失败。
- `list`/`check` 用 `out_dir.glob("*.md")` 在不存在的子目录下查找，无法识别已迁移的 `ontology/domain/out-of-scope-<concept>.md` 扁平节点。

## 范围
- 重构 `out-of-scope-manager.py`，使其在 `ontology/domain/` 下以 `out-of-scope-<concept>.md` 扁平命名读写，并产出/识别合法 frontmatter（type=domain）。
- 同步更新 `skills/triage-work/SKILL.md` 调用示例与说明。
- 修复并跑通 `tests/test_out_of_scope.py`、确保 `ontology-validate` 通过。

## 非范围
- 不改动 ontology/domain 已有的 out-of-scope-* 节点内容。
- 不重构 triage-work 的其它逻辑。
- knowledge/ 相关内容已删除，不回溯。

## 风险
- 工具写出的节点若 frontmatter 不完整，`ontology-validate` 失败；需在 add 时生成最小合法 frontmatter。
- 现有 test 可能依赖旧子目录布局，需同步更新用例。
