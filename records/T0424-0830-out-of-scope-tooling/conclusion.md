# T0424 结论：改造 out-of-scope-manager.py 以匹配 ontology/domain 扁平命名

## 上下文
T0423 删除 `knowledge/`，out-of-scope 知识现为 `ontology/domain/out-of-scope-<concept>.md` 扁平节点（`ontology/domain/out-of-scope.md` 为域根）。`scripts/out-of-scope-manager.py` 是被 `skills/triage-work/SKILL.md` 实际调用的在役工具（且有 `tests/test_out_of_scope.py`），但其 `concept_file()` 仍按 `<concept>.md` 写子文件，会生成 `ontology/domain/out-of-scope/<concept>.md`——父目录 `out-of-scope` 非合法本体 type，导致 `ontology-validate` 失败；且 `list`/`check` 在不存在的子目录下查找，无法识别已迁移节点。

## 假设与结果
- Plan 假设：工具可改为在 `ontology/domain/` 下以 `out-of-scope-<concept>.md` 扁平命名读写，并产出合法 `pdca.asset/v1` frontmatter，使 triage wontfix 知识真正落入本体的同时通过校验。
- 结果：工具扁平化 + 合法 frontmatter；`triage-work` SKILL 同步；单元测试 7 passed；`ontology-validate` 通过（探针节点经验证后清理，islands=0）；证据链 + 收敛映射 valid:true。

## 分析（逐 AC 判定）
- **AC-1 ✅**：`concept_file()` 改为 `<out_dir>/out-of-scope-<slug>.md`；`--dir` 默认改为 `ontology/domain`；不再创建/依赖子目录 `out-of-scope/`。（证据 ev-tool）
- **AC-2 ✅**：`add` 新概念写入单块合法 frontmatter（type=domain、layer:Knowledge、status:active、domain/specializes: ontology:domain/out-of-scope、relates_to: ontology:concept/pdca），保留 `# <Title>` + `## Why this is out of scope` + `## Prior requests`；追加路径兼容 frontmatter。探针 `out-of-scope-t0424-probe.md` 经 `ontology-validate` 通过（edges +2 后 OK）。（证据 ev-fm）
- **AC-3 ✅**：`list` 用 `out-of-scope-*.md` 匹配；`check` 正确读取扁平节点 `## Why this is out of scope` 段。（证据 ev-list）
- **AC-4 ✅**：`skills/triage-work/SKILL.md` 搜索路径 `ontology/domain/out-of-scope/` → `ontology/domain/out-of-scope-*.md`；示例命中 `dark-mode.md` → `out-of-scope-dark-mode.md`。（证据 ev-skill）
- **AC-5 ✅**：`tests/test_out_of_scope.py` 同步命名断言（含 frontmatter 合法性断言）并通过（7 passed）；`ontology-validate` 通过（nodes:239/edges:489/islands:0）；登记 5 证据 + 收敛映射，validate-convergence valid:true。（证据 ev-test）

## 失败原因
无（全部 AC 达成）。

## 适用边界
- 现有 `ontology/domain/out-of-scope.md` 域根的「子主题」列表未自动回填（本任务非目标）；后续若有实际 out-of-scope 概念写入，可选择性维护。
- `scripts/out-of-scope-manager.py` 反污染（`--implemented` 拒绝写入）逻辑保持原语义不变。

## 下一轮建议
- 无强制后续；本体作为知识唯一权威的运行闭环（flow-act 写入、triage wontfix 聚合）现已自洽。

## 已知坑
- `records/T0272-0815-self-audit/health-audit.md` 为 T0272 既有未提交改动，提交须始终排除。

## 判定
- verdict.outcome: **confirmed**
- reason: 5 项 AC 全部达成，工具扁平化并产出合法 frontmatter，ontology-validate 通过、单元测试通过、收敛映射 valid:true，triage wontfix 知识写入已闭环到本体。
- verdict_id: T0424-confirmed-2026-08-30
- at: 2026-08-30T12:20:30+08:00
