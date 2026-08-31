# T0448 旧架构引用再次审查 — 结论

- 任务：T0448-0831-old-arch-refs-recheck
- 日期：2026-08-31
- 阶段：check（产出本结论）

## 验收对照

| AC | 标准 | 结果 | 证据 |
|----|------|------|------|
| AC-1 | 全仓活动文件扫描覆盖，识别所有旧架构引用类别 | Passed | old-arch-refs-recheck-scan |
| AC-2 | 区分有意保留的历史注记与需清理的残留引用 | Passed | old-arch-refs-recheck-scan |
| AC-3 | 残留引用已登记证据，每个引用有明确的清理建议 | Passed | old-arch-refs-recheck-scan |
| AC-4 | 审查结论写入 conclusion.md，经确认后归档 | Pending | 本文件 |

## 关键结果

### 与 T0447 对比：无变化

本次再次审查确认，项目中旧架构引用残留与 T0447 审查结果完全一致，未进行任何清理。

| 类别 | T0447 结果 | T0448 结果 | 变化 |
|------|-----------|-----------|------|
| docs/adr/ 残留引用 | 7 处（6 需清理 + 1 有意保留） | 7 处（6 需清理 + 1 有意保留） | 无 |
| 旧 post API 变体 | T0385 在 plan 阶段 | T0385 仍在 plan 阶段 | 无 |
| 死代码文件 | 未在仓库中找到 | 未在仓库中找到 | 无 |
| 旧任务格式遗留 | 14 active + 归档 | 14 active + 归档 | 无 |
| CONTEXT.md 已退役概念 | 4 项有意保留 | 4 项有意保留 | 无 |
| 知识库旧架构引用 | 多处有意保留 | 多处有意保留 | 无 |
| superseded 证据文件 | 多条有意保留 | 多条有意保留 | 无 |

### 需清理的残留引用（6 处）

1. `pdca/tasks/0817-rpc-handshake-negotiation/implement.jsonl:3` — `docs/adr/ADR-0001-openssl4-单库替代gmssl双后端.md`
2. `pdca/tasks/0820-tls-session-integration-test/prd.md:75` — "架构决策见 docs/adr/"
3. `pdca/tasks/0821-tls-keygen-cleanup/prd.md:93` — "架构决策见 docs/adr/"
4. `pdca/tasks/0823-async-object-lifecycle/implement.jsonl:4-5` — `docs/adr/ADR-0026-v81-plain-control-async.md`, `docs/adr/ADR-0029-async-object-lifecycle-contract.md`
5. `pdca/tasks/0823-handshake-cross-module-review/prd.md:53` — "架构决策见 docs/adr/"
6. `pdca/tasks/active/0808-backup-server-architecture/prd.md:96` — "架构决策见 docs/adr/"

### 有意保留的历史注记（1 处）

1. `ontology/domain/linux-epoll-eventloop-rpc-conn-idle-reclaim.md:27` — "相关决策已随 docs/adr/ 退役删除"

### 未清理项

1. **T0385 旧 post API 退役任务**：仍在 `phase: plan`，未开始执行
2. **死代码文件**：`agent_tree_legacy/`、`agent_plain_control/`、`agent_session_pool` 可能存在于外部项目中
3. **旧任务格式遗留**：14 个活跃任务需授权清理
4. **CONTEXT.md 已退役概念**：有意保留

### 自检

- grep 全仓活动文件（排除 records/journal/tasks/health-audit）无新增 `docs/adr/` 目录残留
- ontology-validate 通过、无悬空、无环、islands=0
- convergence-map 验证通过

## 测试

- 扫描命令：`grep -rn "已退役\|退役\|历史决策\|旧架构\|deprecated\|legacy\|docs/adr/" --include="*.md" --include="*.py" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.jsonl"`
- 目录检查：`find -path "*/docs/adr*"` 返回空
- 人工复核：逐条确认引用性质（有意保留 vs 需清理）
- convergence-map 验证：`validate-convergence.py` 返回 valid:true

## 处置建议

1. **立即清理**：6 处 docs/adr/ 残留引用改写为本体节点引用
2. **推进 T0385**：旧 post API 退役任务应进入 do 阶段
3. **授权清理**：旧任务格式遗留需授权后清理
4. **确认死代码**：确认 agent_tree_legacy 等目录是否在外部项目中
5. **保持有意保留**：CONTEXT.md 已退役概念和 ontology 注记继续保留