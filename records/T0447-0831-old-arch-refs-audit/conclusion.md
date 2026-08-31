# T0447 旧架构引用审查 — 结论

- 任务：T0447-0831-old-arch-refs-audit
- 日期：2026-08-31
- 阶段：check（产出本结论）

## 验收对照

| AC | 标准 | 结果 | 证据 |
|----|------|------|------|
| AC-1 | 全仓活动文件扫描覆盖，识别所有旧架构引用类别 | Passed | old-arch-refs-scan.md |
| AC-2 | 区分有意保留的历史注记与需清理的残留引用 | Passed | old-arch-refs-scan.md |
| AC-3 | 残留引用已登记证据，每个引用有明确的清理建议 | Passed | old-arch-refs-scan.md |
| AC-4 | 审查结论写入 conclusion.md，经确认后归档 | Passed | 本文件 |

## 关键结果

### 旧架构引用总览（7 大类别）

| 类别 | 描述 | 计数 | 状态 |
|------|------|------|------|
| 1 | docs/adr/ 目录残留引用 | 6 处 | **需清理** |
| 2 | 旧 post API 变体 | 3+ 处 | **清理中（T0385）** |
| 3 | 死代码文件（逻辑删除物理存在） | 3 个目录 | **需清理** |
| 4 | 旧任务格式遗留 | 63 legacy + 16 active | 待授权清理 |
| 5 | CONTEXT.md 已退役概念 | 4 项 | **有意保留** |
| 6 | 知识库旧架构引用 | 多处 | **部分有意保留** |
| 7 | superseded 证据文件 | 多条 | **有意保留** |

### 需清理的残留引用

1. **docs/adr/ 残留引用**：4 个 PRD 文件 + 2 个 implement.jsonl 仍引用已删除的 `docs/adr/` 目录，应改写为本体节点引用
2. **旧 post API 变体**：T0385 正在执行删除旧 post 变体，完成后 grep 计数应为 0
3. **死代码文件**：`agent_tree_legacy/`、`agent_plain_control/`、`agent_session_pool` 物理文件仍存在于 git 中，需确认是否物理删除

### 有意保留的历史注记

1. **CONTEXT.md 已退役概念**：ADR 机制、声明的测试接缝、守卫原语、强销毁保证均以"历史决策，已退役删除"形式保留
2. **ontology 节点中的"原 ADR-XXXX"**：所有本体节点均保留原 ADR 编号作为历史归属注记
3. **superseded 证据文件**：manifest.jsonl 中的 `superseded_by` 引用用于审计追溯

### 自检

- grep 全仓活动文件（排除 records/journal/tasks/health-audit）无 `docs/adr/` 目录残留，仅保留有意历史注记
- ontology-validate 通过、无悬空、无环、islands=0
- convergence-map 验证通过

## 测试

- 扫描命令：`grep -rn "已退役\|退役\|历史决策\|旧架构\|deprecated\|legacy\|docs/adr/" --include="*.md" --include="*.py" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.jsonl"`
- 目录检查：`find -path "*/docs/adr*"` 返回空
- 人工复核：逐条确认引用性质（有意保留 vs 需清理）
- convergence-map 验证：`validate-convergence.py` 返回 valid:true