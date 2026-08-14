# AC-7 100M 行端到端全路径对照（MySQL 8.0 → Parquet）

日期：2026-08-14 ｜ 任务：T0250（Do 阶段收尾补充）

## 数据
- 表：`poct25.poc_orders_100m`，MySQL 8.0.36（t0250-mysql8:3307）
- 结构：`id BIGINT PK, customer_id INT, amount DECIMAL(12,2), created_at DATETIME(6), status VARCHAR(16), payload VARCHAR(96), active TINYINT(1)`，ROW_FORMAT=DYNAMIC
- 行数：**100,000,000**（SQL `COUNT(*)` 权威确认；id 范围 11 ~ 1,011,000,000）
- 固化 `.ibd`：5,888,802,816 B（359,374 页 / 16 KiB），干净关闭后 `podman cp` 直拷

## 对照路径（3 轮流中位数 / 单次全量）
| 路径 | rows | 耗时 s | 吞吐 rows/s | Parquet 大小 | 说明 |
|---|---|---|---|---|---|
| mysqlbin 物理直读 | 100,000,000 | 58.35 | 1,713,813 | 634 MB | 单次全量（parse 18.3s + arrays 13.1s + write 26.3s） |
| DuckDB mysql_scanner | 100,000,000 | 285.97（中位） | 349,693 | 494 MB | ATTACH TYPE mysql；COUNT + COPY zstd |

- mysqlbin 物理直读比 DuckDB 在线扫描 **快 4.9×**；Parquet 大小相差 28%（类型化 vs 通用 VARCHAR 物化+字典压缩差异）
- 两路输出 `rows=100,000,000` 均与 SQL count 一致

## 过程关键坑（可复用经验）
1. **自引用 `INSERT INTO t ... SELECT ... FROM t` 在 binlog=ROW 下回滚**：90M 行灌数一次触发 InnoDB 锁等待超时 ROLLING BACK（45M 行锁清理）。
   规避：先 `CREATE TABLE src AS SELECT * FROM t` 物化 10M 行源表，再 `INSERT ... SELECT ... FROM src`（不同表无锁冲突），成功且 188K 行/s。
2. **大文件禁止放 /tmp**：`/tmp` 为 tmpfs（7.5G），`podman cp` 5.3G ibd 时 quota 截断成 3.1G（文件只有前 196K 页，约 55.4M 行）。
   表现：mysqlbin/探针读出的 leaf 页与 nrecs 自洽但行数只有一半；对比 `SHOW TABLE STATUS Data_length=5.3G` 才暴露。
   规避：固化文件直接 cp 到项目 `data/100m/`（NVMe 128G 可用）。
3. DuckDB 1.5.x 移除 `mysql_scan()` 表函数，改用 `LOAD mysql_scanner; ATTACH 'host=... user=... password=... database=...' AS x (TYPE mysql);` 后按普通表查询。

## 产物
- `data/100m/poc_orders_100m.ibd`（固化 5.88G）
- `data/100m/poc_orders_100m_mysqlbin.parquet`（634 MB，96 row groups，7 列：id/customer_id INT64、amount FLBA、created_at INT64、status/payload BYTE_ARRAY、active BOOLEAN）
