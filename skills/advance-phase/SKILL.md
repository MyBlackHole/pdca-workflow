---
name: advance-phase
description: 通过严格 schema、语义门禁和原子 receipt 将任务推进到相邻 PDCA 阶段。
---

# Advance Phase

## 输入

- 当前任务目录。
- 相邻目标阶段：`do | check | act | archive`。

## 执行

```bash
python3 "$PDCA_HOME/scripts/transition-phase.py" <task-dir> --to <phase>
```

命令统一完成：严格 schema → 当前阶段语义门禁 → `task.json.bak` → 原子更新 → transition receipt。禁止绕过命令直接改 `meta.phase`。

## 门禁

| 转换 | 必需语义 |
|------|----------|
| plan → do | `final_confirmation.response=confirmed` |
| do → check | PRD；有效 evidence schema、文件、size、digest |
| check → act | conclusion、verdict、`check_confirmation` |
| act → archive | disposition；phase/status/active/states 终态一致 |

解析错误、未知状态、非相邻转换、空字段或跨文件不一致均 fail-closed。相同目标重复调用返回 unchanged；receipt 与当前状态冲突则停止并报告。

## 回滚

仅恢复命令生成且 phase 相邻的 `task.json.bak`：

```bash
bash "$PDCA_HOME/scripts/rollback-phase.sh" <task-dir>
```

回滚不删除 evidence、conclusion 或 journal；这些事实保留供重新 Check。

## 完成

- `task.json` 满足严格 schema。
- `states.<target>`、status、active 与目标 phase 一致。
- `transition-receipts/<from>-to-<target>.json` 存在。

## 已知坑

- check_confirmation 必须带 `response` 字段，缺 response 会被 transition 拒绝（T0265 教训）。
- PRD `## 验收标准` 必须是 `- [ ] AC-x: ...` checkbox 格式；`### AC-x` 标题式会被拒。
- development/bugfix 场景 PRD 必须含 `### 声明的测试接缝` 子节，缺失即拒绝。
