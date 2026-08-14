# PG 物理直读 → Parquet 验证记录（T0250 Do 阶段）

## 环境
- PG: 18.4 (容器 t0216-pg, 端口 5433, user=test, db=poct25)
- Arrow C++: pyarrow 2500 (libarrow.so.2500) @ venv
- 编译: g++ 16.2.1, C++20, --gc-sections; PG 生成头 (configure+make src/include)

## V1 场景（1M INSERT，无删除/更新）
- 表 `poc_orders`（7 列）：int8 id / int4 customer_id / numeric(12,2) amount /
  timestamp created_at / text status / text payload / bool active
- heap 文件 `base/1929481/1929482`（136,536,064 B）
- pgbin 转换：
  - rows=1,000,000, seen_total=1,000,000, invisible=0, dead=0, toast=0
  - parse 0.18s / total 0.84s / **吞吐 1,188,111 rows/s**（ZSTD 压缩写出）
- Parquet 大小：26,014,189 B（≈26MB / 20.8 B/行）
- DuckDB 校验（vs PSQL 全量聚合）：7 项全部一致
  | 指标 | Parquet | PG |
  |---|---|---|
  | count | 1,000,000 | 1,000,000 |
  | distinct id | 1,000,000 | 1,000,000 |
  | amount 范围 | 0.00–999.99 | 0.00–999.99 |
  | distinct status | 4 | 4 |
  | distinct payload | 1,000,000 | 1,000,000 |
  | active=true | 500,000 | 500,000 |
  | created_at 范围 | 2026-01-01~01-12 | 同 |

## Boundary 表（8 列边界类型）
- 大 payload (9000/7000 重复字符) → **TOAST 压缩**，解析跳过（VARATT_IS_COMPRESSED → skipped_toast）
- NULL / 空串 / emoji UTF-8 (😀🚀é中) / numeric 极值 ±9999999999.99 / 历史时间戳(1999) → 解析正确
- 暴露 bug并修复：① bool 列字节数组被当位图（已修复 bits_pack）
  ② status/payload 共享 buffer 致偏移错位（已修复独立 buffer）
  ③ 压缩 varlena 越界读（已修复跳过+计数）

## V2/V3/V4 可见性四场景（CLOG 精确判断）
- 表 `poc_scen_v2/v3/v4`（3 列 id/val/note），操作后 CHECKPOINT 再拷贝 pg_xact
  （关键约束：CLOG 必须与 heap 同快照！！）
- **结果（物理直读 visible vs PG SELECT count 差异=0）**：

| 场景 | 操作 | PG count | 物理 visible | invisible | 差异 |
|---|---|---|---|---|---|
| V1 | 1M INSERT | 1,000,000 | 1,000,000 | 0 | 0 |
| V2 | 11 行 + UPDATE 5 + DELETE 5 | 6 | 6 | 10 | 0 |
| V3 | 10 行 + DELETE 5 | 5 | 5 | 5 | 0 |
| V4 | 4 提交 + 2 回滚 + 2 再提交 | 4 | 4 | 2 | 0 |

- 附加发现：维护时如果只拷 heap 不重拷 pg_xact，V2/V3 会误判全 invisible
  （CLOG 过期），V4 因 frozen 不受影响 → 快照一致性是物理直读的关键前提

## 100M 回归：FROZEN hint-bit 误判（AC-10，详见 ac10_pg_100m_frozen_fix.md）
- 现象：100M 直读 rows=65,581,895，skipped_invisible=34,418,105。
- 根因：`HEAP_XMIN_FROZEN = COMMITTED|INVALID` 两 bit 同置，原 `pg_tuple_visible`
  先判 `XMIN_INVALID→invisible`，把 34.4% frozen 行全误判；且 PG12+ heap 头布局
  t_infomask 在偏移 20（非旧文档 24）。
- 修复：INVALID 置位时先排除 FROZEN（COMMITTED 同置→可见），仅纯 INVALID 判 aborted。
- 结果：rows=100,000,000 == SQL COUNT(*)，差异 0，skipped_invisible=0；id 1..100M 连续。
- 性能：1.90M rows/s（parse 12.2s / write 36.5s / total 52.7s）。

## 结论
PG 侧原型完成：物理文件直读 → Parquet 全链路正确，MVCC 可见性用 CLOG 精确匹配，
性能 ~1.19M rows/s（ZSTD）/ 100M 1.90M rows/s，可作为 DuckDB postgres_scanner 对照基准。

## 产物
- build/pgbin（主工具，heap+pg_xact → parquet+JSON 指标）
- tools/dump_boundary.c（边界表逐字段 dump）
- tools/pgbin_scen.c（场景表可见性计数验证）
- bench/gen.py（数据生成）、bench/gen_scenarios_pg.py（V2-V4 场景构造）
- 本文件