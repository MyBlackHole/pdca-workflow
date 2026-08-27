---
schema: pdca.asset/v1
id: T3982-0826-pgwrecover-common-code-extraction
phase: check
source_ids: [evidence-common-build, evidence-pg16-replay-ok, evidence-regression-10pass]
---

## 上下文
T3971 交付了每版本独立 vendored redo 栈，pg16/pg18 各有 11/16 个 .c 文件。分析发现 7 个文件在两版本间完全相同或仅有 include 路径差异，存在 ~7,000 行重复代码。本任务抽取公共模块到 `src/pg/common/`，版本目录仅保留真正不同的文件。

## 假设与结果
| 假设 | 结果 |
|------|------|
| 公共代码可从版本目录分离 | ✅ 7 个文件成功提取到 common/ |
| PG18 版本可直接作为公共版本（pg_lzcompress/xlogreader/snprintf） | ✅ 向上兼容，无功能回退 |
| fe_bufpage.h 可统一 include 路径 | ✅ pg16 通过 fe_bufpage.h 转发到 storage/bufpage.h |
| 版本差异文件保持分离可行 | ✅ pg16 4 个 / pg18 9 个，编译通过 |
| 不影响现有测试 | ✅ 10 passed，0 warnings |

## 分析

- **AC-1** ✅ `src/pg/common/` 包含 7 个公共 .c 文件，编译通过（evidence-common-build）
- **AC-2** ✅ pg16 版本目录仅保留 fe_bufpage/fe_heap_aux/fe_memutils/pg_redo_heap_official（4 个 .c）（evidence-pg16-dir）
- **AC-3** ✅ pg18 版本目录保留上述 4 个 + 5 个独有（brin/gist/hash/spgist/seq）（evidence-pg18-dir）
- **AC-4** ✅ pg16 minimal replay heap/gin 逐字节一致（evidence-pg16-replay-ok）
- **AC-5** ✅ pg18 regression 10 passed 不变，0 warnings（evidence-regression-10pass）
- **AC-6** ✅ 构建脚本支持 common/ 编译 + 版本 .so 链接（evidence-common-build）

### 消除重复
- 从两份共 ~22,000 行 → common 7,961 + pg16 3,142 + pg18 7,365 = 18,468 行
- 消除 ~3,500 行版本重复代码

### 额外修复
- `fe_bufpage.h` 移除 `PageGetTempPageCopySpecial` 重复声明（与 `storage/bufpage.h` 冲突）
- pg16 `fe_bufpage.c` 添加 `#include "fe_bufpage.h"` 获取 `PageData` 类型定义
- `xlogreader.c` 添加 `#include <inttypes.h>` 支持 `PRIu64` 格式符

## 适用边界
- pg18 的安全检查（pg_lzcompress 边界检查）向上兼容，不影响 pg16
- xlogreader.c 的 I/O 统计代码由 `#ifndef FRONTEND` 守护，前端编译不包含
- 版本差异文件（fe_bufpage/fe_heap_aux/fe_memutils/pg_redo_heap_official）因架构性差异保持分离

## 下一轮建议
1. 新增 PG 版本时，先检查 common/ 7 个文件是否可直接复用，再决定版本差异文件
2. 可考虑将 common/ 编译为静态库（.a），避免每次重新编译
3. fe_bufpage.c 的 pg16/pg18 差异可进一步拆分（公共函数 vs 版本特定函数）
