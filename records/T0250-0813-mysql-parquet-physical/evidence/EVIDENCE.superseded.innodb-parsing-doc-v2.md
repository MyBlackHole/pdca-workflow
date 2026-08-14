# MySQL InnoDB 物理直读 → Parquet 验证记录（T0250 Do 阶段）

## 环境
- MySQL: 8.0（容器 t0250-mysql8，端口 3307，root/test，库 poct25）
- 镜像: docker.io/library/mysql:8.0（818MB），podman 6.0.2 rootless
- 快照方式: `SET GLOBAL innodb_fast_shutdown=1` + `FLUSH TABLES` + `podman stop -t 60`
  → 数据位于匿名卷 `03418972.../_data/poct25/`（需 `podman unshare` 读取）
- Arrow C++: pyarrow 2500（libarrow.so.2500）@ venv；编译 g++ 16.2.1 C++20

## V1 场景（1M INSERT，无删除/更新）
- 表 `poc_orders`（7 列，全 NOT NULL，主键 id）：
  id BIGINT / customer_id INT / amount DECIMAL(12,2) / created_at DATETIME(6) /
  status VARCHAR(16) / payload VARCHAR(96) / active TINYINT(1)
- .ibd 文件 `poct25/poc_orders.ibd`（138,412,032 B = 8448 页×16KB）
  - INDEX 页 7703（叶 7693 + 非叶 10）、ALLOCATED 741、SDI 1、FSP/XDES/IBUF 各 1
- mysqlbin 转换：
  - rows=1,000,000；parse 0.21s / total 1.07s / **吞吐 936,482 rows/s**（ZSTD 写出）
- Parquet 大小：23,818,195 B（≈22.7MB / 22.7 B/行；PG 同数据 26MB）
- DuckDB 校验（vs MySQL SQL 全量聚合）：全部一致
  | 指标 | Parquet | MySQL |
  |---|---|---|
  | count | 1,000,000 | 1,000,000 |
  | SUM(id) | 500,000,500,000 | 500,000,500,000 |
  | SUM(customer_id) | 500,500,000 | 500,500,000 |
  | SUM(amount) | 499,995,000.00 | 499,995,000.00 |
  | amount 范围 | 0.00–999.99 | 0.00–999.99 |
  | distinct status | 4 (new/paid/shipped/closed) | 4 |
  | active=true | 500,000 | 500,000 |
  | created_at 范围 | 2026-01-01 00:00:01 ~ 01-12 13:46:40 | 同 |

## InnoDB 页/记录格式逆向（COMPACT/DYNAMIC，依据 percona-xtrabackup 8.0 源码）
- 页常量：`FIL_PAGE_TYPE`=24（INDEX=17855）、`FIL_PAGE_DATA`=38、`PAGE_N_RECS`=54、
  `PAGE_LEVEL`=64、`PAGE_INDEX_ID`=66；`PAGE_NEW_INFIMUM`=99(0x63)
- 记录头（extra 5B，在 origin 前）：byte0=info_bits<<4|n_owned，
  byte1-2=status+heap_no 大端 `(heap_no<<3)|status`，byte3-4=next（**相对当前 origin 的有符号偏移**，
  `next_offs = rec + (int16)field`，rem0rec.ic rec_get_next_offs）
- 变长字段长度数组位于 origin 前：status_len@org-6、payload_len@org-7（nulls 区 0 字节，全 NOT NULL）
- **整数存储**（row0mysql.cc row_mysql_store_col_in_innobase_format）：MySQL 小端 → InnoDB 大端 +
  **有符号符号位取反（首字节 ^0x80）**。BIGINT 1→`80 00...01`，INT 1→`80 00 00 01`，-111→`7f ff...91`
- **DECIMAL(12,2)**：6 字节 `[符号+intg高位(1B)][intg_lo(4B BE)][frac(1B)]`，
  `intg=(b0&0x7F)*1e9 + be32(b1..4)`，值=intg + frac/100（0x80=正；0.01→`80 00 00 00 00 01`，
  9999999999.99→`80 00 00 00 63 63`，边界最大→`89 3B 9A C9 FF 63`）
- **DATETIME(6)**：8 字节（5B 日期 + 3B 微秒），日期位域 `ym<<22|day<<17|hour<<12|min<<6|sec`，
  ym=year*13+month（**month 0-indexed**，2026-01-01→0x19B8C20001）
