# T0308 — PG 转换覆盖 4B 头 varlena 与 TOAST 外置路径（研究 + 验证报告）

## 背景与问题

T0311 校验 POC 中，~2564B 的 payload 行在旧 pgbin 中被 `varlena_extended()`
跳过（仅登记不判值）。T0308 定位根因并完整实现两条解码路径：

1. **行内压缩 4B 头 varlena**（VARATT_IS_COMPRESSED）：T0311 的"TOAST 行"
   实为行内压缩（pglz），并非 external——`toast_tuple_target` 默认 2048B，
   仅对超过该阈值且压缩无法获益的取值才外置；
2. **TOAST external 指针**（VARATT_IS_EXTERNAL，1B 头 0x01 + varatt_external 16B）：
   需读 pg_toast_<oid> 表按 (chunk_id, chunk_seq) 拼接 chunk_data，
   external 若压缩再 pglz 解压。

## 关键实测结论（pg9.6 / pg11 / pg18.4 三容器原始字节对拍）

### external 头布局三版本一致（无版本分派）
```
varattrib_1b_e (2B): b[0]=0x01, b[1]=0x12 (VARTAG_ONDISK=18)
varatt_external(16B): rawsize(va_rawsize)@2, extinfo(va_extinfo)@6,
                      valueid(va_valueid)@10, toastrelid(va_toastrelid)@14
  extinfo 低 30 位 = extsize（已存 chunk 数据大小）
  extsize < rawsize-4  => external 是 pglz 压缩
```
实测（id%200==100/150 桶，70×/80×md5 拼接）：rawsize 2244/2564、extsize
2240/2560、cm=0（未压缩 external）。9.6/11 未见 va_toastidx 迹象。

### 行内压缩 4B 头（T0311 修正）
```
va_tcinfo@4 低 30 位 = 原始数据大小（不含 varlena 头）；数据在 vp+8
解压目标 = va_tcinfo & 0x3FFFFFFF
```
实测 id%200==0 桶（md5||x*2470，pg_column_size=76）：行内压缩，非 external。

### pglz 格式（PG18 源码移植，各版本一致）
- 控制字节每 8 位控制 8 个块；位 0=字面量（复制 1B）；位 1=回引 tag。
- tag：`len=(sp[0]&0x0f)+3`、`off=((sp[0]&0xf0)<<4)|sp[1]`、sp+=2；
  `len==18` 时追加 1 字节扩展长度；off∈[1,4095]、len∈[3,273]。
- 重叠复制用 off 加倍技巧（len>off 时）。
- **toast 压缩数据带 4B rawsize 前缀**（T0308 关键实测，PG9.6/11/18 一致）：
  外部压缩 chunk 数据 = `4B(rawsize 低 30 位 | PG18 高 2 位压缩方法, 0=pglz/1=lz4)`
  + pglz 流。9.6/11 无方法位（恒 0）。**解压须跳过前 4B**，解压目标 =
  前缀低 30 位（= external 头 rawsize-4）。行内压缩（4B 头）无此前缀
  （va_tcinfo 已存原始大小），实测 id%200==0 桶解压正常。
- PG18 压缩方法 ID（toast_compression.h）：TOAST_PGLZ=0、TOAST_LZ4=1；
  默认 default_toast_compression=pglz（实验容器），故三版本均为 pglz。

### external 压缩态实测（AC-2 闭合）
- 构造 id%200==50 桶（78×md5||repeat('x',2000)=4496B）：压缩后 ~2741B
  >toast_tuple_target(2048) 且 <rawsize-4 → external 压缩（pglz），三版本
  一致。pg_column_size=2719（<len 4496）。
- 解码：外部头 rawsize=4500（含 4B 头）、extsize=2741、method=0(pglz)；
  前缀 0x00001190=4496=rawsize-4 校验通过；pglz 解压得 4496B 全值。
- 三版本 verify 五维 PASS 中该桶 payload 逐字段全值一致，skipped_toast=0。

### TOAST 表 chunk
- chunk_id int4 + chunk_seq int4 + chunk_data bytea；按 (id,seq) 排序后
  拼接去 varlena 头即得完整值。pg_toast_load 全量 mmap 扫描可见元组。

## 实现变更

