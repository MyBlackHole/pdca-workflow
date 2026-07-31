# Triage Brief — T0165

- **分类**: enhancement / research（延续 T0163 pg-mysql-parquet-poc 的物理路径调研）
- **需求**: 数据文件直接转换（物理路径）的难点清单 + Parquet 按索引有序写入的改动评估
- **查重**: 已归档 T0150（Parquet 格式调研）、T0163（六路径性能 POC，知识已沉淀 2 篇）——本任务聚焦"物理路径工程化难点"与"有序输出"，不重复性能基准
- **事实核查**:
  - poc_orders_big（1 亿行）无索引；heap 13.6GB 文件在 /home/.trials100m/（磁盘剩 26G）
  - pgbin 批处理版可用（/tmp/opencode/pgfiledump-test/），支持 heap→parquet 顺序流式
  - 当前可见性判断为启发式（HEAP_XMAX_INVALID+HEAP_UPDATED），无 PG 服务时无法读 pg_xact 精确判定
  - 现有数据 payload 64B，未触发 TOAST 阈值（2KB）
- **关键未知（需 P1/P2 决策）**: 难点实证深度、有序写入方案范围（排序/分片/btree 直读）、数据规模、排序键类型