- **聚簇索引字段物理序（实测）**：[id][DB_TRX_ID 6B][DB_ROLL_PTR 7B][其余用户列]
  （系统列插在主键与普通列之间）
- 本表字段布局（叶记录）：id@org+0(8B) / sys 13B / customer_id@org+21(4B) /
  amount@org+25(6B) / created_at@org+31(8B) / status@org+39(变长) /
  payload@org+39+sl(变长) / active@org+39+sl+pl(1B)

## Boundary 表（已完成，全字段验证通过）
- `poc_boundary`（8 列含 NULL/TEXT/emoji/DECIMAL 极值/DATETIME 历史时间）
  `poct25/poc_boundary.ibd`（照源码 SDI 驱动解析，非硬编码）
- **新版 LOB（MySQL 8.0.13+）**：9000B TEXT → off-page 存 `FIL_PAGE_TYPE_LOB_FIRST`(type 24) 页，
  外部 REF（20B：space 4B+page 4B+offset 2B+version 2B+len 8B BE）；LOB 首页结构：
  `DATA_LEN@54`(4B)、index 数组常量 10 node×60B → **data_begin=696**；
  7000B < 半页(8192B) 不 off-page，本地存于记录
- **3 行全字段对照（vs SQL，全部一致）**：
  | 列 | id=1 | id=2 | id=3 |
  |---|---|---|---|
  | n_null (NULL) | NULL | NULL | 42 |
  | s_empty (VARCHAR) | '' len0 | '' len0 | '   ' len3 |
  | d_extreme (DECIMAL(12,2)) | 9999999999.99 | **-9999999999.99** | 0.00 |
  | b_large (TEXT) | 'x'×9000 off-page | 'y'×7000 本地 | 'tiny' len4 |
  | u_emoji | 'emoji:<多字节>' len35 | 'plain ascii' len11 | 'b' len1 |
  | t_ts (DATETIME) | 2026-01-01 00:00:00 | 2026-12-31 23:59:59 | 1999-06-15 12:30:00 |
  | act (TINYINT) | 1 | 0 | 1 |
- SDI 驱动通用解析（Python 原型 `/tmp/opencode/innodb_sdi.py`）：rec_init_offsets_comp_ordinary
  语义（NULL 位图 LSB 起 / 变长 len 反序存储 / DATA_BIG_COL 2B 编码 + 0x4000 external 位），
  已从源码推导并在 boundary 验证

## V2/V3/V4/V5 场景（UPDATE/DELETE/ROLLBACK，对标 PG 可见性场景）
- 场景表（id BIGINT PK, val INT, note TEXT）+ 快照：`SET innodb_fast_shutdown=0` +
  `mysqladmin shutdown` 固化（见下）；物理直读 `tools/../ /tmp/opencode/innodb_scen.py`
- 结果（物理直读可见行 vs SQL 全表，全部一致）：
  | 表 | 操作 | SQL 可见 | 物理可见 | deleted标记 |
  |---|---|---|---|---|
  | v2 | 11 行 + UPDATE 5(val+1) + DELETE 5 | 6 | 6 (val=11,31,51,71,91,110) | 0（已 purge） |
  | v3 | 10 行 + DELETE 5 | 5 | 5 (id 6-10) | 0（已 purge） |
  | v4 | COMMIT 2 + ROLLBACK 2 + 再插 2 | 4 | 4 (id 1,2,5,6) | 0（回滚清除） |
  | v5 | UPDATE 大 TEXT note 9000a→9000b + val→99 | 1 | 1 (val=99, note=LOB pg6 'b'×9000) | 0 |
  | v7 | 8 行 + DELETE 4（ReadView 冻结阻止 purge） | 4 | 4 (id 5-8) | **4（保留验证）** |
- **delete-mark 识别**：记录头 byte0（origin-5）`info_bits=(b0>>4)&7`，
  `REC_INFO_DELETED_FLAG=0x20` → 位2（`b0 & 0x20`）；deleted 记录仍串在主链上，
  解析器跳过即得可见行；已删除记录 purge 后会从链上消失（PAGE_N_RECS 减少）
