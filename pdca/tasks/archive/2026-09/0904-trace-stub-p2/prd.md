# P2溯源与桩清偿：43py分类归零+桩改写+子单闭环

## 背景

`T2045 §7` 断言“代码无私设本体”过于乐观：实测 `scripts/*.py 60` 个中 `43` 个零 `ontology:` 引用，领域与基础设施混杂；`report-center/*.md:23` 自指式 `testable_signal`（`检查本文件完整性…`）约 12 处不可回归；`T2047/T2048/T2050/T2051` 四子单悬空（`plan/Pending`）。本切片按 `ontology:concept/template-minimal` 双轨制清零。

输入锚点：
- `file: scripts/*.py:1` — 43 零引用清单（`grep -L ontology:`）
- `file: ontology/domain/report-center/report-center-auth-rpc-compensation-patterns.md:23` — 自指桩样板
- `file: ontology/concept/template-minimal.md:1` — 豁免与三件套规范
- `file: scripts/ontology-validate.py:1` / `scripts/ontology_graph.py:1` — validate/islands 门禁

## 目标

43 个分类归零或豁免标注、桩全量改写为真可回归、四子单显式闭环，四检全过。

## 范围

- 输入：`scripts/*.py` 43 零引用、`ontology/domain/report-center/*.md` 自指桩、四子单
- 输出：溯源注释/豁免标注 + 桩改写 + 子单 `task_only` 归档 + 回归验证
- 不做：不改门禁语义；历史 duplicate 身份问题（P3，需解禁）不动

## 功能需求

1. **py溯源双轨**：领域概念补 `ontology:` 溯源注释，基础设施加 `NO-ONTOLOGY-INFRA` 豁免标注，`grep -L` 清单归零或全豁免
2. **桩改写**：自指式 `testable_signal` 全量改写为 `grep/python` 双检真可回归
3. **子单明确**：四子单（T2047/T2048/T2050/T2051）工作已落实父证据（T2046/T2049），子单留 `plan/Pending` 作 tracking 保留（与 `0904-ai-deep-sub` 等先例一致），不独立推进、不置 archive（archive 态需全套证据/结论/verdict，tracking 单不适用）

## 验收标准

- [ ] AC-1 py溯源已清：`grep -rL "ontology:" scripts/*.py` 输出为空或仅豁目标注文件，且抽查 5 处溯源注释可回溯本体节点
- [ ] AC-2 桩节点已改：自指桩清零（`grep` 计数为 0），`ontology-validate OK + islands:0 + doctor missing==[]` 全过
- [ ] AC-3 子单已明确：四子单留 `plan/Pending` tracking 保留且工作落实父证据，无独立推进义务（`Round2` 修订）

## 关联本体节点

```
ontology:concept/pdca-architecture
ontology:concept/template-minimal
ontology:concept/knowledge-artifact
```

## 拆分映射

- py溯源双轨 -> T2053 溯源
- 桩改写 -> T2054 桩
- 子单明确 -> T2055 追踪保留说明
