# PRD — pgwrecover 公共代码抽取

> 状态：P3 完整规格
> 关联：T3971（多版本重放架构）

## 问题陈述
T3971 交付了每版本独立 vendored redo 栈（策略 A），pg16/pg18 各有 11 个 .c 文件。分析发现 7 个文件在两版本间完全相同或仅有 include 路径差异，存在 ~7,000 行重复代码。需抽取公共模块到 `src/pg/common/`，版本目录仅保留真正不同的文件。

## 决策
- **分离而非 #ifdef**：公共部分提取到 common/，版本差异留在各自目录，不引入版本宏
- **合并增量差异**：pg_lzcompress/xlogreader/snprintf 取两版本并集，PG18 的安全检查向上兼容
- **保持分离**：fe_bufpage/fe_heap_aux/fe_memutils/pg_redo_heap_official 因架构性差异保持版本独立

## 验收标准
- [ ] AC-1: `src/pg/common/` 包含 7 个公共 .c 文件，编译通过（0 警告）
- [ ] AC-2: pg16 版本目录仅保留 fe_bufpage/fe_heap_aux/fe_memutils/pg_redo_heap_official + 版本头
- [ ] AC-3: pg18 版本目录仅保留上述 4 个 + 5 个独有（brin/gist/hash/spgist/seq）+ 版本头
- [ ] AC-4: pg16 minimal replay heap/gin 逐字节一致
- [ ] AC-5: pg18 regression 10 passed 不变，0 warnings
- [ ] AC-6: 构建脚本支持 common/ 编译 + 版本 .so 链接

## 实现步骤
1. 创建 `src/pg/common/` 目录
2. 提取 fe_buffer.c（完全相同，直接移动）
3. 合并 fe_nbt_aux.c / fe_gin_aux.c / pg_redo_btree.c（提取公共部分，版本目录保留 include 差异）
4. 合并 pg_lzcompress.c（取并集，PG18 安全检查向上兼容）
5. 合并 xlogreader.c（PG18 I/O 统计用已有 FRONTEND 宏处理）
6. 合并 snprintf.c（平台差异用已有的 WIN32 宏处理）
7. 更新构建脚本：common/ 编译 + 版本 .so 链接
8. 验证：pg16 replay + pg18 regression + 0 warnings

## 范围外
- pg_redo_heap_official.c / fe_bufpage.c / fe_heap_aux.c / fe_memutils.c 的统一（架构性差异太大）
- pg18 独有文件（brin/gist/hash/spgist/seq）的处理
- 头文件公共化（版本头差异较大，暂不动）