- **保留 delete-mark 的方法**（v7 验证）：后台开 RR 事务 `DO SLEEP(150)` 建立旧 ReadView
  阻塞 purge → DELETE 提交后 `FLUSH TABLES` 落盘 → 运行中拷 .ibd（b0=0x20/0x24 标记可见）
- **UPDATE 大字段**（v5）：TEXT 9000a→9000b 触发新 LOB_FIRST 页（页6 'b'），
  记录 REF 指向新页，旧 LOB 页（页5 'a'）残留孤儿；物理直读自动得到最新版本
- UPDATE 小字段（v2 的 val）：in-place 更新，物理记录即最新值，旧值仅存 undo log

## 正式工具 delete-mark 过滤（mysqlbin C 解析器）
- `src/mysql/mysql_parse_pages.c` 记录链遍历加入
  `if (!((page[org-5] >> 5) & 1))` 跳过 delete-mark（REC_INFO_DELETED_FLAG=0x20）
- 验证（同构 poc_orders schema，10 行 + DELETE 3 保留 delete-mark）：
  页 nrecs=10（3 条 b0 bit5 置位 + 7 可见）→ mysqlbin **rows=7** == SQL count=7 ✓
- 回归：poc_orders 1M 无删除表 rows 仍 = 1,000,000 ✓（过滤不影响普通表）
- **保留 delete-mark 快照的可靠方法**（v7/del5 实测）：
  ① 后台 RR 事务读**别的表**建立旧 ReadView（阻塞 purge，勿读目标表否则
     FLUSH/MDL 被锁）② DELETE 提交 ③ **等待 ~8s 让 checkpointer 刷 dirty 页**（
     FLUSH TABLES 不强制刷该表脏页，需等后台 checkpoint）④ 运行中拷 .ibd
- 注：无 ReadView 保护时（或正常关闭 mysqladmin shutdown）purge 会物理删除
  delete-mark 记录，PAGE_N_RECS 同步减少——此时遍历链自然得到可见行，结果同样正确

## BLOB 快照一致性陷阱（重要）
- `podman stop` 触发的关闭**不 flush InnoDB 脏页**（无 "Shutdown completed" 日志；
  早期快照 .ibd 缺 BLOB 数据页导致解不出大 TEXT）
- 可靠流程：`SET GLOBAL innodb_fast_shutdown=0` 后**在容器内 `mysqladmin shutdown`**
  （正常关闭全量刷盘，mtime 更新、BLOB 页落盘）→ 再 `podman unshare` 拷贝 .ibd
- 对照实验：新插 blob_test（9000B z）→ mysqladmin 关闭后 z=9000 落盘确认

## SDI 驱动通用 C 工具（mysqlbin 动态 schema）
- 此前 mysqlbin 硬编码 poc_orders 字段布局；现改为 **SDI 驱动**，任意表 .ibd 可直接转 Parquet：
  - `src/mysql/mysql_sdi.c/.h`：从 FIL_PAGE_SDI 页解压 zlib JSON 表定义，构建物理布局
  - `src/mysql/mysql_parse_pages.c`：通用 rec_offsets + 全类型解码（INT/DECIMAL/DATETIME2/TIME2/STRING/BLOB/off-page LOB）
  - `src/mysql/mysqlbin.cpp`：动态 Arrow schema，按列类型映射输出
- **关键逆向（对照 ibd2sdi / rem0rec / row0mysql）**：
  - SDI 记录：rec 首 4B=(type,type2,id)，`id==1` 为表定义；压缩 payload 从 **rec+33** 起 zlib
  - 布局：**PRIMARY 索引 elements 顺序 = 物理列序**（主键列 + DB_TRX_ID 6B + DB_ROLL_PTR 7B + 其余列）；
    系统列**必须在布局中占位对齐 offsets，但输出时跳过**（不写 Parquet）
  - 主键列数 = elements 中 `hidden==false` 的个数（true = 系统列/聚集附加列）
  - `tinyint(1)` → Parquet **boolean**（读 column_type_utf8 判断）
  - 类型映射：INT→int64、FLOAT→float32、DOUBLE→float64、DECIMAL→decimal128(p,s)、
    DATETIME2/TIMESTAMP2→timestamp(us)、TIME2→int64、VARCHAR/CHAR→utf8、TEXT/BLOB→binary
