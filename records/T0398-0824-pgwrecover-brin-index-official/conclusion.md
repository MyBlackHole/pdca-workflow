---
schema: pdca.asset/v1
id: T0398-0824-pgwrecover-brin-index-official
phase: check
source_ids: [T0398-commit-90b5a30]
---

## 分析
- **AC-1** ✅ brin_xlog.c 全 redo 例程逐行拷贝（commit 90b5a30）
- **AC-2** ✅ 真实样本(5000 行 INSERT+DELETE)双文件语义级一致 PASS
- **AC-3** ✅ RM_BRIN_ID 接线, 回归 6 passed

## 适用边界
BRIN 数据页恢复(revmap+regular 页); brinSetHeapBlockItemptr 为
前端等价实现(官方 revmap.c 的槽位定位逻辑简化版)。
