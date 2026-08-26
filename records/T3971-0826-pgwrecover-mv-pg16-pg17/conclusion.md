---
schema: pdca.asset/v1
id: T3971-0826-pgwrecover-mv-pg16-pg17
phase: check
source_ids: [evidence-build-pg16-so, evidence-pg16-heap-ok, evidence-pg16-gin-ok, evidence-regression-10pass, evidence-pruned-headers]
---

## 上下文
T3971 原 PRD 采用策略 B（抽取 pg_common/ 共享内核），Do 阶段用户确认 pivot 到**策略 A（每版本独立 vendored redo 栈）**：L1 引擎核心版本无关、L2 redo 实现每版本独立 .so（符号空间隔离）、L3 中性 ABI（l3.h：PgwRecoverVtbl）隔离版本差异。pg_common/ 已清空，12 个 fe_*.c 移入 src/pg/versions/pg18/。

额外交付：最小 L2（Slice3）— pg16 仅保留 heap/btree/gin 所需 redo + 基础设施（11 个 .c），暴露可变面；版本目录头文件从 845 裁剪到 84（90% 删除）。

## 假设与结果
| 假设 | 结果 |
|------|------|
| 每版本独立 .so + dlopen 可行 | ✅ 符号空间完全隔离，pg16/pg18 .so 独立编译链接 |
| L3 中性 ABI 可隔离版本差异 | ✅ l3.h 定义 L3ReplayTarget/L3ReplayResult/PgwRecoverVtbl，引擎仅持 l3.h |
| PG16 WAL 格式（magic D113）可正确解析 | ✅ pg16 重放 heap/gin 逐字节一致 |
| 最小 L2 可暴露可变面 | ✅ 保留 11 个 .c，可变面集中在 fe_bufpage.c/PgRedoSet/redo 函数体 |
| PG18 回归不受影响 | ✅ 10 passed（9 PG18 + 1 PG16），0 warnings |

## 分析

### 策略变更说明
PRD 原定策略 B（pg_common/），Do 阶段用户确认 pivot 到策略 A（每版本独立）。以下 AC 按**实际策略 A** 判定。

- **AC-1** ✅ PG18 构建通过且回归 10 passed（9 PG18 + 1 PG16），0 警告（evidence-regression-10pass）
- **AC-2** ✅ PG16 vendored 到 src/pg/versions/pg16/（11 个 .c，头文件裁剪到 84），编译通过（evidence-build-pg16-so）
- **AC-3** ✅ 构建支持 --version=16/18 按版本选择，per-version .so + 单二进制（evidence-build-pg16-so）
- **AC-4** ✅ PG16 heap 逐字节一致（evidence-pg16-heap-ok），gin 逐字节一致（evidence-pg16-gin-ok）
- **AC-5** ✅ PG18 回归 10 passed 不变，构建 0 警告（evidence-regression-10pass）
- **AC-6** ✅ 分发缝 pg_redo_set_for_version() 注册 PG16（control_version=1300），新增版本仅需在 pg_redo_dispatch.c 加集合 + versions/ 加目录 + build 脚本加一行（evidence-build-pg16-so）

### 额外交付（超出 PRD）
- Slice3 最小 L2：pg16 剔除 5 个额外 rmgr（seq/hash/spgist/brin/gist），保留 heap/btree/gin
- 头文件裁剪：pg16 845→84（90%），pg18 138→92（33%），基于 gcc -M 传递闭包
- PGW_MINIMAL 编译宏：最小模式下 pg_redo_dispatch.c 仅注册 3 个 rmgr

## 适用边界
- 策略 A 适合 PG 版本间 redo 逻辑差异大的场景（符号隔离，不需共享代码）
- 头文件裁剪基于 gcc -M 闭包，新增 .c 需重新计算
- PG17 待后续任务，沿用同一模式

## 下一轮建议
1. 接入 PG17（新建任务，复制 pg16/pg18 模式）
2. 考虑将版本目录的头文件裁剪脚本化（自动计算闭包）
3. 可变面定点 diff：用外部 PG 源码仓库对比 versions/pg16 与 versions/pg18 的 .c 文件差异
