# 跟进：PG 转换覆盖 4B 头 varlena 与 TOAST 外置路径（T0301 后续）

## 问题陈述

T0301/T0311 后仍存盲区：

1. **TOAST 外置值无对照**：pgbin 对 2KB+ payload（TOAST 外置）行按设计跳过，parquet
   中为空串，仅登记行数，TOAST 值正确性从未验证。T0311 实测 2564B payload 被 PG
   pglz 压缩存储（external+compressed）。
2. **4B 头 varlena 仅顺带**：T0311 的 480B（4B 头未压缩）形态已存在于 poc_consistency
   但未作为正式对照维度。
3. **NULL 行为仅单版本实测**：T0311 只在 PG18 实测 NULL bitmap；9.6/11 的 nullbit
   行为未回归。
4. **external 头跨版本差异未验证**：PG12 移除 toastidx 字段，9.6/11 external 头布局
   与 18 不同，未对照。
5. **pgbin 参数不一致**：`--rows` 用位置参数，与 T0301 产物约定不符。

## 目标

- 闭合 TOAST 外置值对照盲区（完整解码：toast 表读取 + chunk 拼接 + pglz 解压）。
- 三版本（9.6/11/18）含 NULL + TOAST 数据五维校验全 PASS。
- 校验脚本泛化为表无关，去硬编码与 TOAST 白名单。
- pgbin 参数统一为 `<heap> <clog_dir> <out> [--rows=] [--pg-version=]`。

## 方案

1. **灌数**：三容器各建 `poc_toast` 表（含 md5/chars 两列，rows=10000，chars 含
   4B 头 480B 与 TOAST 2564B 形态 + 稀疏 NULL），dump heap + pg_xact，导出 SQL 基准
   tsv（`COALESCE(col::text,'NULL')` 规范化）。
2. **pgbin 扩展 TOAST 解码**：
   - 命令行增加 toast 表 heap 路径参数（`--toast=<heap>`）。
   - external 头解析：`VARATT_EXTERNAL`（va_header=0x01）；读 va_valueid(4)+
     va_toastrelid(4)；PG12+ 无 toastidx，9.6/11 含（版本分支，实测确认）。
   - toast 表 heap 遍历：chunk_id/chunk_seq/chunk_data → 按 chunk_seq 排序拼接。
   - pglz 解压：压缩标志（va_extinfo 高位）→ pglz_decompress（从 third_party/pg184
     移植，用现有内存缓冲）。
   - 解出的原始 varlena 按 4B/1B 头再去头读值，进五维逐字段对照。
3. **verify 泛化**：`verify_consistency.py --table=poc_toast` 从 parquet schema +
   pg 列名映射自动生成规范化列，去掉硬编码列名与 id%500 TOAST 白名单。
4. **回归**：三版本各跑五维校验 + mutation 12 类（捕获率 100%）+ T0301/T0311 既有
   基线不回归。

## 用户故事

- 作为数据工程师，转换含大字段（TOAST 外置）的 PG 表后，校验应证明每个 TOAST 值
  与数据库一致，而非仅行数一致。
- 作为开发者，9.6 与 18 的 TOAST external 头布局差异应被自动对照捕获。

## 实现决策

- 解码路径进 pgbin（不做独立工具），失败时行级跳过并计数（不中断全量）。
- pglz 解压复用 third_party/pg184 的 pglz_decompress；压缩/未压缩两态都覆盖。
- toast 元组遍历复用现有 heap 页遍历框架（页解析/pg_xact 可见性）。

## 测试决策

- 校验基线 = T0311 五维（行数/逐字段/聚合/schema/类型语义）+ mutation 12 类。
- 版本矩阵 = 9.6/11/18 × {poc_orders 回归, poc_toast 新基线}。
- T0301/T0311 既有基线脚本重跑不回归（verify_version_convert.py、mutate_consistency.py）。

## 范围外

- 类型全集（float/uuid/json/bytea）扩列：pgbin 列集硬编码，列为后续任务。
- 非 heap 源（WAL 逻辑解码等）不涉及。
- toast 表物理布局仅支持 heap（无 index-only）读取，以 chunk_seq 顺序为准。

## 验收标准

- [ ] AC-1: 三版本（9.6/11/18）各灌 poc_toast（10000 行，含 480B/2564B 形态 + 稀疏 NULL），heap/tsv 基准齐全
- [ ] AC-2: pgbin 支持 `--toast=<heap>` 读 toast 表并解码 TOAST 值（压缩+未压缩），无崩溃
- [ ] AC-3: pgbin 参数统一为 `<heap> <clog_dir> <out> [--rows=] [--pg-version=]`
- [ ] AC-4: verify_consistency.py 泛化支持 `--table=`，去硬编码列名与 TOAST 白名单
- [ ] AC-5: 三版本 poc_toast 五维校验全 PASS（含 TOAST 值逐字段对照）
- [ ] AC-6: mutation 12 类捕获率 100%（poc_toast 基线）
- [ ] AC-7: T0301/T0311 既有基线回归 PASS（9.6/11/18 poc_orders）
- [ ] AC-8: evidence 登记（脚本/修复/报告）+ research-report 总结 external 头跨版本差异实测结论

## Seam 分析

### 声明的测试接缝
- seam: bench/verify_consistency.py -> src/pg/pgbin.cpp（TOAST 解码值对照）
- seam: bench/gen_toast.py -> src/pg/pgbin.cpp（TOAST 输入构造）
- seam: bench/mutate_consistency.py -> src/pg/pgbin.cpp（mutation 反向验证）

## 备注

- POC 输入补充（T0311）见文件尾部；缺陷修复参考 T0311 记录。
- 容器：t0301-pg96（9.6）、t0301-pg11（11）、t0216-pg（18, user test/test）。
- TOAST 数据形态：md5 列固定长度非压缩 4B 头形态；chars 列重复字符触发 pglz 压缩。
