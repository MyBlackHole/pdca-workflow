# 旧架构引用再次扫描证据

- 扫描日期：2026-08-31
- 扫描范围：全仓库（排除 .git/、records/、journal/、tasks/archive/）
- 扫描方法：grep 搜索已退役术语 + 目录存在性检查 + 人工复核
- 对比基准：T0447-0831-old-arch-refs-audit 结论

## 扫描命令

```bash
grep -rn "docs/adr/" --include="*.md" --include="*.py" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.jsonl" --exclude-dir=.git --exclude-dir=records --exclude-dir=journal --exclude-dir=archive
grep -rn "已退役\|退役\|历史决策" --include="*.md" --include="*.py" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.jsonl" --exclude-dir=.git --exclude-dir=records --exclude-dir=journal --exclude-dir=archive
grep -rn "deprecated\|legacy\|旧架构\|旧模式" --include="*.md" --include="*.py" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.jsonl" --exclude-dir=.git --exclude-dir=records --exclude-dir=journal --exclude-dir=archive
find -type d \( -name "agent_tree_legacy" -o -name "agent_plain_control" -o -name "agent_session_pool" \)
grep -rn "post_wait_priority\|post_priority_kind\|post_wait_priority_timestamped\|post_wait_priority_observed" --include="*.hpp" --include="*.cpp" --include="*.h" --exclude-dir=.git
```

## 对比 T0447 结果

### 类别 1：已删除的 docs/adr/ 目录残留引用

| 来源 | 行 | 引用内容 | 状态 |
|------|-----|---------|------|
| `ontology/domain/linux-epoll-eventloop-rpc-conn-idle-reclaim.md:27` | 27 | "相关决策已随 docs/adr/ 退役删除" | **有意保留** |
| `pdca/tasks/0817-rpc-handshake-negotiation/implement.jsonl:3` | 3 | `docs/adr/ADR-0001-openssl4-单库替代gmssl双后端.md` | **残留引用** |
| `pdca/tasks/0820-tls-session-integration-test/prd.md:75` | 75 | "架构决策见 docs/adr/" | **残留引用** |
| `pdca/tasks/0821-tls-keygen-cleanup/prd.md:93` | 93 | "架构决策见 docs/adr/" | **残留引用** |
| `pdca/tasks/0823-async-object-lifecycle/implement.jsonl:4-5` | 4-5 | `docs/adr/ADR-0026-v81-plain-control-async.md`, `docs/adr/ADR-0029-async-object-lifecycle-contract.md` | **残留引用** |
| `pdca/tasks/0823-handshake-cross-module-review/prd.md:53` | 53 | "架构决策见 docs/adr/" | **残留引用** |
| `pdca/tasks/active/0808-backup-server-architecture/prd.md:96` | 96 | "架构决策见 docs/adr/" | **残留引用** |

**与 T0447 对比**：无新增，无清理。7 处引用保持不变。

### 类别 2：旧 post API 变体

- T0385 仍在 `phase: plan`，未开始执行
- `pdca/tasks/0823-async-object-lifecycle/`：PRD 仍描述旧 post 变体（6+ 个变体）
- `ontology/domain/linux-epoll-eventloop-transport-ownership-model.md`：仍引用 `reactor_post_wait_priority`
- 源码中未找到旧 post 变体符号（源码不在本仓库中）

**与 T0447 对比**：无变化。T0385 仍为 plan 阶段。

### 类别 3：死代码文件

- `agent_tree_legacy/`、`agent_plain_control/`、`agent_session_pool`：未在仓库中找到

**与 T0447 对比**：无变化。可能存在于外部项目中。

### 类别 4：旧任务格式遗留

- 14 个活跃任务（含 T0165、T0216、T0221 等旧格式 ID）

**与 T0447 对比**：无变化。旧任务格式清理需授权。

### 类别 5：CONTEXT.md 已退役概念

- ADR 机制、声明的测试接缝、守卫原语、强销毁保证

**与 T0447 对比**：无变化。有意保留。

### 类别 6：知识库旧架构引用

- `ontology/concept/ontology-asset.md`：ADR 机制已退役注记
- `ontology/concept/pdca-architecture.md`：原 ADR 机制已退役注记
- `ontology/concept/pdca-provable-skill-increments.md`：legacy_no_gate 分类引用
- `ontology/domain/backup-crypto-openssh-gm-support.md`：已废弃的 `EVP_PKEY_get1_EC_KEY`
- `ontology/domain/benchmark-small-pack-streaming-decode.md`：兼容包装引用

**与 T0447 对比**：无新增。有意保留的历史注记。

### 类别 7：superseded 证据文件

- manifest.jsonl 中的 `superseded_by` 引用

**与 T0447 对比**：无变化。有意保留。

## 新增发现

无新增旧架构引用类别。

## 已清理项

无（与 T0447 结果一致，无任何残留引用被清理）。

## 结论

项目仍然存在与 T0447 相同的旧架构引用残留。未进行任何清理。主要残留为：
1. 7 处 docs/adr/ 引用（6 处需清理 + 1 处有意保留）
2. T0385 旧 post API 退役任务尚未开始执行
3. 死代码文件可能存在于外部项目中
4. 旧任务格式遗留需授权清理
5. CONTEXT.md 和 ontology 中的已退役概念有意保留