# PostgreSQL 逻辑导出转换 Parquet POC 报告

## 调研目标

验证 PostgreSQL 使用逻辑 COPY 导出后转换为 Parquet 的本地端到端性能和数据校验结果。

## 实验环境

- 测试机器: AMD Ryzen 7 PRO 4750U（16 线程），15 GiB 内存，NVMe 磁盘（Linux 7.1.5-arch1-1 x86_64）
- Python: 3.14.6（`.venv-poc`），fastparquet 2026.5.0，pandas 2.3.3，psycopg2 2.9.12
- 容器运行时: podman 6.0.2（host 网络模式）
- PostgreSQL: 容器内 `docker.io/library/postgres:latest`（PostgreSQL 18.4）

## 方法

- 使用 Podman 临时 PostgreSQL 实例，目标行数 1000000。
- 在 PostgreSQL 内用 `generate_series` 构造包含整数、NUMERIC、TIMESTAMP、TEXT、BOOLEAN 的测试表。
- 使用 `COPY (...) TO STDOUT WITH CSV HEADER` 执行逻辑导出。
- 使用 pandas + fastparquet 将 CSV 转为 ZSTD 压缩 Parquet。

## 可复现命令

```bash
# 1. 启动 PostgreSQL 容器（host 网络，容器内端口 55432）
podman run -d --name pdca-pg-parquet-poc --network host \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=poc \
  docker.io/library/postgres:latest -c listen_addresses=* -c port=55432

# 2. 运行 POC（在任务目录 0731-pg-mysql-parquet-poc 下）
/home/black/Public/aio/Idea/Parquet/.venv-poc/bin/python pg_poc.py \
  --host 127.0.0.1 --port 55432 --dbname poc --user postgres --password postgres \
  --rows 1000000 --out poc-output/pg

# 3. 清理
podman rm -f pdca-pg-parquet-poc
```

## 发现

- PostgreSQL 版本: `PostgreSQL 18.4 (Debian 18.4-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`
- 准备数据耗时: 5.721s
- COPY 导出耗时: 1.226s
- CSV 读取耗时: 3.281s
- Parquet 写入耗时: 1.634s
- 端到端耗时: 11.979s
- 端到端吞吐: 83477.95 rows/s
- 导出吞吐: 815447.62 rows/s
- 转换吞吐: 203425.23 rows/s
- CSV 大小: 112667851 bytes
- Parquet 大小: 23896107 bytes
- CSV/Parquet 压缩比: 4.71x
- 峰值 RSS: 433.57 MiB
- 行数校验: source=1000000, parquet=1000000, match=True

## 结论与建议

- PostgreSQL 逻辑 COPY 导出链路已完成端到端验证：1M 行 112.7 MB CSV 导出仅 1.23s（导出吞吐 81.5 万 rows/s），瓶颈在 CSV 读取 + Parquet 写入的转换阶段（合计 4.92s，占端到端 41%）。
- 当前转换通过 CSV 中间态完成，NUMERIC 在 pandas 侧按 float64 读取，生产级工程化需要补测 Decimal 保真路径。
- MySQL 实测已按用户决策取消；`mysqlsh` 原生 Parquet 导出未覆盖，记为后续决策缺口（详见总报告 research-report.md）。

## 参考资料

- 本任务 PRD: `prd.md`
- 原始指标: `pg_metrics.json`
- 总报告: `../../research-report.md`
