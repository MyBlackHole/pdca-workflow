# pgwrecover btree P1（VACUUM/MARK_HALFDEAD/UNLINK_PAGE）

> parent: T0338
> 场景：development

## 范围

在 T0338 基础上，实现 btree WAL P1 类型：

| WAL 类型 | 操作 | 难度 |
|----------|------|------|
| VACUUM (0xC0) | 同 DELETE（无冲突处理） | 中 |
| MARK_PAGE_HALFDEAD (0xB0) | 父页删除下链接 + 叶页重建为 half-dead | 高 |
| UNLINK_PAGE (0x80) | 页面从 btree 链摘除（5 块） | 高 |
| UNLINK_PAGE_META (0x90) | 同 UNLINK_PAGE + 元页更新 | 高 |

## 验收

- AC-1: VACUUM 重放单元测试
- AC-2: MARK_PAGE_HALFDEAD 重放单元测试
- AC-3: UNLINK_PAGE/UNLINK_PAGE_META 重放单元测试
- AC-4: 回归不破坏既有单测
