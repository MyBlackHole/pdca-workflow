# pgwrecover 多版本 PG 兼容性测试(PG16/17)

## 背景
pgwrecover 当前仅针对 PG18 开发和验证。需确认对 PG16/PG17 的
兼容性状况并补齐差异。

## 验收标准
- AC-1: PG16 实例生成 WAL 样本 → pgwrecover 重放 → 语义级一致
- AC-2: PG17 实例生成 WAL 样本 → pgwrecover 重放 → 语义级一致
- AC-3: 差异点已文档化(结构体变化/新增操作码/偏移变化)
- AC-4: 不兼容项有明确的错误提示而非静默错误

## 已知版本差异预分析
| 组件 | PG16 | PG17 | PG18 | 影响 |
|------|------|------|------|------|
| pg_control_version | 1300 | 1300 | 1800 | 需确认 |
| XLogRecord 头 | 同 | 同 | 同 | 低 |
| heap INSERT/DELETE | 同 | 同 + PRUNE_ON_ACCESS | + FREEZE_PLAN | 中 |
| btree WAL | 同 | 同 | 同 | 低 |
| xl_heap_prune | 无 flags 字段 | 新增 XLHP_* flags | 扩展 | 高 |
