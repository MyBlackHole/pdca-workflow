# 旧架构引用扫描证据

- 扫描日期：2026-08-31
- 扫描范围：全仓库（排除 .git/、records/、journal/）
- 扫描方法：grep 搜索已退役术语 + 目录存在性检查 + 人工复核

## 发现的旧架构引用

### 类别 1：已删除的 docs/adr/ 目录残留引用

`docs/adr/` 目录已于 T0419/T0420/T0421 清理删除，但以下文件仍引用该路径：

| 文件 | 行 | 引用内容 |
|------|-----|---------|
| `pdca/tasks/0820-tls-session-integration-test/prd.md` | 75 | `架构决策见 docs/adr/` |
| `pdca/tasks/0821-tls-keygen-cleanup/prd.md` | 93 | `架构决策见 docs/adr/` |
| `pdca/tasks/0823-handshake-cross-module-review/prd.md` | 53 | `架构决策见 docs/adr/` |
| `pdca/tasks/active/0808-backup-server-architecture/prd.md` | 96 | `架构决策见 docs/adr/` |
| `pdca/tasks/0817-rpc-handshake-negotiation/implement.jsonl` | 3 | `docs/adr/ADR-0001-openssl4-单库替代gmssl双后端.md` |
| `pdca/tasks/0823-async-object-lifecycle/implement.jsonl` | 4-5 | `docs/adr/ADR-0026-v81-plain-control-async.md`, `docs/adr/ADR-0029-async-object-lifecycle-contract.md` |

### 类别 2：旧 post API 变体（正由 T0385 退役中）

- `pdca/tasks/0823-async-lifecycle-retire-old-api/prd.md`：旧 post 变体仍在 reactor.hpp/cpp 中保留
- `pdca/tasks/0823-async-object-lifecycle/prd.md`：reactor post 回调有 6+ 个变体
- `ontology/domain/linux-epoll-eventloop-transport-ownership-model.md`：引用 `reactor_post_wait_priority`

### 类别 3：死代码文件（逻辑删除但物理存在）

- `agent_tree_legacy/`、`agent_plain_control/`、`agent_session_pool`：ROUND 文档声称"删除"但 git 中无删除记录

### 类别 4：旧任务格式遗留

- 63 个 legacy 任务 + 16 个旧格式活跃任务未获删除授权

### 类别 5：CONTEXT.md 中的已退役概念

- ADR 机制、声明的测试接缝、守卫原语、强销毁保证

### 类别 6：知识库中的旧架构引用

- legacy 端口引用、dead code 描述、兼容包装等

### 类别 7：superseded 证据文件

- 多条 convergence-map.superseded.* 文件

## 结论

项目仍存在大量旧架构引用，分为有意保留的历史注记和需清理的残留引用两类。
