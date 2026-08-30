# PRD：改造 out-of-scope-manager.py 以匹配 ontology/domain 扁平命名

## 背景
T0423 删除 `knowledge/`，out-of-scope 知识现以 `ontology/domain/out-of-scope-<concept>.md`（扁平短横命名）存在，`ontology/domain/out-of-scope.md` 为域根。`scripts/out-of-scope-manager.py` 是被 `skills/triage-work/SKILL.md`（wontfix 分支）实际调用的在役工具，但其 `concept_file()` 仍按 `<concept>.md` 写子文件，会生成 `ontology/domain/out-of-scope/<concept>.md`——父目录 `out-of-scope` 不是合法本体 type，导致 `ontology-validate` 失败；且 `list`/`check` 在不存在的子目录下查找，无法识别已迁移的扁平节点。

## 目标
改造工具以在 `ontology/domain/` 下以 `out-of-scope-<concept>.md` 扁平命名读写，并产出合法 frontmatter，使 triage wontfix 知识真正落入本体且通过校验。

## 验收标准
- [ ] AC-1：`concept_file()` 改为 `<out_dir>/out-of-scope-<slug>.md`；`--dir` 默认改为 `ontology/domain`；不再创建/依赖子目录 `out-of-scope/`。
- [ ] AC-2：`add` 新概念写入**单块**合法 frontmatter（`schema: pdca.asset/v1`、`type: domain`、`layer: Knowledge`、`status: active`、`domain: [ontology:domain/out-of-scope]`、`relations.specializes: [ontology:domain/out-of-scope]`、`relations.relates_to: [ontology:concept/pdca]`），并保留 `# <Title>` + `## Why this is out of scope` + `## Prior requests` 结构；追加路径同理兼容 frontmatter。
- [ ] AC-3：`list` 用 `<out_dir>/out-of-scope-*.md` 匹配；`check` 正确读取扁平节点上的 `## Why this is out of scope`。
- [ ] AC-4：`skills/triage-work/SKILL.md` 调用示例与说明同步（`--dir` 指向 `ontology/domain`，文件名 `out-of-scope-<concept>.md`）。
- [ ] AC-5：`tests/test_out_of_scope.py` 同步更新命名并通过；`ontology-validate` 通过（nodes 不降、islands=0）；登记证据 + 收敛映射 `validate-convergence` valid:true。

## 非目标
- 不改写现有 `ontology/domain/out-of-scope.md` 根节点内容（其「子主题」列表可后续维护）。
- 不改动除 out-of-scope 之外的其它知识写入路径。

## 设计要点
- frontmatter 风格与 T0423 迁移产出一致（单块 `pdca.asset/v1`），确保 `ontology-validate` 通过。
- 既有测试为临时目录自包含用例，需将文件名断言从 `dark-mode.md` 改为 `out-of-scope-dark-mode.md`，并新增 frontmatter 合法性断言。
