# E5 根因与修复记录（NULL/类型边界实证）

## 结论修正（重要）
早期结论"NULL 位图未生效（heap_deform_tuple 依赖 t_infomask）"为**误判**。
真相：`heap_deform_tuple`（PG18 官方代码）**一直解析正确**，
错误在 pgbin 自身的后续处理环节。经 PG17/18 源码对比确认：
- `att_isnull`（PG17=PG18）：bitmap 位=0-based 列索引，**1=非空、0=NULL**
  （tupmacs.h 注释 "a 0 in the null bitmap indicates a null, while 1 indicates non-null"）
- `HeapTupleHeaderGetNatts = t_infomask2 & 0x7FF`（PG17=PG18，无移位）
- 早期"infomask2=0x7 与 natts=7 需查"疑问：**0x7 & 0x7FF = 7 正确**，无异常

## 实际根因（pgbin 自身 5 个 bug，全部修复）
1. **文本 offset 组装错位**（main.cpp）：status/payload 的 offset 数组在 append
   **之后**记录 `text_blob.size()`——空串 append 0 字节不改变 size，但 size 已含
   前面循环的累积 → 空串被读成 [0,13)（读到全部 status 内容 'paidclosednew'）。
   修复：**先 push 当前 size 再 append**。
2. **无 NULL 语义**：早期 NULL 列被写成 0/false/epoch。修复：C 端新增
   `nullmask[row]`（bit0-6），main 端生成每列 validity bitmap + null_count。
3. **Arrow validity bitmap 方向**：Arrow 的 null bitmap 语义是 **1=有效、0=null**
   （array_base.h `IsNull() = !IsValid()`，IsValid 读 bit，1=有效）。
   初始实现按"1=null"置位 → 全部反转。修复：非 NULL 列置位、NULL 列清零。
4. **时间戳哨兵/溢出**（真实类型难点）：PG 哨兵 `DT_NOEND=INT64_MAX`（+infinity）、
   `DT_NOBEGIN=INT64_MIN`（-infinity）；合法极值（如 294276-12-31）加上
   946684800s 的 epoch 偏移后**溢出 int64** → 回绕成 290279 BC 假值。
   修复：哨兵/溢出检测 → 标 NULL + 错误计数（本实证 2 个：infinity + 294276-12-31）。
   PG 有限下界 4713-01-01 BC 转换正常（-210866760000000000 + delta 不溢出）。
5. **active 列布局**：C 端每行 1 字节 vs BooleanArray 要求 bit-packed。
   修复：C 端写 `actives[row >> 3] |= 1 << (row & 7)`，分配 (batch+7)/8。

## E5 最终验证（e5_clean.parquet，5 行 edge 表）
| id | customer | amount | created_at | status | payload | active |
|----|----------|--------|-----------|--------|---------|--------|
| 1  | NULL     | NULL   | NULL      | NULL   | NULL    | NULL   |
| 2  | 0        | 0.00   | epoch     | ''     | ''      | false  |
| 3  | 2147483647 | 9999999999.99 | **NULL**(infinity 溢出) | paid | x | **true** |
| 4  | -2147483648 | -9999999999.99 | 4713-01-01 BC ✓ | closed | y×100 | **true** |
| 5  | 1        | 0.01   | **NULL**(294276 溢出) | new | NULL | false  |

ERRORS=2（两个时间戳溢出被正确检测为 NULL）。行 3/4 的 active=true 正确（bit-packed 修复）。

## 回归验证
- E1（poc_orders_e1_heap 1M）：1000000 行、updated=200000、distinct id=1M、
  0 个 NULL、吞吐 116 万行/s——**无回归**。
- E2（t7_heap TOAST 表）：status='new' 正常（组装 bug 修复生效），
  payload 仍为 TOAST 指针二进制（\x12\x84\x0C...）→ 非法 UTF8 → DuckDB
  报 Invalid string encoding——**TOAST 静默损坏难点复现确认（与组装 bug 无关）**。
