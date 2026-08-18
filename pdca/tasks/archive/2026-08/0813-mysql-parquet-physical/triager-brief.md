# Triage Brief — T0250 调研 MySQL、PG 数据文件直接转换 Parquet

> 日期：2026-08-13 | 分类：enhancement | scenario_type：research | 状态：ready-to-plan（待 Grill）

## 1. 需求原文

> 走 PDCA 流程：调研 mysql、pg 数据文件直接转换成 Parquet。

## 2. 分类

- 类别：`enhancement`（新调研）
- `scenario_type`：`research`

## 3. Claim 验证与查重（关键）

| 已有资产 | 覆盖内容 | 与本需求关系 |
|---|---|---|
| T0163（归档，2026-07-31） | PG 逻辑导出+六路径性能对照，含 **pg_filedump 物理直读**、**C++ 官方源码 heap 直读**（1 亿行 74.7s / RSS 403MiB） | **PG 物理路径已深度实证**，本需求 PG 侧应**复用不重做**；其明确记录"MySQL 实测取消"决策缺口 |
| T0165（active，do 阶段，PG 难点+btree 有序枚举） | PG 数据文件直接转换难点矩阵 + btree 叶链有序枚举 | PG 侧继续深化中，尚未完成 |
| `knowledge/data-formats/pg-to-parquet-path-benchmark.md` | PG→Parquet 六路径实测对照 | 复用为 PG 侧基线 |
| `knowledge/data-formats/pg-heap-physical-read-notes.md` | PG heap 物理直读工程要点 | 复用为 PG 侧工程经验 |
| `knowledge/backup/xtrabackup-incremental-schemes.md` | MySQL 物理备份（InnoDB 页 LSN/位图） | 仅备份视角，**非转换** |
| `parquet-technical-reference.md`（T0150） | Parquet 格式/编码/类型映射 | 通用基础 |

**关键缺口确认**：
- **MySQL 数据文件（InnoDB .ibd / 表空间）直接解析 → Parquet：完全空白**。
- T0163 归档时 MySQL 实测取消，`mysql_poc.py` 仅写了逻辑路径（pymysql 流式）未实测；`mysqlsh util.exportTable` 原生 Parquet 记为决策缺口。

## 4. 信息缺口（进入 Grill）

1. **范围**：MySQL 为主补缺口 + PG 侧引用已有结论？还是 PG+MySQL 全量重研？（推荐前者，避免与 T0163/T0165 重复）
2. **"数据文件直接转换"边界**：严格 InnoDB 物理文件解析（.ibd 页/B+树/记录格式）？还是含逻辑层工具（mysqlsh / mysqldump / binlog→CDC）？（推荐严格物理，与 PG 物理路径对齐）
3. **深度**：纯文档调研（可行性+方案+风险矩阵）还是含实测 PoC？（InnoDB 物理解析工程量远超 PG，推荐文档调研为主 + 关键路径小规模实测）
4. **交付物**：调研报告 + knowledge 沉淀；是否含原型代码 / 对现有 pgbin 工具的改造？

## 5. 推荐下一步

- P1/P2 Grill 澄清上述 4 项 → 方向确认 → P3 PRD → P6 终审 → plan→do。