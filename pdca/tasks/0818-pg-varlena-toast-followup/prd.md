# 跟进：PG 转换覆盖 4B 头 varlena 与 TOAST 外置路径（T0301 后续）

## 验收标准

## POC 输入补充（来自 T0311，2026-08-18）

T0311 POC 发现与建议，本任务须承接：

1. **TOAST 值对照**：pgbin 对 2KB+ payload 行跳过（parquet 空串，仅登记），需实现
   TOAST 值解码/对照（当前 2564B 样本 g%500==0 已存在于 poc_consistency）。
2. **4B 头 varlena 正式对照**：poc_consistency 已有 480B（4B 头未压缩）形态，可复用。
3. **校验基线**：使用 T0311 固化的五维校验 + mutation 12 类（捕获率 100%），脚本
   bench/verify_consistency.py、bench/mutate_consistency.py。
4. **NULL 行为跨版本回归**：POC 单 PG18 实测；9.6/11 的 NULL bitmap 行为用校验基线
   回归确认。
5. **pgbin 参数统一**：`<heap> <clog_dir> <out> [--rows=] [--pg-version=]`。
6. **类型全集**：float/uuid/json/bytea 等扩列（pgbin 列集硬编码 7 列）列为后续，
   本任务不必须。

缺陷修复参考：T0311 修复记录（src/pg/pg_heap_reader.c nullbit 判定/t_bits 偏移/
nulls 位图；pgbin.cpp validity_buf）。
