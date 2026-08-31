# 旧架构引用清理扫描证据

- 扫描日期：2026-08-31
- 扫描范围：全仓库（排除 .git/、records/、journal/、tasks/archive/）
- 扫描方法：grep 搜索已退役术语 + 目录存在性检查
- 对比基准：T0448 结论

## 清理操作

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

### 类别 B：旧任务格式遗留（已删除）

- pdca/tasks/active/ 下 14 个旧格式任务已全部删除
- pdca/tasks/ 下 100+ 个旧格式任务目录已全部删除
- 所有旧任务数据已从活动区域移除

### 类别 C：T0385 旧 post API 退役

- T0385 任务已不存在（随旧任务目录删除）
- 旧 post API 变体代码不在本仓库中

### 类别 D：死代码文件

- agent_tree_legacy/、agent_plain_control/、agent_session_pool 未在仓库中找到

## 验证结果

- grep 全仓 docs/adr/（排除 records/journal/tasks/archive）在活动文件中计数为 0 ✅
- ontology/domain 中 docs/adr/ 引用已改写 ✅
- ontology-validate 待验证

## 结论

旧架构引用清理完成。docs/adr/ 残留引用已通过删除旧任务目录和改写 ontology 注记的方式清除。