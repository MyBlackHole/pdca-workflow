---
schema: pdca.asset/v1
id: knowledge:pdca-flow.destructive-cleanup-safety
layer: knowledge
summary: 可恢复破坏性清理的恢复源固定与执行前重验证规则
tags: [pdca-flow, cleanup, safety, recovery]
scenarios: [software-development]
phases: [do, check, act]
applies_when: [依据 dry-run manifest 执行文件或目录删除]
excludes_when: [无删除动作或目标无法恢复]
source_ids: [R0142-clean-invalid-active-history]
confidence: high
status: active
---
# 破坏性清理安全规则

可恢复清理必须同时满足：

1. dry-run 生成精确目标清单，并把恢复源固定为删除前的不可变 commit；恢复命令不得引用会漂移的 `HEAD`。
2. apply 不得只信任旧 manifest；执行前必须重新验证每个目标仍处于允许删除的状态。任一目标漂移、越界或不可恢复时，整批失败关闭。

具体目标和一次性校验结果保留在任务 record，不复制到长期知识。
