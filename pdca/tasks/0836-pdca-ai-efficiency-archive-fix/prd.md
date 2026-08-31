# 修复 archive 本体自检

## 目标

修复 `lifecycle-success` 和 `lifecycle-act-disposition` 的 archive 阶段失败问题。

## 问题分析

`ARCHIVE_ONTOLOGY_INVALID` 错误：`ontology-validate.py` 在 fixture root 的 `ontology/` 目录上失败，因为缺少 `manifest.jsonl` 等必要文件。

`ACT_TO_ARCHIVE_FAILED`：由 `ARCHIVE_ONTOLOGY_INVALID` 导致。

## 实施计划

### AC-1：修复 fixture root 的 ontology 目录
- 确保 fixture root 的 `ontology/` 目录包含 `manifest.jsonl`
- 或更新 `archive_ontology_ready_issues` 函数使其在缺少 `manifest.jsonl` 时不失败

### AC-2：lifecycle-success 返回 archived
- 修复 archive 转换

### AC-3：lifecycle-act-disposition 返回 DISPOSITION_MISSING
- 修复 disposition 验证

### AC-4：更新 skill-content-baseline.json
- 将 `flows/flow-do/SKILL.md` 条目更新为 `ontology/process/flow-do.md`

### AC-5：22/22 fixture 真正通过