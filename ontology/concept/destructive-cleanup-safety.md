---
schema: pdca.asset/v1
id: ontology:concept/destructive-cleanup-safety
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/destructive-cleanup-safety/1.0.0
summary: 可恢复破坏性清理的恢复源固定与执行前重验证规则
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-task
---

# 破坏性清理安全规则（destructive-cleanup-safety）

可恢复清理必须同时满足：

1. dry-run 生成精确目标清单，并把恢复源固定为删除前的不可变 commit；恢复命令不得引用会漂移的 `HEAD`。
2. apply 不得只信任旧 manifest；执行前必须重新验证每个目标仍处于允许删除的状态。任一目标漂移、越界或不可恢复时，整批失败关闭。

具体目标和一次性校验结果保留在任务 record，不复制到长期知识。

## 来源

- `（原知识层）destructive-cleanup-safety.md`
- 关联记录：`R0142-clean-invalid-active-history`
