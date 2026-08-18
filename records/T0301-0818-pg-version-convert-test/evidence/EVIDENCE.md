# PG 多版本（9.6/11/18）物理直读 → Parquet 验证记录（T0301 Do 阶段）

## 环境与数据
- 容器（各库 poct25, user=test）：
  - t0301-pg96: PG 9.6.24（CLOG 目录 pg_clog/）
  - t0301-pg11: PG 11.16（CLOG 目录 pg_xact/）
  - t0216-pg:  PG 18.4（CLOG 目录 pg_xact/）
- 三容器各灌 poc_orders 1M 行（7 列：int8 id / int4 customer_id / numeric(12,2) amount /
  timestamp created_at / text status / text payload / bool active），CHECKPOINT 后
  提取 heap 文件（各 154,566,656 B）与 CLOG 目录。
- 提取与校验：bench/gen_pg_versions.py、bench/extract_version_pg.sh、bench/verify_version_convert.py。

## 关键版本事实（实测修正，见 src/pg/pg_versions.h）
1. **heap 元组头布局各版本一致**：xmin/xmax/cid@0/4/8、ctid@12、infomask2@18、
   infomask@20、t_hoff@22、头 24B（三容器 pageinspect 均 t_hoff=24, t_infomask=2306）。
   早前"PG12 移除 t_xvac 使头 28B→24B"推论有误：t_xvac 与 t_cid 同处 t_field3
   union（4B），不改变头布局。
2. **varlena 编码各版本一致（packed）**：1B 头最低位=1，长度=头>>1（实测 payload
   头 0xA3→81B）；4B 头低 2 位=00/10，长度=(va_header>>2)&0x3FFFFFFF（实测临时表
   200B 文本 4B 头 0x00000330>>2=204B）。早前"PG13- 老格式（最高位标志）"无实例。
3. **CLOG 唯一版本差异为目录名**：PG9.x 及更早 pg_clog/，PG10+ pg_xact/；SLRU
   段（32 页/段）与 2-bit xid 状态编码一致，读取器同一（目录参数化）。

## 实现（src/pg/pg_heap_reader.c / pgbin.cpp / pg_clog_legacy_pg9.c）
- 自解码 heap 字段（替代 PG18 编译期 heap_deform_tuple），null bitmap 仅
  HEAP_HASNULL 时存在；varlena 对齐用字节探测（照抄 att_align_pointer）；
  numeric 解码为 Decimal128（memcpy 防非对齐 UBSan）。
- 布局/编码统一常量（无版本分派）；--pg-version=N 仅标注源版本与 CLOG 目录语义。
- CLOG 精确可见性（pg_tuple_visible）等效 MVCC 快照。

## 验证结果（verify_version_convert.py 全量 1M×7 列）
| 版本 | parquet | 逐字段差异 | 聚合 | sum_amount | active=true | id 范围 |
|---|---|---|---|---|---|---|
| 9.6 | 24,245,766 B | 0 | PASS | 5000005000.00 | 500000 | [1,1000000] |
| 11  | 24,245,766 B | 0 | PASS | 5000005000.00 | 500000 | [1,1000000] |
| 18  | 24,245,766 B | 0 | PASS | 5000005000.00 | 500000 | [1,1000000] |

- 转换吞吐：约 1.2M-1.4M rows/s（parse+text+arrays+write 合计，ZSTD 写出）。
- seen_total=1,000,000，skipped_invisible/dead/toast 均 0。
- parquet 与 SQL 基准（poc_orders.sql.tsv，UTC 格式化）按 id 排序后逐字段对照差异=0。

## 调试回溯（防回归）
- PG11 崩溃（row=0 t_hoff=0）：根因 PgHeapLayouts[PG11-]={24,22,26,28} 错误
  （t_hoff 实为偏移 22，读 b[26]=0 → dp=b 全错位）。实测修正后布局统一。
- PG9.6 早前"成功"为假象：--pg-version=96 被 atoi(96)>11 判为 PGVER_12PLUS，
  恰好 24B 布局与 packed varlena 才是正确解释——印证统一布局。