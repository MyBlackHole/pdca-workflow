---
schema: pdca.asset/v1
id: T0311-0818-pg-consistency-poc
phase: check
source_ids: ["t0311-gen-script", "t0311-convert-parquet", "t0311-verify-script", "t0311-mutate-script", "t0311-research-report", "t0311-src-heap-reader", "t0311-src-pgbin", "t0311-src-pg-versions", "convergence-map"]
---

## 上下文

对 PG 转换（heap+CLOG→Parquet）的"全面数据一致性校验方法"做完备性验证（POC）：
合成宽表 poc_consistency（10 万行，NULL 三形态/空串/空白/中文 emoji/480B 4B 头
varlena/2564B TOAST/数值与时间边界），pgbin 自解码转换，五维校验
（行数/逐字段/聚合/schema 元数据/类型语义），12 类 mutation 注入验证捕获率。
场景：research。数据：PG18 容器 t0216-pg，库 poct25。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 合成表覆盖 NULL 三形态 + 文本/数值/时间边界，灌数成功 | **成立**：10 万行；分布 cid=5263/amt=4347/ts=3448/st=14285/pl=7692/act=5882 NULL，long4b=923、toast=200、空串/空白/中文 emoji 覆盖 |
| pgbin 转换成功生成 parquet | **成立**（修复后）：100000 行，TOAST 50 行跳过，rows=100000 |
| 五维校验全部 PASS | **成立**：行数一致、10 万×7 列逐字段全一致（TOAST 200 行仅登记）、聚合 13 项全一致（sum=9847668592.51）、schema 7 列映射全 PASS、类型语义规范化一致 |
| mutation ≥10 种注入，捕获率 100% | **成立**：12/12 全捕获（改值/值→NULL/时间精度/删行/重复行/换列序/decimal 精度/bool 翻转/NULL↔空串/payload 截断/id 错位/尾随空格）；基线未变异 PASS |
| T0301 回归不受修复影响 | **成立**：9.6/11/18 三版本 verify_version_convert.py 全 PASS |

## 分析

- **AC 判定**：
  - AC-1（合成表形态覆盖+灌数成功）**PASS**：gen_consistency.py，SQL count=100,000
  - AC-2（pgbin 转换成功，parquet 生成）**PASS**：poc_consistency.parquet（rows=100000）
  - AC-3（五维校验全 PASS）**PASS**：verify_consistency.py 五维全 PASS
  - AC-4（mutation ≥10 种，捕获率 100%）**PASS**：mutate_consistency.py 12/12
  - AC-5（评估结论入 evidence）**PASS**：research-report.md（盲区清单+固化建议）
- **关键发现（T0301 校验盲区实锤 + 3 缺陷）**：
  1. **缺陷#1a nullbit 判定反转**：PG null bitmap bit=1=非空，pgbin 原 `if (nullbit) continue`
     把非空当 NULL。T0301 无 NULL 数据故全量 PASS 是假象。
  2. **缺陷#1b t_bits 偏移**：`offsetof(HeapTupleHeaderData, t_bits)=23`，原宏
     PG_HEAP_HEADER_SIZE=24 多移 1 字节，bitmap 读到数据区首字节。pageinspect 实测
     复核 t_bits 字节。
  3. **缺陷#2 NULL 语义丢失**：pgbin 写 parquet 时 Arrow validity buffer 全为
     `nullptr,0`，NULL 变空串/0/0.00/false。
  4. **缺陷#3 未初始化 UB**：NULL 列直接 continue，cols 数组（new[]）读垃圾，触发
     SIGFPE（`__divti3`）。
  - 修复后：含 NULL 转换正确（NULL 计数与灌数精确一致），T0301 三版本回归 PASS。
- **校验方法结论**：五维校验对好数据 PASS、对 12 类注入错误 100% 捕获，方法可信；
  TOAST 值对照与类型全集为已知盲区（建议 3，供 T0308）。
- **偏离 PRD 记录**：PRD 原写"不修改 src/pg 解码逻辑"，POC 发现 3 缺陷后经用户
  确认（clarifications 选项 A）修复 src/pg 三个文件，属 bug 修复而非范围扩展。
- **性能**：非 AC 验收项（无记录）。

## 失败原因

（无 rejected/partial；全部 AC PASS。缺陷修复属 POC 产出而非失败。）

## 适用边界

- 适用：PG18 合成宽表形态（含 NULL/空串/多字节/4B 头 varlena）下五维校验 + mutation
  基线（12 类，捕获率须 100%）。
- 边界：
  - TOAST（2KB+）为登记不判值（T0308 需实现值对照）。
  - 类型全集（float/uuid/json/bytea 等）不在 pgbin 列集，schema 维度仅覆盖 7 列映射。
  - 单版本（PG18）；NULL 行为跨版本（9.6/11）建议 T0308 用校验基线回归。
  - 校验方法与转换器共享 varlena 头/布局假设，共享假设类错误仍需独立权威源交叉复核。