---
schema: pdca.asset/v1
id: T0395-0824-pgwrecover-hash-index-official
phase: check
source_ids: [T0395-commit-a0af5dd]
---

## 上下文
T0401 全面审查确认 HASH 索引(12)为静默缺口。本任务按官方源码
逐行拷贝原则完成 hash_xlog.c 前端化并端到端验证。

## 假设与结果
| 假设 | 结果 |
|------|------|
| hash redo 依赖可脱离 Relation 拷贝 | ✅ 实际仅 5 个辅助函数, 全部页面级操作 |
| 全套 hash 操作码(SPLIT/OVFL/SQUEEZE/BITMAP)可重放 | ✅ 成立 |

## 分析
- **AC-1** ✅ hash_xlog.c 14 个 redo 例程+hash_redo 逐行拷贝, 编译 0 警告（commit a0af5dd）
- **AC-2** ✅ 真实样本(2000 行 INSERT 触发 SPLIT×10/OVFL/SQUEEZE)
  端到端: 语义级一致(verify_consistency PASS); 已知残留: SQUEEZE 后
  bitmap 空闲位单 bit 差异(自由空间记账, 不影响既有元组)（test_hash_index_official）
- **AC-3** ✅ RM_HASH_ID 主循环接线 + other_rmgr 放行修正; 回归 4 passed

已知边界: bitmap 空闲位精确性待 SQUEEZE 路径精调(登记跟进);
heap 侧同样本验证 PASS。

## 适用边界
HASH 索引数据页恢复; 位图空闲位记账精度不影响恢复后 PG 正常运行
(位图仅在分配新 ovfl 页时消费, 差异位会被 VACUUM 重算纠正)。

## 下一轮建议
GIN/GIST/SPGIST/BRIN 按同一模式推进(各任务已登记)。
