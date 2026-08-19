---
schema: pdca.asset/v1
id: T0308-0818-pg-varlena-toast-followup
phase: check
source_ids: [gen-toast-script, pgbin-source, pg-heap-source, verify-script, mutate-script, research-report, review-report, verify-18, verify-11, verify-96, mutate-18, mutate-11, mutate-96, lz4-verify, regress-T0311, regress-T0301-96, regress-T0301-11, regress-T0301-18]
---

## 上下文
T0308（T0301 后续）目标：闭合 PG 物理直读（pgbin）对 4B 头 varlena 与 TOAST 外置路径的覆盖盲区。三版本（9.6/11/18）各灌 poc_toast（10000 行，含多形态 TOAST 分桶 + NULL），pgbin 新增 `--toast=<heap>` 完整解码（行内压缩/external 压缩+未压缩），verify 泛化 `--table=`，五维 + mutation + T0301/T0311 回归。development 场景。

## 假设与结果
- 假设 A：external 头布局三版本一致（无版本差异）→ 成立（PG9.6/11/18 实测 rawsize@2/extinfo@6/valueid@10/toastrelid@14 一致）。
- 假设 B：压缩判定可用 `extsize < rawsize-4`（PG 官方 `VARATT_EXTERNAL_IS_COMPRESSED` 同式）→ 成立。
- 假设 C：toast 压缩数据为纯 pglz 流 → **被实测推翻**：压缩数据带 4B rawsize 前缀（pglz/lz4 均如此，9.6/11/18 一致），解压须跳过前 4B。此为 T0308 关键发现。
- 假设 D：PG18 仅默认 pglz、lz4 列不在范围 → **用户决策本次一并实现**：LZ4 raw block 有界解压接入（external 前缀与行内 tcinfo 高 2 位分派），全形态实测通过。

## 分析
- 实现：pg_heap_reader.c 移植 pglz_decompress + 手写 lz4_decompress_block（均带边界/目标尺寸前置校验）；PgToast 全流程（mmap 扫描 toast heap→chunk_id 二分→seq 排序拼接→按需解压）；decode_tuple 行内/external 解码（dscratch 缓冲）；pgbin 参数 `--toast=/--rows=/--pg-version=`（移除位置参数 max_rows 兼容层）。
- 数据：gen_toast.py 构造 id%200 形态分桶（行内未压缩 480B / 行内压缩 2502B / external 压缩 4496B / external 未压缩 2240·2560B / id%7==0 约 1400 NULL）。
- 验证：三版本 10000 行五维全 PASS（TOAST 值逐字段对照，skipped_toast=0）+ mutation 12/12；lz4 列 t_cmp7 全形态五维 PASS；T0311（10 万行）与 T0301（100 万×3）回归全 PASS。
- 审查：双轴审查 Blocking 3 条（解压缓冲前置校验 / chunk 头长度防护 / t_hoff 页界）全部修复，Blocking=0 通过门禁。

## 逐条 AC 判定
- AC-1（三版本基准齐全）：PASS — gen-toast-script（evidence）+ verify 全值对照佐证
- AC-2（--toast 解码压缩+未压缩，无崩溃）：PASS — pg-heap-source/pgbin-source + verify/lz4-verify 全形态，skipped_toast=0
- AC-3（参数统一 --rows=/--pg-version=）：PASS — pgbin-source（兼容层已移除，严格位置参数 3 个）
- AC-4（verify 泛化 --table= 去硬编码/白名单）：PASS — verify-script
- AC-5（三版本五维全 PASS）：PASS — verify-18/11/96
- AC-6（mutation 12/12）：PASS — mutate-18/11/96
- AC-7（T0301/T0311 回归）：PASS — regress-T0311 + regress-T0301-96/11/18
- AC-8（evidence 登记 + research-report external 头跨版本实测）：PASS — research-report + 登记清单

## 失败原因（仅 rejected/partial）
（无）

## 适用边界
- pgbin 假定 poc_orders 同构 7 列布局（id int8 等）；验证表须同构，否则列错位。
- 灌数导出须单独 `CHECKPOINT`（`psql -c "INSERT; CHECKPOINT;"` 同串共享隐式事务导致 CLOG 未落盘 → 全 invisible）。
- 压缩方法位仅支持 PG18 枚举 pglz=0/lz4=1；更早版本无 lz4；PG18 默认 default_toast_compression=pglz。
- verify 需 `--pg-dsn`（列语义取自 information_schema）。

## 下一轮建议
- 如需支持任意表 schema，需将 pgbin 列布局改为元数据驱动（attrelid→attlen/attalign/atttypmod）。
- 大表场景可评估 toast 表 mmap 全扫描的 IO 成本（当前 1M 行级 20ms 级，无压测需求）。
