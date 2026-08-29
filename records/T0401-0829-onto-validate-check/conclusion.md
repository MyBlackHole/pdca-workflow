# T0401 检查结论

## 收敛条件
Plan 收敛语句：`ontology-validate.py and ontology-check skill gate new asset writes and pass a smoke test against existing ontology assets`

## 验收判定
- **AC-1** ✅ — `scripts/ontology-validate.py` 校验 frontmatter `type` 必须等于父 `<type>/` 目录名，违规报 `TYPE_DIR_MISMATCH`（证据 `ev-validate`）
- **AC-2** ✅ — 校验 `relations.*` / `domain` 引用的 ontology id 在 `ontology/` 中存在对应节点，否则报 `DANGLING_REF`（证据 `ev-validate`）
- **AC-3** ✅ — 以 relation 引用构建有向图并 DFS 检测环，发现报 `CYCLE`（证据 `ev-validate`）
- **AC-4** ✅ — 校验每个 `attributes[].testable_signal` 非空，否则报 `ATTR_NO_TEST_SIGNAL`（证据 `ev-validate`）
- **AC-5** ✅ — `skills/ontology-check/SKILL.md` 定义新资产写入门禁流程（合法 type、引用非空悬、attributes 覆盖），并说明与 `ontology-validate.py` 的衔接（证据 `ev-check-skill`）
- **AC-6** ✅ — `tests/test_ontology_validate.py` 三个用例（clean 通过 / type 不匹配检出 / 空悬引用检出）全 PASS；冒烟运行真实 `ontology/` 返回 0 issues 且可解析 JSON（证据 `ev-test`）

## 证据映射
convergence map（证据 `convergence`）回链 ev-validate（AC-1..4）、ev-check-skill（AC-5）、ev-test（AC-6），无空悬引用。

## Verdict
- outcome: confirmed
- reason: AC-1..6 全部满足；测试接缝验证脚本能正确通过合规资产并检出 type/空悬违规
- verdict_id: V-T0401-0001
- at: 2026-08-29T18:25:00+08:00
