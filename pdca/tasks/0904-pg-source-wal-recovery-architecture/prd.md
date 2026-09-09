# PRD：嵌入数据库源码实现崩溃恢复与 Parquet 转换

## 背景

用户希望像 XtraBackup 一样，嵌入到 PostgreSQL 和 MySQL 源码内，调用数据库自身的崩溃恢复函数，恢复后直接读取数据文件转换成 Parquet。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     统一引擎（版本无关）                          │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ PG 恢复引擎      │    │ MySQL 恢复引擎   │                    │
│  │ (嵌入 PG 源码)   │    │ (嵌入 InnoDB 源码)│                   │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                             │
│           ▼                       ▼                             │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ 数据读取         │    │ 数据读取         │                    │
│  │ (heap_getnext)   │    │ (.ibd 直读)     │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                             │
│           ▼                       ▼                             │
│  ┌─────────────────────────────────────────┐                   │
│  │         Parquet 写入 (Arrow/Parquet)     │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### PostgreSQL 嵌入方案

#### 调用链

```
pg_recovery_init(datadir)
    │
    ├── 读取 pg_control → 获取 checkpoint LSN
    │
    ├── StartupXLOG() 或精简版
    │     ├── 初始化 xlogreader
    │     ├── 初始化 buffer manager (fe_buffer.c)
    │     └── 执行 WAL redo (heap_redo/btree_redo/...)
    │
    └── 恢复完成，数据文件一致

pg_heap_read(heap_path, callback)
    │
    ├── 打开 heap 文件
    ├── 遍历 page → line pointer → tuple
    ├── MVCC 可见性判断
    └── 回调输出行数据

pg_to_parquet(heap_path, parquet_path, schema)
    │
    ├── pg_heap_read 读取行数据
    ├── 类型转换 (PG type → Arrow type)
    └── Arrow/Parquet 写入
```

#### 需要 stub 的依赖

| 子系统 | stub 方式 | 工作量 |
|--------|----------|--------|
| 共享内存 | no-op | 1 人天 |
| Lock Manager | no-op | 1 人天 |
| SLRU (CLOG/Subtrans) | 只读模式 | 3 人天 |
| RelCache | 绕过（直接文件 IO） | 2 人天 |
| WAL Insert | no-op（不写 WAL） | 1 人天 |
| Checkpointer | no-op | 1 人天 |
| Proc Array | no-op | 1 人天 |
| GUC 系统 | 最小化 | 2 人天 |

#### 需要实现的功能

| 功能 | 说明 | 工作量 |
|------|------|--------|
| StartupXLOG 精简版 | 仅初始化恢复所需子系统 | 10-15 人天 |
| table_open 前端化 | 绕过 RelCache，直接打开文件 | 3-5 人天 |
| heap_getnext 前端化 | 遍历 tuple | 5-8 人天 |
| MVCC 可见性判断 | xmin/xmax + CLOG | 3-5 人天 |
| TOAST 解压 | 已有 pg_lzcompress | 2-3 人天 |

### MySQL 嵌入方案（类似 XtraBackup）

#### 调用链

```
innodb_recovery_init(datadir)
    │
    ├── buf_pool_init()        ← 页缓冲池
    ├── log_sys_init()         ← redo log 系统
    ├── trx_sys_init()         ← 事务系统
    └── fsp_init()             ← 表空间管理

innodb_recovery_redo_apply()
    │
    ├── recv_recovery_from_checkpoint_start()
    │     ├── 读取 checkpoint LSN
    │     ├── log_recv_parse()      ← 解析 redo log
    │     └── recv_apply_log_rec()  ← MLOG_* 按页 LSN 幂等应用
    │
    └── Redo 前滚完成，数据文件一致

innodb_recovery_undo_rollback()
    │
    ├── trx_rollback_or_clean()
    │     ├── 从 trx_sys 取活跃事务列表
    │     ├── 遍历 undo log 链
    │     ├── INSERT 回滚 = 移除行
    │     └── UPDATE/DELETE 回滚 = 恢复旧版本
    │
    └── Undo 回滚完成，无未提交事务

innodb_to_parquet(ibd_path, parquet_path, schema)
    │
    ├── mmap(.ibd)
    ├── 页遍历 → 记录解码
    ├── 类型转换 (InnoDB type → Arrow type)
    └── Arrow/Parquet 写入
```

#### 需要嵌入的 InnoDB 模块

| 模块 | 文件 | 功能 |
|------|------|------|
| **Redo Log** | log0recv.cc, log0log.cc | redo 解析与前滚 |
| **Transaction** | trx0roll.cc, trx0undo.cc, trx0sys.cc | undo 回滚 |
| **Buffer Pool** | buf0buf.cc | 页缓冲管理 |
| **File Space** | fil0fil.cc, fsp0fsp.cc | 表空间管理 |
| **Data Dictionary** | dict0dict.cc, dict0boot.cc | 数据字典 |
| **Page** | page0cur.cc, page0page.cc | 页管理 |
| **Record** | rem0rec.cc | 记录格式解析 |

---

## 实施计划

### Phase 1：MySQL 嵌入（2-3 周）

**目标**：像 XtraBackup 一样嵌入 InnoDB 源码

1. 获取 MySQL 8.0/8.4 源码
2. 集成 InnoDB 核心模块（~50 个 .cc 文件）
3. 实现简化版 innodb_init（仅恢复所需）
4. 封装 recv_recovery_from_checkpoint_start
5. 封装 trx_rollback_or_clean
6. 与现有 mysqlbin 集成

**产出**：MySQL 崩溃恢复 .so + Parquet 转换

### Phase 2：PostgreSQL 嵌入（4-6 周）

**目标**：嵌入 PG 源码实现崩溃恢复

1. 获取 PG 16/17/18 源码
2. 实现 StartupXLOG 精简版
3. 实现 table_open/heap_getnext 前端化
4. 实现 MVCC 可见性判断
5. 与 Parquet 写入集成

**产出**：PostgreSQL 崩溃恢复 .so + Parquet 转换

### Phase 3：统一引擎（2-3 周）

**目标**：建立统一的引擎框架

1. 设计统一 API 接口
2. 实现 dlopen 动态加载
3. 版本检测和自动分发
4. 统一 Parquet 写入

**产出**：统一引擎支持 PG + MySQL

---

## 工作量估算

| 阶段 | 工作量 | 风险 |
|------|--------|------|
| Phase 1 (MySQL) | 2-3 周 | 中（XtraBackup 已证明可行） |
| Phase 2 (PG) | 4-6 周 | 高（StartupXLOG 依赖复杂） |
| Phase 3 (统一) | 2-3 周 | 低 |
| **总计** | **8-12 周** | |

---

## 验收标准

### Phase 1

- [ ] InnoDB 崩溃恢复可用（redo 前滚 + undo 回滚）
- [ ] 恢复后 .ibd 文件一致
- [ ] Parquet 转换正确

### Phase 2

- [ ] PG 崩溃恢复可用（WAL redo）
- [ ] 恢复后 heap 文件一致
- [ ] 数据读取正确
- [ ] Parquet 转换正确

### Phase 3

- [ ] 统一引擎框架可用
- [ ] 支持多版本 PG/MySQL
- [ ] 版本自动检测