- **构建**：`bash scripts/build_mysqlbin.sh`（链接需 `-lz`，mysql_sdi.o 用 zlib）
- **回归/场景全通过**（用同一 mysqlbin 跑各类表）：
  | 表 | rows | 对照 SQL |
  |---|---|---|
  | poc_orders (1M) | 1,000,000 | 聚合全一致（SUM amount 499,995,000.00 / status 4×250,000 / active 500,000） |
  | poc_boundary | 3 | 全字段一致（NULL/负数 DECIMAL/9000B off-page LOB/emoji/1999 历史时间） |
  | poc_scen_v5 | 1 | val=99, note='b'×9000（更新后 LOB 页） |
  | poc_scen_v2/v3/v4/v7 | 6/5/4/4 | 各类更新场景行值一致 |
  | poc_orders_del5 | 7 | 页内 3 条 delete-mark 被跳过（SQL DELETE 3 后剩 7） |
  | poc_nopk（无主键） | 3 | a=(1,2,NULL)/b=x,y,z/c=1.50,2.50,3.50 全对 |
  | poc_compk（复合主键） | 3 | a/b/c 全对；DATETIME(3) d 修复后 .123/.456/.789 精确 |
  | poc_dt（DATETIME 精度 3-6） | 3 | d3-d6 微秒 1/10/100/123456/999999 边界全对 |
  | poc_time / poc_time2（TIME 精度 0-6） | 3/2 | 超 24h(838:59:59)、负数 frac 反向补码、fsp 全区间正确 |
- **无主键表（GEN_CLUST_INDEX）**：SDI 里仍有名为 PRIMARY 的索引（type=2），
  elements 顺序 = DB_ROW_ID(6B) + DB_TRX_ID(6B) + DB_ROLL_PTR(7B) + 用户列；
  **DB_ROW_ID 必须按 6B sys=3 占位**（曾误当 7B 导致偏移错位）
- **已验证修复的解码 Bug**：
  - DECIMAL 小数段 fx（非整 9 位组）：C 曾对 frac 补零到 9 位导致放大 10^7 倍，
    正确语义为 `unscaled = intg*10^scale + fv`（fv 直接是 fx 位原始值，不再补零）
  - DECIMAL i0==0 时 vint 已是完整 ix 位整数，曾误补零到 9 位
  - 布局若不占位系统列，记录 offsets 整体错位（后续字段全乱）——必须先 SDI 取全序再输出时跳过
  - **DATETIME2/TIMESTAMP2 小数秒缩放**：对照 MySQL `my_datetime_packed_to_binary`
    （mysys/my_time.cc），frac 存储按 fsp 压缩：dec1/2(1B)=微秒/10000、
    dec3/4(2B)=微秒/**100**、dec5/6(3B)=微秒原值。解码需反向缩放，否则 fsp<5 值放大/错位
  - **TIME2 解码**：int3 = `TIMEF_INT_OFS(0x800000)` + hms 位域（`hour<<12|min<<6|sec`），
    非纯秒数；frac 缩放同 DATETIME。**负值**：intpart 反码 + frac 反向补码
    （fsp1/2: `0x100-fraw`、fsp3/4: `0x10000-fraw`、fsp5/6: `0x1000000-fraw`），
    且整秒需 `intpart+1` 借位。曾误把 TIME2 当纯微秒导致 -1s/-0.001 差值与符号错乱

## 结论
MySQL 侧物理直读 → Parquet 全链路正确（1M 行聚合 8 项与 SQL 完全一致），
吞吐 ~936K rows/s（ZSTD）。InnoDB 页/记录格式逆向完成，解析器可复跑。

## 产物
- build/mysqlbin（主工具，.ibd → parquet + JSON 指标）
- src/mysql/mysql_parse_pages.c（InnoDB 叶页记录解析）、src/mysql/mysqlbin.cpp（Arrow 写出）
- scripts/build_mysqlbin.sh（构建）
- bench/gen_mysql.py（数据生成，1M + boundary）
- tools/dump_ibd.c（页类型统计/页头）、tools/hexpage.c、tools/trav2.c（记录链验证）
- evidence/mysql/poc_orders.parquet（本产物）、evidence/mysql/poc_orders.ibd、poc_boundary.ibd、poc_nopk.ibd、poc_compk.ibd、poc_dt.ibd（快照）
- 本文件
