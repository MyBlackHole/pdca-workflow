# T0423 PRD：将 knowledge/ 领域知识迁入 ontology/domain 后删除 knowledge/

## 背景
T0418~T0422 已将 docs/ 与 knowledge/ 桩内容析出进本体，确立本体为知识唯一权威。现 `knowledge/` 剩 123 个领域知识文件（649K，分布在约 28 个域目录），均为本体尚未承载的领域知识（存储引擎/TLS/备份/报表中心/AI 效率等）。用户确认"先迁入本体再删"：逐文件迁移为 `ontology/domain/*` 节点，校验通过后删除 `knowledge/`。

## 调研结论（接入方案，已确认）
- README §2 明列 `domain` 为合法 `type`；§64 指出 `domain/` 是与 `entity/` 同义的领域分组目录；§133 规定 `domain` 属性须指向既有 `domain/*` 节点。
- 约束：`type` 必须等于父目录名（故节点平铺于 `ontology/domain/`，type=domain）；引用无悬空；关系无环；图无孤岛。
- 接入：每个域一个**域根节点** `ontology/domain/<domain>.md`（type=domain，specializes pdca，relates_to pdca）；每个原文件一个**叶节点** `ontology/domain/<domain>-<slug>.md`（type=domain，specializes 域根，frontmatter `domain: [ontology:domain/<domain>]`），保证 file→root→pdca 连通、无孤岛。

## 验收标准
- [ ] AC-1：建立 `ontology/domain/` 接入方案——28 个域根节点（type=domain、specializes pdca、relates_to pdca）+ 逐文件叶节点（type=domain、specializes 域根、`domain` 属性指向域根），确保 type==父目录名、无孤岛、引用可解析。
- [ ] AC-2：123 个 `knowledge/<domain>/*.md` 逐文件迁移为 `ontology/domain/<domain>-<slug>.md`（保留原文正文 + 补 `pdca.asset/v1` frontmatter：schema/id/type/layer/status/summary/relations/attributes），脚本化生成。
- [ ] AC-3：处置 `knowledge/manifest.jsonl` 与 `knowledge/README.md`（索引/说明信息并入对应域根节点或删除，knowledge/ 不再保留索引）。
- [ ] AC-4：`ontology-validate.py` 通过、`islands=0` 后 `git rm` 删除 `knowledge/` 目录。
- [ ] AC-5：活动文件（AGENTS.md、flows/*、skills/*、ontology 节点、templates/* 等）对 `knowledge/` 的引用改写为 `ontology:domain/*` 节点。
- [ ] AC-6：登记证据 + 收敛映射，`validate-convergence.py` valid:true。
- [ ] AC-7：全仓（排除 records/journal/tasks）无指向已删 `knowledge/` 文件的实时引用；经 Check 撰写 conclusion 并获 verdict。

## 范围外
- 不对领域知识做内容改写/摘要（仅迁移 + 加 frontmatter），保真优先。
- `records/T0272-0815-self-audit/health-audit.md` 始终排除于提交之外。

## 风险与对策
- 节点数增多（89→~240）：靠脚本统一生成 frontmatter，迁移后跑 ontology-validate 逐条修。
- 大域（core 31 文件）：逐文件成节点，保持可寻址，避免单节点过大。
