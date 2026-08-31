# 全面清理旧架构引用

## 背景

T0448 再次审查确认项目仍存在与 T0447 相同的旧架构引用残留（7 大类别）。现发起全面清理任务，按类别逐一清理。

## 目标

清理全仓旧架构引用，使项目不再包含指向已删除目录/文件或仍使用旧模式的残留引用。

## 清理范围

### 类别 A：docs/adr/ 残留引用（已清理）

| # | 文件 | 操作 |
|---|------|------|
| A1 | pdca/tasks/0817-rpc-handshake-negotiation/ | 整个目录已删除（旧任务格式） |
| A2 | pdca/tasks/0820-tls-session-integration-test/ | 整个目录已删除（旧任务格式） |
| A3 | pdca/tasks/0821-tls-keygen-cleanup/ | 整个目录已删除（旧任务格式） |
| A4 | pdca/tasks/0823-async-object-lifecycle/ | 整个目录已删除（旧任务格式） |
| A5 | pdca/tasks/0823-handshake-cross-module-review/ | 整个目录已删除（旧任务格式） |
| A6 | pdca/tasks/active/0808-backup-server-architecture/ | 整个目录已删除（旧任务格式） |
| A7 | ontology/domain/linux-epoll-eventloop-rpc-conn-idle-reclaim.md:27 | 已改写 "相关决策已随 docs/adr/ 退役删除" → "相关决策已随 ADR 机制退役删除" |

### 类别 B：旧 post API 变体

- T0385 任务已不存在（随旧任务目录删除）
- 旧 post API 变体代码不在本仓库中

### 类别 C：旧任务格式遗留（已删除）

- pdca/tasks/active/ 下 14 个旧格式任务已全部删除
- pdca/tasks/ 下 100+ 个旧格式任务目录已全部删除
- 所有旧任务数据已从活动区域移除

### 类别 D：死代码文件

- agent_tree_legacy/、agent_plain_control/、agent_session_pool 未在仓库中找到

## 验收标准

- [ ] AC-1：全仓 grep `docs/adr/`（排除 records/journal/tasks/archive）在活动文件中计数为 0 ✅
- [ ] AC-2：ontology/domain 中 `docs/adr/` 引用已改写为本体节点引用 ✅
- [ ] AC-3：旧任务格式遗留已删除 ✅
- [ ] AC-4：清理后 `ontology-validate` 通过，无悬空，无环

## 关联本体节点

```
ontology:concept/pdca-task
ontology:domain/linux-epoll-eventloop-rpc-conn-idle-reclaim
```

## 依赖

- T0448（旧架构引用审查）已完成，结论已确认