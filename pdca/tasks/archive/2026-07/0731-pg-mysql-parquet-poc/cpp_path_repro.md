# C++ 物理路径 — 数据流、构建、运行与验证命令（复现手册）

数据文件直接转换（复用 PostgreSQL 18.4 官方源码）。源码：`pg_heap_reader.c`（heap 解析 + numeric 解码）、`main.cpp`（Arrow/Parquet 写入）、`stub_pg.c`（backend 符号桩）。

## 0. 数据流全景

```
PG 表 poc_orders (100 万行)
  │  ① 建表 + generate_series 生成数据
  │  ② CHECKPOINT 落盘
  ▼
heap 数据文件 base/5/poc_orders_heap（136,536,064 B，8KB×16667 页）
  │  ③ docker cp 拷出到测试机
  ▼
/tmp/opencode/pgfiledump-test/poc_orders_heap
  │  ④ pgbin：读页 → 官方 heap_deform_tuple 解行 → decode_numeric → Arrow 列式组装
  │      → ParquetWriter(zstd, batch 1<<20) 写盘
  ▼
pg_final.parquet（25,978,753 B，7 列，DECIMAL(12,2) 无损）
  │  ⑤ DuckDB 读回校验（行数/唯一 id/amount 规则/类型）
  ▼
验证通过：1,000,000 行 / 1,000,000 distinct / amount 规则 1M 精确匹配
```

## 1. 环境变量

```sh
S=/tmp/opencode/pgsrc/postgresql-18.4/src/include        # PG 18.4 源码 include
P=/home/black/Public/aio/Idea/Parquet/.venv/lib/python3.14/site-packages/pyarrow   # pyarrow 2500 系列
D=/tmp/opencode/pgfiledump-test                            # 工作目录
```

## 2. 数据生成（PG 侧，poc-postgres 容器，端口 55432）

```sh
# 建表 + 100 万行（规则与 DuckDB/pg_filedump 各路径完全一致，保证同口径对比）
psql -h 127.0.0.1 -p 55432 -U postgres -d pocdb << 'SQL'
DROP TABLE IF EXISTS poc_orders;
CREATE TABLE poc_orders (
  id BIGINT PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  status TEXT NOT NULL,
  payload TEXT NOT NULL,
  active BOOLEAN NOT NULL
);
INSERT INTO poc_orders
SELECT
  g AS id,
  (g % 100000)::integer AS customer_id,
  round(((g % 100000)::numeric / 100), 2) AS amount,
  timestamp '2026-01-01 00:00:00' + (g || ' seconds')::interval AS created_at,
  CASE g % 4 WHEN 0 THEN 'new' WHEN 1 THEN 'paid' WHEN 2 THEN 'shipped' ELSE 'closed' END AS status,
  md5(g::text) || repeat('x', 32) AS payload,
  (g % 2 = 0) AS active
FROM generate_series(1, 1000000) AS g;
SQL
```

## 3. poc_orders_heap 是怎么来的（heap 数据文件定位与拷贝）

`poc_orders_heap` 不是人工生成的文件，而是 **poc_orders 表的 main fork 数据文件本身**（relfilenode=16414，文件名即 relfilenode 数字），从 PG 容器拷出时按表名重命名。来源链：

```
CREATE TABLE poc_orders + INSERT 100 万行
  → 行数据写入表堆 base/<库OID>/16414（relfilenode，136,536,064 B = 8192 B × 16667 页）
  → CHECKPOINT 全部落盘
  → docker cp 拷出 → 重命名为 poc_orders_heap
  → sha256 与容器内文件全等校验通过
```

```sh
# 3.1 查表物理文件路径（返回 base/<库OID>/<relfilenode>，如 base/16384/16414）
podman exec pdca-pg-parquet-poc su postgres -c \
  "psql -p 55432 -d poc -c \"SELECT pg_relation_filepath('poc_orders'), pg_relation_filenode('poc_orders')\""

# 3.2 CHECKPOINT 保证数据全部落盘、文件一致（物理路径的前提）
podman exec pdca-pg-parquet-poc su postgres -c 'psql -p 55432 -d poc -c "CHECKPOINT"'

# 3.3 容器内核对文件大小（期望 136536064 = 8192 × 16667）
podman exec pdca-pg-parquet-poc su postgres -c \
  "ls -la /var/lib/postgresql/18/docker/base/16384/16414"

# 3.4 拷出到测试机（按表名重命名）
podman cp pdca-pg-parquet-poc:/var/lib/postgresql/18/docker/base/16384/16414 $D/poc_orders_heap

# 3.5 一致性校验：两侧 sha256 必须完全一致（实测 02dc47aa0f70018b…）
podman exec pdca-pg-parquet-poc su postgres -c \
  "sha256sum /var/lib/postgresql/18/docker/base/16384/16414"
sha256sum $D/poc_orders_heap
```

注意：库 OID、relfilenode 数字随实例变化（本机当前为 16384/16414；此前容器曾为 base/5），**必须用 `pg_relation_filepath` 现场查询，不可硬编码**。新表在无 VACUUM FULL 情况下 relfilenode 稳定；若曾 VACUUM FULL 需重新查询。

