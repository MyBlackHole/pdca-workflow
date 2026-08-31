---
schema: pdca.asset/v1
id: ontology:domain/data-formats-t0301-pg-version-convert-test
type: domain
layer: Knowledge
status: active
summary: PG 多版本 heap+CLOG 物理直读→Parquet 转换（T0301 实测知识）
domain:
- ontology:domain/data-formats
relations:
  specializes:
  - ontology:domain/data-formats
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# PG 多版本 heap+CLOG 物理直读→Parquet 转换（T0301 实测知识）

## 核心事实（实测 pg9.6/pg11/pg18.4 三容器）

1. **heap 元组头布局各版本一致**（24B）：
   - xmin@0 / xmax@4 / cid(t_field3)@8 / ctid@12 / infomask2@18 / infomask@20 / t_hoff@22 / pad@23
   - null bitmap（t_bits）紧随头部（t_hoff 已计入）；数据区从 t_hoff 起。
   - **推翻二手推论**：旧说法"PG12 移除 t_xvac 使头 28B→24B"错误——t_xvac 与 t_cid
     同处 t_field3 union（4B），各版本 HeapTupleFields 均为 xmin/xmax/t_field3=12B。
2. **varlena 编码各版本一致（packed）**：
   - 1B 头最低位=1，长度=头>>1（≤127B 含头）
   - 4B 头低 2 位=00（未压缩）/10（压缩），长度=(va_header>>2)&0x3FFFFFFF
   - 1B 头=0x01（external）为 TOAST 指针；压缩/外置跳过判定可用 PG18 宏通用。
   - **推翻二手推论**：旧说法"PG13- 老格式（1B 头最高位=0 长度=头&0x7F）"无实例支撑；
     PG9.6/11 数据 1B 头 0xA3→81B、4B 头 0x00000330>>2=204B 均按 packed 解析。
3. **CLOG 唯一版本差异为目录名**：pg9.x 及更早 `pg_clog/`，PG10+ `pg_xact/`；
   SLRU 段（32 页/段）与 2-bit xid 状态编码一致，读取器同一（目录参数化）。

## 实测验证方法（可复用）

- **头布局**：三容器 `heap_page_items(get_raw_page('tbl',0))` 查 t_hoff/t_infomask/t_infomask2
  （均 t_hoff=24、t_infomask=2306 证明布局一致）。
- **varlena 格式**：对目标版本建临时表插入 >127B 文本，提取 relfilenode heap，
  解析 4B 头 `>>2` vs `&0x3FFFFFFF` 判格式；1B 头用 `0x51`（老，81B 直接存）vs
  `0xA3`（packed，81B 移位）判别。
- **对照流程**：容器 CHECKPOINT 后提取 heap+CLOG（CLOG 必须与 heap 同快照）→
  转换 → SQL 基准（UTC 格式化 to_char(...,'YYYY-MM-DD HH24:MI:SS.US')）→ 按 id
  排序逐字段对照（物理页序≠主键序）。

## 坑与教训

- **版本号紧凑化陷阱**：`atoi("96")=96 > atoi("11")=11`，用数字判断版本先后会误判
  （PG9.6 被当 12PLUS 曾产生"假成功"）。规范输入或解析字符串，勿裸比数字。
- **布局常量**：集中在版本矩阵文件（pg_versions.h）并标注实测来源，禁止硬编码旧偏移。
- **对齐规则**：varlena 列用字节探测（PG att_align_pointer 语义），非 varlena 列数学对齐。
- **4B 头 varlena 与 TOAST**：正式对照数据若全为 1B 头短值，4B 头/TOAST 路径需另行
  单点实测（本任务仅 PG11 临时表 200B 文本实测）。

## 工具

- `bench/gen_pg_versions.py`（灌数）、`bench/extract_version_pg.sh`（提取）、
  `bench/verify_version_convert.py`（全量对照）、`src/pg/pgbin`（--pg-version 标注源版本，
  位置参数 `<heap> <clog_dir> <out> <rows>`）。