| 文件 | 变更 |
|---|---|
| src/pg/pg_heap_reader.c | 移植自包含 pglz_decompress；PgToast 结构；toast_decode（二分查 chunk）；decode_tuple 增加 toast 参数并实现行内压缩/external 解码（解压走 dscratch 缓冲）；pg_toast_load 扫描拼接；pg_parse_heap_range 透传 toast；#undef qsort（避免 port.h 宏替换为未链接的 pg_qsort） |
| src/pg/pgbin.cpp | `--toast=<heap>`（预加载 toast 表）、`--rows=N`（替代/兼容位置参数 max_rows）；dscratch 分配；统计输出 skipped_toast |
| bench/gen_toast.py | 三版本 poc_toast 灌数（id%200 形态分桶 + id%7==0 NULL）+ heap/toast/clog 固化 + to_char US 微秒 tsv 基准（cp -rT 避免 clog 目录嵌套） |
| bench/verify_consistency.py | 表泛化 `--table=`：列/类型以 information_schema 为准，动态规范化 SQL；移除 TOAST 白名单（全值参与对照）；表名标识符白名单；全 NULL 列 SUM 处理 |
| bench/mutate_consistency.py | 透传 `--table`；m09 泛化（任意列首个 NULL→空串） |

## 双轴审查修复（Blocking 全部收敛）
- pglz_decompress 目标缓冲前置校验（toast_decode/行内压缩分支：rawsize-4 /
  tcinfo 超 dscratch_cap 即拒绝，防堆溢出）。
- pg_toast_load chunk_data 头合法性防护（空/过短 varlena 头跳过，防 exhdr
  下溢后 memcpy 越界）；t_hoff 页边界校验（toast 表与主表）。
- verify：表名标识符白名单（防 SQL 注入）；聚合 SUM 全 NULL 列返回 NULL
  时按 0 处理（防 Decimal(None) 崩溃）。

## 范围与实现决策说明（规范轴收敛记录）
- pgbin 保留旧位置参数 `<max_rows>` 兼容层：T0301/T0311 既有脚本以位置参数
  调用，AC-3 统一为 `[--rows=]` 的同时保留兼容，避免破坏历史命令。
- verify `--pg-dsn` 由可选改为必填：表泛化后列名/序/类型必须从
  information_schema 获取（parquet 无法自证列语义），收紧行为已声明。
- external 头未按 PRD 假设做版本分支：三版本实测头布局一致（无 va_toastidx），
  统一解析；压缩判定用 `extsize < rawsize-4`（PG 官方 VARATT_EXTERNAL_IS_COMPRESSED
  同式），非 extinfo 高位标志。
- pglz_decompress 为手写等价实现（严格 bounds-check + 目标尺寸前置校验），
  未直接链接 third_party（该目录仅有部分 PG 源码）。

## 验证结果

### AC-1~4 灌数 + 转换 + 参数
- 三版本 poc_toast 各 10000 行：150 行 external 尺寸（50 行内压缩 2502B +
  50 external 2240B + 50 external 2560B）、1407 行 payload NULL、其余
  1B/4B 头常规。
- pgbin `--toast=` 解码：三版本 seen_total=10000、skipped_invisible/dead/
  toast 均 0。

### AC-5 三版本五维校验（verify_consistency.py --table poc_toast）
| 版本 | 行数 | 逐字段全值 | 聚合 | schema | 汇总 |
|---|---|---|---|---|---|
| 9.6 | 10000/10000 | PASS | PASS | PASS | 五维全 PASS |
| 11  | 10000/10000 | PASS | PASS | PASS | 五维全 PASS |
| 18  | 10000/10000 | PASS | PASS | PASS | 五维全 PASS |

TOAST 大字段（行内压缩 + external 未压缩）逐字段全值一致。

### AC-6 mutation 12/12（三版本）
- 基线（未变异）verify PASS；12 类变异（改值/NULL/时间精度/删行/重复/
  换列序/decimal 精度/bool 翻转/NULL↔空串/截断/跳号/尾随空格）全部被捕获。

### AC-7 回归
- T0311（poc_consistency 10 万行）：新 pgbin 重转后五维全 PASS +
  mutation 12/12。原 154 行"TOAST 仅登记"现全值一致（行内压缩解码）。
- T0301（poc_orders 100 万行 × 三版本）：新 pgbin 重转后逐字段全值一致
  （skipped_toast=0），无回归。

## 遗留与边界

- external 压缩态（extsize<rawsize-4）未在本次灌数中自然产生（md5 拼接
  不可压）；代码路径由 toast_decode 覆盖，建议后续用 repeat 大字段
  （>2KB 且可压）补一条压缩 external 证据。
- pglz 压缩方法位（va_tcinfo 高 2 位）仅 PG12+；9.6/11 无该位，本项目按
  低 30 位兼容。
- 多 chunk（单值 >~2KB 拆多 chunk）路径由 pg_toast_load 拼接覆盖；
  单值超过单 chunk 上限（2000B）的未单独构造证据，逻辑含于拼接实现。
