# PostgreSQL 数据文件直接转 Parquet POC 报告（C++ 物理路径）

## 调研目标

验证物理路径的极限形态：复用 PostgreSQL 18.4 官方源码（`heap_deform_tuple` +
backend 内存上下文与 elog 基础设施），以 C++ 直读 heap 数据文件并调用 Arrow C++
写入 Parquet，对照逻辑路径与 pg_filedump 路径评估吞吐、资源与类型保真。

## 方法

- 源数据: `/tmp/opencode/pgfiledump-test/poc_orders_heap`（poc_orders 的 main fork，136536064 bytes，CHECKPOINT 后从容器拷出）。
- 行解码: 官方 `heap_deform_tuple`（`src/backend/access/common/heaptuple.c`），backend 依赖以 `stub_pg.c` 桩实现（elog/mcxt/hash/except 等），内存分配复用官方 `aset/generation/slab/bump/alignedalloc`。
- numeric 解码: 自定义 `decode_numeric`（short/long 头解析 + 公共指数对齐换算 Decimal128，`ndigits==0` 的零值 2 字节头单独处理）。
- 写入: Arrow C++（Decimal128(12,2) / TIMESTAMP(us) / VARCHAR / BOOLEAN），Parquet ZSTD，batch 1<<20，单进程单线程。
- 编译: `gcc/g++ -O2 -ffunction-sections -fdata-sections -Wl,--gc-sections`。

## 发现

- 端到端耗时: 0.633s，吞吐 1,578,666 rows/s（含写盘）
- 解析阶段耗时: 0.141s（读页+deform+decode，7092199 rows/s）
- 转换组装耗时: 0.052s（text）+ 0.033s（arrays）
- Parquet 写入耗时: 0.408s
- Parquet 大小: 25978753 bytes（较 pg_filedump 路径 26020890 bytes 略小）
- 峰值 RSS: 349.5 MiB（pg_filedump 路径为 911.25 MiB，逻辑路径 COPY 为 972 MiB）
- 行数校验: source=1000000, parquet=1000000, distinct id=1000000
- 数值保真: amount == (id % 100000) / 100.0 全量 1000000/1000000 精确匹配（DECIMAL(12,2)，含 0.00 边界行）
- 类型保真: BIGINT/INTEGER/DECIMAL(12,2)/TIMESTAMP/VARCHAR/BOOLEAN 与源表完全一致
- 分布校验: status 四值各 250000 行均匀

## 结论与建议

- C++ 官方源码物理路径为六路径中吞吐最高、资源最低的形态：较逻辑路径 COPY（0.82s、972 MiB）快约 1.3 倍，较 DuckDB 直转（1.333s）快约 2.1 倍。
- 官方代码复用成本低（仅 stub 少量 backend 符号），`heap_deform_tuple` 天然处理 null bitmap 与 attcacheoff，无需手推列偏移。
- 工程化注意: numeric 空 digits（零值）须显式处理；`attcacheoff` 缓存依赖正确 tuple descriptor。
- 吞吐与限制对照见总报告 research-report.md 第 6 节。

## 参考资料

- 本任务 PRD: `prd.md`
- 原始指标: `pg_cpp_metrics.json`
- 总报告: `../../research-report.md`
