# T3982 Act — 知识处置

## 任务结论
公共代码抽取完成：7 个公共 .c 文件提取到 `src/pg/common/`，版本目录仅保留真正不同的文件。
消除 ~3,500 行版本重复代码。所有测试通过。

## 知识沉淀
1. **公共模块识别方法**：通过 diff 两版本源码，识别出完全相同或仅有 include 路径差异的文件
2. **include 路径统一**：`fe_bufpage.h` 作为 shim，统一 PG16/PG18 的 include 路径
3. **PG18 向上兼容**：PG18 的安全检查（如 pg_lzcompress 边界检查）不影响 PG16
4. **PGW_MINIMAL 宏守卫**：通过编译时宏控制功能集，避免运行时分支

## Disposition
- **projected**：此模式可复用于其他需要多版本支持的 PostgreSQL 扩展
- 知识沉淀到 `knowledge/pg/pgwrecover-multiversion-architecture.md`

## 后续建议
1. 新增 PG 版本时，先检查 common/ 是否可直接复用
2. 可考虑将 common/ 编译为静态库（.a）
3. fe_bufpage.c 的 pg16/pg18 差异可进一步拆分
