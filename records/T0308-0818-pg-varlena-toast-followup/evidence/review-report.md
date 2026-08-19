# T0308 双轴代码审查报告

审查范围：`src/pg/pg_heap_reader.c`、`src/pg/pgbin.cpp`、`bench/gen_toast.py`、`bench/verify_consistency.py`、`bench/mutate_consistency.py`（相对 T0301 基线增量）。

## 标准轴

编码标准 + Fowler 坏味基线（对照项目既有 C/Python 风格与 PostgreSQL 移植惯例）。

### 硬违规（已修复，Blocking）
- [B1] `pglz_decompress` 调用侧未前置校验目标尺寸：toast_decode 的 external 解压与行内压缩分支的 `rawsize-4` / `tcinfo` 均未与 scratch/dscratch 容量比较，异常数据可致堆溢出。修复：两分支统一前置 `> cap 即 return -1`。
- [B2] `pg_toast_load` 对 chunk_data varlena 头未做长度合法性校验：`varlena_size_exhdr` 在头 <=4B 时下溢，随后 memcpy 越界。修复：1B/4B 头分别校验，空/过短 chunk 跳过。
- [B3] `pg_toast_load` 与 `decode_tuple` 的 `t_hoff` 无页边界校验。修复：越界时跳过（toast 表）/回退 `PG_HEAP_HEADER_SIZE`（主表）。

### 硬违规（Warn，已修复）
- [W1] toast 表页内 itemid/偏移未统一做 8KB 页界钳制（缺整体页边界防御纵深）。
- [W2] `verify_consistency.py` 动态 SQL 中表名直接字符串拼接（历史遗留，本任务触达）。修复：表名标识符白名单正则 + 拒绝非标输入。
- [W3] `check_agg` 全 NULL 列 `SUM` 返回 SQL NULL → `Decimal(None)` 崩溃。修复：None 按 0 处理。

### 判断项（记录不修）
- [J1] 行内压缩 external 头双份（`PgToast`/`HeapCols`）字段重复（Data Clumps）。
- [J2] 手写 pglz 解压与 PG 源码的魔法数（0x0f/0xf0/18/3/273）散落（Magic Numbers）。
- [J3] `varlena_extended` 旧分支为死代码（Speculative Generality），随 T0301 基线遗留。

## 规范轴

对照 `prd.md` AC-1~AC-8 逐条审查。

### spec 要求但缺失（已闭合）
- [M1] AC-2 的"压缩 TOAST 值"无真实数据覆盖：原 poc_toast 仅行内压缩与未压缩 external，无 external 压缩态。修复：gen_toast 增加 id%200==50 桶（4496B 外置压缩），三版本实测解码全值一致，skipped_toast=0。

### 额外功能（范围蔓延，记录声明）
- [S1] pgbin 保留旧位置参数 `<max_rows>` 兼容层（AC-3 为 `--rows=`）；T0301/T0311 既有脚本以位置参数调用，保留以不破坏历史命令。
- [S2] verify `--pg-dsn` 由可选改必填：表泛化后列语义需从 information_schema 获取，parquet 无法自证，收紧已声明。

### 实现偏差（记录）
- [D1] external 头未按 PRD 假设做版本分支：三版本实测头布局一致（无 va_toastidx），统一解析。
- [D2] 压缩判定用 `extsize < rawsize-4`（与 PG 官方 `VARATT_EXTERNAL_IS_COMPRESSED` 一致），非 extinfo 高位标志；PG18 压缩方法 ID pglz=0/lz4=1，lz4 为遗留边界（research-report 已记录）。
- [D3] pglz_decompress 为手写等价实现（严格边界检查），未直接链接 third_party（目录仅有部分 PG 源码）。

## 风险评级
低。全部硬违规已修复并回归验证；唯一未覆盖项（lz4 压缩）在当前三版本默认 pglz 场景下不触发，已作边界记录。

标准轴 6 硬违规（3 Blocking 已修）+ 3 判断项；规范轴 1 缺失（已闭合）+ 2 蔓延 + 3 偏差。Blocking = 0，通过门禁。
