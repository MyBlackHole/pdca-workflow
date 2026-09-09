# PRD: 数据库恢复与转换架构图绘制

## 背景

database_转换_parquet 项目已实现 MySQL 和 PostgreSQL 的崩溃恢复与 Parquet 转换功能。为了更好地理解系统架构和工作原理，需要绘制完整的架构图、原理图和流程图。

## 目标

1. 绘制系统架构图，展示各组件关系
2. 绘制 MySQL 崩溃恢复原理图
3. 绘制 PostgreSQL 崩溃恢复原理图
4. 绘制数据转换流程图
5. 绘制测试架构图

## 验收标准

- [ ] 系统架构图（Mermaid 格式）
- [ ] MySQL 崩溃恢复原理图
- [ ] PostgreSQL 崩溃恢复原理图
- [ ] 数据转换流程图
- [ ] 测试架构图
- [ ] 所有图示可被 Mermaid 渲染

## 技术方案

使用 Mermaid 语法绘制以下图示：

### 1. 系统架构图

展示项目的主要组件：
- 源代码层（MySQL/PG 源码嵌入）
- 恢复引擎层（redo/undo/WAL replay）
- 数据读取层（heap reader/ibd parser）
- 转换层（Parquet converter）
- 测试层（多版本测试套件）

### 2. MySQL 崩溃恢复原理图

展示 MySQL 崩溃恢复的过程：
- redo log 前滚（recv_recovery_from_checkpoint_start）
- undo log 回滚（trx_rollback_or_clean）
- 数据文件恢复

### 3. PostgreSQL 崩销恢复原理图

展示 PostgreSQL 崩溃恢复的过程：
- WAL replay（StartupXLOG）
- 数据页恢复
- 一致性检查

### 4. 数据转换流程图

展示从源数据到 Parquet 的转换流程：
- 数据读取
- Schema 映射
- 数据转换
- Parquet 写入

### 5. 测试架构图

展示测试套件的组织结构：
- 单元测试
- 集成测试
- 崩溃恢复测试
- 大数据量测试

## 参考资料

- 项目源代码：`src/mysql/`, `src/pg/`, `src/common/`
- 测试代码：`tests/pgwrecover/`
- 文档：`docs/USAGE.md`, `docs/API.md`