**heap 文件物理结构（解码依据）：**
- 8KB 页 × 16667 页；每页 page header（PageHeaderData）→ 行指针数组（ItemIdData，偏移 4B）→ 元组区。
- 行 = HeapTupleHeaderData（t_hoff 后为数据区）+ 定长/变长列按 attalignby 对齐布局；表 7 列均 NOT NULL → 无 null bitmap。
- varlena 短头：低 1 位=1 表示 1 字节头（长度含头），如 amount 的 `0b` = 11 字节总长；numeric 短型头 2 字节（dscale/weight/sign），如 `0x7f81` = dscale=3, weight=-1 → digit 100 → 0.01。
- 零值 numeric 仅 2 字节头（ndigits=0，varlena 总长 3B）——见第 7 节踩坑。

## 4. 编译官方 PG 对象（仅一次）

```sh
for f in heaptuple:backend/access/common mcxt:backend/utils/mmgr aset:backend/utils/mmgr \
         generation:backend/utils/mmgr slab:backend/utils/mmgr bump:backend/utils/mmgr \
         alignedalloc:backend/utils/mmgr; do
  src=${f%%:*}; dir=${f##*:}
  gcc -O2 -std=gnu11 -ffunction-sections -fdata-sections -I$S -I$S/port/linux -I$S/port \
      -c $S/../src/$dir/$src.c -o $D/$src.o
done
gcc -O2 -std=gnu11 -ffunction-sections -fdata-sections -I$S -I$S/port/linux -I$S/port \
    -c $S/../src/port/snprintf.c -o $D/pg_snprintf.o
```

## 5. 编译本项目代码并链接

```sh
gcc -O2 -std=gnu11 -ffunction-sections -fdata-sections -I$S -I$S/port/linux -I$S/port \
    -c $D/pg_heap_reader.c -o $D/pg_heap_reader.o
g++ -O2 -c $D/main.cpp -o $D/main.o
gcc -O2 -std=gnu11 -ffunction-sections -fdata-sections -I$S -I$S/port/linux -I$S/port \
    -c $D/stub_pg.c -o $D/stub_pg.o
g++ -O2 -o $D/pgbin $D/pg_heap_reader.o $D/heaptuple.o $D/mcxt.o $D/aset.o $D/generation.o \
    $D/slab.o $D/bump.o $D/alignedalloc.o $D/stub_pg.o $D/main.o $D/pg_snprintf.o \
    -L$P -Wl,-rpath,$P -Wl,--gc-sections -l:libarrow.so.2500 -l:libparquet.so.2500 -lpthread
```

## 6. 运行与验证

```sh
# 6.1 转换（heap 文件 → Parquet）；输出 JSON 指标
$D/pgbin $D/poc_orders_heap /tmp/opencode/pgfiledump-test/pg_final.parquet 1000000
# {rows:1000000, parse_seconds, text_seconds, arrays_seconds, write_seconds, total_seconds,
#  throughput_rows_per_second}

# 6.2 DuckDB 读回校验
python3 - << 'EOF'
import duckdb
con = duckdb.connect()
con.execute("CREATE VIEW v AS SELECT * FROM read_parquet('/tmp/opencode/pgfiledump-test/pg_final.parquet')")
print(con.execute("SELECT count(*), count(DISTINCT id) FROM v").fetchone())          # (1000000, 1000000)
print(con.execute("SELECT count(*) FROM v WHERE amount = (id % 100000) / 100.0").fetchone())  # (1000000,)
print(con.execute("SELECT typeof(amount), typeof(created_at) FROM v LIMIT 1").fetchone())      # (DECIMAL(12,2), TIMESTAMP)
print(con.execute("SELECT id, amount, status, active FROM v WHERE id IN (1, 999999, 1000000) ORDER BY id").fetchall())
EOF
```

## 7. 关键实现点（踩坑记录）

- `heap_deform_tuple` 需要合法 `TupleDesc`（CompactAttribute 布局：attlen/attbyval/attalignby/attcacheoff=-1），构造见 `make_tupdesc()`；deform 自动处理 null bitmap 与 attcacheoff 缓存，无需手推列偏移。
- backend 依赖以 stub 提供：errstart/errfinish/errcode/errmsg/errdetail/errcontext_msg、error_context_stack、ExceptionalCondition、hash_bytes/hash_create/hash_search、datumCopy、pg_mbcliplen、stack_is_too_deep、pg_strerror_r；`pg_fprintf`/`pg_snprintf` 来自官方 snprintf.c。
- numeric 解码（`decode_numeric`）：short/long 头解析 → 每 digit 指数 `4*(weight-i)+target_scale` → 公共最小指数对齐后一次乘除（保持 Decimal128 精确）。
- **空 digits 零值**（2 字节头，ndigits=0，如 amount=0.00 的行）必须提前返回 0：否则 `min_exp` 保持 INT_MAX，`value *= 10` 循环 2^31-1 次/行，实测单次运行 21.9s（修复后 0.14s）。
- 链接需 `-ffunction-sections -fdata-sections -Wl,--gc-sections` 丢弃未引用 backend 符号；C 文件用 gcc 编译、g++ 链接。
- 物理路径前提：CHECKPOINT 后文件一致；只覆盖单表 heap（TOAST 列需另处理）。

## 8. 实测指标（本机复现）

- parse 0.141s（709 万 rows/s）→ text 0.052s → arrays 0.033s → write 0.408s → 端到端 0.633s（157.9 万 rows/s）
- Parquet 25,978,753 B，峰值 RSS 349.5 MiB
- 验证：1,000,000 行 / 1,000,000 distinct id / amount 规则 1,000,000 精确匹配 / DECIMAL(12,2)+TIMESTAMP 类型保真 / status 四值各 250,000
