# PRD — pgwrecover PG17 版本支持

## 问题陈述
pgwrecover 已支持 PG16 和 PG18 多版本 WAL 重放（T3971+T3982）。现需添加 PG17 支持，沿用同样的 vendored redo 栈模式。PG17 位于 PG16 和 PG18 之间，其 WAL 格式和 pg_control 结构与 PG16 相同，但部分源码可能与 PG18 有共同差异。

## 实现决策
1. **获取 PG17 源码**：从 PostgreSQL 官方仓库获取 REL_17_STABLE 分支源码
2. **差异分析**：对比 PG17 与 PG16/PG18 的关键文件，识别版本差异
3. **版本目录**：创建 `src/pg/versions/pg17/`，仅包含差异文件
4. **注册分发**：在 `pg_redo_dispatch.c` 中注册 PG17（control_version=1700）
5. **构建支持**：更新 `build_pgwrecover.sh` 支持 PG17 编译

## 验收标准
- [ ] AC-1: PG17 版本目录创建完成，包含差异文件（编译通过）
- [ ] AC-2: 构建脚本支持 PG17（`--version=17` 参数）
- [ ] AC-3: PG17 WAL magic（0xD116）正确识别
- [ ] AC-4: PG17 heap replay 逐字节一致
- [ ] AC-5: PG16/PG18 回归测试不变（10 passed + 0 warnings）
- [ ] AC-6: 分发缝注册 PG17（control_version=1700 → pg_redo_set_pg17）

## 范围外
- PG17 特有新功能（如 WAL summarization）的完整支持
- PG17 regression 测试套件（仅验证核心 redo 正确性）

## 备注
- PG17 pg_control 结构与 PG16 相同（无新字段）
- PG17 WAL magic = 0xD116
- PG17 control_version = 1700
