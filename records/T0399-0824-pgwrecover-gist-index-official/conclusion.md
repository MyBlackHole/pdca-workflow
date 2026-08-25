---
schema: pdca.asset/v1
id: T0399-0824-pgwrecover-gist-index-official
phase: check
source_ids: [T0399-commit-6ae642d]
---

## 分析
- **AC-1** ✅ gistxlog.c 全 redo 例程逐行拷贝, 编译通过（commit 6ae642d）
- **AC-2** ✅ 真实样本(box 列 1500 行)端到端: heap+index 语义级一致 PASS,
  applied=2643(PAGE_UPDATE×5626+SPLIT×30)
- **AC-3** ✅ RM_GIST_ID 接线; 回归 7 passed

前次 FAIL 根因 = 样本时间窗口错位(非 redo bug)。
重做样本(一气呵成 stop→cp→不再启停)后验证 PASS。

## 适用边界
GiST 数据页恢复; 全部操作码(PAGE_UPDATE/PAGE_SPLIT/DELETE/
PAGE_REUSE/PAGE_DELETE/ASSIGN_LSN)。
