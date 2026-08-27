# pgwrecover 多版本 WAL 重放架构

## 策略选择

### 策略 A：每版本独立 vendored redo 栈（已采用）
- 每个 PG 版本独立目录（`versions/pg16/`、`versions/pg18/`）
- 编译为独立 `.so`（符号空间完全隔离）
- 引擎核心通过 dlopen + 中性 ABI 调用
- **优点**：版本间零干扰，WAL magic 版本差异自然隔离
- **缺点**：头文件重复（可通过裁剪减少 90%）

### 策略 B：pg_common/ 共享内核（未采用）
- 版本无关代码下沉到共享目录
- 每版本只留差异 redo
- **优点**：代码复用高
- **缺点**：`#ifdef PG_VERSION` 泛滥，构建复杂度高

## 最小 L2 方法论

### 目的
拿到最小实现后，只需 diff 这些文件即可识别跨版本可变面，无需看整棵 PG 源码树。

### 步骤
1. 选择主 rmgr（如 heap/btree/gin）
2. 剔除次要 rmgr（seq/hash/spgist/brin/gist）
3. 保留 redo 逻辑 + 基础设施（WAL 解码、页原语、buffer 层、压缩）
4. 编译验证
5. 用 `gcc -M` 计算头文件传递闭包，裁剪到编译所需

### 可变面识别
最小 L2 中真正跨版本变化的文件：
- `fe_bufpage.c`（PageData 定义）
- `pg_redo_dispatch.c`（PgRedoSet 结构）
- 各 `*_redo` 函数体
- `xlogreader.c`（WAL magic）

## 构建模式

```
per-version .so + single engine binary
--version=16  →  dlopen(libpgwrecover_16.so)  →  pg_replay_run()
--version=18  →  dlopen(libpgwrecover_18.so)  →  pg_replay_run()
```

L3 ABI（l3.h）：
- `L3ReplayTarget`：中性 WAL 目标描述
- `L3ReplayResult`：中性重放结果
- `PgwRecoverVtbl`：版本函数表

## 公共代码抽取（T3982）

### 目标
从 pg16/pg18 版本目录中抽取共享模块到 `src/pg/common/`，消除版本间代码重复。

### 公共模块（7 个 .c 文件）
| 文件 | 功能 | 抽取依据 |
|------|------|----------|
| `fe_buffer.c` | BufferPool 实现 | 完全相同 |
| `fe_nbt_aux.c` | NBTree 辅助 | 完全相同 |
| `fe_gin_aux.c` | GIN 辅助 | 完全相同 |
| `pg_redo_btree.c` | BTree redo | 完全相同 |
| `pg_lzcompress.c` | LZ 压缩 | PG18 新增安全检查，向上兼容 |
| `xlogreader.c` | WAL 读取 | 差异在 `#ifndef FRONTEND` 守护内 |
| `snprintf.c` | 格式化输出 | PG18 改进 Windows 支持 |

### 版本差异文件
- **pg16**（4 个）：`fe_bufpage.c`、`fe_heap_aux.c`、`fe_memutils.c`、`pg_redo_heap_official.c`
- **pg18**（9 个）：上述 4 个 + `fe_brin_aux.c`、`fe_gist_aux.c`、`fe_hash_aux.c`、`fe_spgist_aux.c`、`pg_redo_seq_official.c`

### include 路径统一
- `fe_bufpage.h` 作为 shim，统一 PG16/PG18 的 include 路径
- PG16：`fe_bufpage.h` → `storage/bufpage.h`（PG16 原生）
- PG18：`fe_bufpage.h` → `storage/bufpage.h`（PG18 原生）
- `PageData` 类型在 `fe_bufpage.h` 中为 PG16 提供 typedef

### 构建脚本
- 先编译 `src/pg/common/*.c` 为 `.o`（用版本特定 -I 路径）
- 再编译版本目录差异 `.c`
- 链接成版本 `.so`

### 效果
- 消除 ~3,500 行版本重复代码
- pg16：11 → 4 个 .c
- pg18：16 → 9 个 .c
- 总计：22,000 → 18,468 行
