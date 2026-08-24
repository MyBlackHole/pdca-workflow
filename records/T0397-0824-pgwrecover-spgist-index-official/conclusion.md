---
schema: pdca.asset/v1
id: T0397-0824-pgwrecover-spgist-index-official
phase: check
source_ids: [T0397-commit-43a50e7]
---

## 分析
- **AC-1** ✅ spgxlog.c 全 redo 逐行拷贝（commit 43a50e7）
- **AC-2** ✅ box 列 1500 行样本, heap 与索引语义级一致 PASS
  (verify_consistency.py, 双文件结构性差异=0)
- **AC-3** ✅ RM_SPGIST_ID 接线

## 适用边界
SP-GiST 数据页恢复; 裁剪版 SpGistState(redo 三字段)。
