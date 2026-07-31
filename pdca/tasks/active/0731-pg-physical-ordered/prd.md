# PRD — T0165 数据文件直接转换难点调研与 btree 有序枚举

## 1. 问题陈述

T0163 已验证 PG 物理路径（heap 文件直读 → Parquet，pgbin）可行且性能占优（1 亿行 74.7s / RSS 403 MiB）。但工程化落地仍有两大未知：

1. **难点清单无实证**：物理直读涉及 MVCC 可见性、TOAST、块校验和、页空洞乱序、多段文件、类型解码、一致性等风险，当前仅硬编码 7 列表模型 + 启发式可见性，未在"非理想数据"（大值列/死元组/空洞）上验证。
2. **有序输出无方案**：heap 为插入序，Parquet 若要求按索引键有序（利于范围查询/聚簇对齐），物理路径如何低成本产出。用户决策：**btree 索引叶链有序枚举 + TID 回表**（不依赖排序）。

## 2. 目标与验收标准

### AC-1 难点矩阵（实证）
≥8 项难点，每项含：机制说明、实证结果（实验复现）、对现有 pgbin 的风险等级、工程化应对。至少覆盖：
- MVCC 可见性精度（UPDATE 造死元组 → 启发式判断 vs PG count 对照；VACUUM 前后差异）
- TOAST 列（造 3KB 大值 → heap 内 TOAST 指针识别，物理路径缺失 pg_toast 文件的行为）
- 块校验和（检查现有页 pd_checksum 状态，校验和不开启时物理路径的风险说明）
- 物理顺序 ≠ 逻辑顺序（删除造空洞 → 乱序度量化）
- 多段文件（>1GB 已实证，补入矩阵）
- 类型解码全集（现有 7 列已覆盖 int64/int32/numeric/timestamp/text/bool，补充 NULL/空串/极值边界）
- 静态一致性（CHECKPOINT 前置条件、崩溃恢复场景）
- schema 元数据直读（无服务时表结构来源，pg_catalog 直读评估）

**Pass 标准**：矩阵 ≥8 项；≥5 项有实证实验数据支撑；每项有风险等级与应对。

### AC-2 btree 有序枚举实现（1M 表）
- 为 poc_orders（1M 行）建 4 个索引：`(id)` int64、`(status)` TEXT、`(amount)` NUMERIC、`(created_at)` TIMESTAMP（非唯一，模拟普通索引）。
- 实现 btree 直读：metapage→root→内部页→叶链（btpo_next），IndexTuple 键解析（null bitmap/定长/变长），TID 回表 heap 复用现有 deform 组装。
- 四种键各输出 Parquet：
  - **有序性**：输出行相邻键单调（类型化比较器，100% 通过）
  - **行数**：与 PG `SELECT count(*)` 一致（索引可见行=表可见行）
  - **抽样**：首/中/尾行键值与 PG ORDER BY 抽查一致
  - NULL/死元组处理：跳过 LP_DEAD/LP_UNUSED 索引元组与不可见行，行为记录

**Pass 标准**：四索引全部满足有序性 100%、行数一致、抽样匹配。

### AC-3 性能对照（1M）
| 路径 | 端到端 | 峰值 RSS |
|---|---|---|
| 物理顺序直读（现有 pgbin 基线） | — | — |
| btree 有序枚举（四种键，各计时） | — | — |
| SQL 对照：D2 `ORDER BY id/status/amount/created_at` 直转 | — | — |

**Pass 标准**：三路径各 ≥1 次计时；btree 直读 vs 物理顺序的额外开销量化（秒与倍数）；D2 ORDER BY 对照列明确标注 PG 服务端排序成本。

### AC-4 改动清单
现有 pgbin → 支持 btree 有序枚举的改动点：新增/修改文件、函数、数据流、复杂度评估（含多段索引文件、NULLS FIRST/LAST、复合键扩展路径）。

**Pass 标准**：清单覆盖全部改动点，标注每个点的复杂度（S/M/L）与风险。

## 验收标准

- [ ] AC-1 难点矩阵 ≥8 项，≥5 项实证数据支撑，每项有风险等级与应对
- [ ] AC-2 四索引 btree 有序枚举：有序性 100%、行数一致、抽样匹配
- [ ] AC-3 三路径各 ≥1 次计时，btree 直读 vs 物理顺序开销量化，D2 对照标注
- [ ] AC-4 改动清单覆盖全部改动点，标注复杂度（S/M/L）与风险

## 3. 方案设计

### 3.1 难点实证实验（5 个）
| # | 实验 | 操作 | 验证点 |
|---|---|---|---|
| E1 | 死元组 | `UPDATE poc_orders SET status='x' WHERE id<=200000`（20 万行）→ 不 VACUUM 跑 pgbin | count vs PG；启发式可见性漏读/多读数 |
| E2 | TOAST | 建 `poc_orders_toast` 表（payload TEXT 3KB）×1000 行 → pgbin | TOAST 指针识别（EXTERNAL/EXTENDED），缺 pg_toast 文件时的行为（垃圾/失败） |
| E3 | checksum | `pg_controldata`/页头检查 pd_checksum；若库未开 checksum 则说明风险+登记验证方法 | 页头 checksum 位状态 |
| E4 | 空洞乱序 | E1 后删除 5 万行 → 物理顺序 id 乱序度（相邻差分布） | 乱序量化 |
| E5 | 类型边界 | 插入含 NULL/空串/amount 极大极小值行 → pgbin | 解码正确性对照 |

E1 与 E4 复用同一表演变；E1 的 UPDATE 不影响 E2 独立表；E4 删除后 E1 对照需在删除前完成或复核（顺序：先 E1 后 E4，避免删除干扰 count 对照；E5 独立造 10 行小表）。

### 3.2 btree 直读设计
- **输入**：heap 文件 + 索引文件（含多段）+ 索引 attno/类型描述（CLI 参数化，非 pg_catalog 直读——schema 直读仅矩阵评估）。
- **页结构**：0 页 BTREE_METAPAGE（btm_root/btm_level/btm_fastroot 仅参考，从 root 沿最左指针 descend 到叶）；叶页 `P_ISLEAF`，`btpo_next` 右兄弟；ItemId 数组有序；IndexTuple：`ItemPointerData t_tid`（回表）+ `t_info`（INDEX_ALT_TID_MASK 等标志）+ 键数据（定长按 attlen/attalign 顺序 + 变长 varlena，首位含 null bitmap 与 hasnulls 标志）。
- **回表**：TID blockno（若带 relblockno 高位 32 位→多段定位）+ offnum → heap 页 PageGetItem → 复用 `pg_parse_heap_range` 的 deform 组装逻辑（重构为"按 TID 取行"函数）。
- **可见性**：回表行沿用现有启发式（HEAP_XMAX_INVALID+HEAP_UPDATED）+ 索引元组 LP_DEAD/LP_UNUSED 跳过；**索引行数可能 ≠ 表可见行数**（索引含未提交/死索引元组）→ AC-2 以 count 对照实测记录差异（预期：刚建索引无写入时一致）。
- **比较器**（有序性验证用）：int64 直接比较；TIMESTAMP int64；NUMERIC 用 decode_numeric 的 __int128（scale 对齐后）；TEXT 用 `strcoll`（与 PG 默认 locale 规则对齐，C locale 下退化为 memcmp 同序）。
- **NULL 处理**：btree NULL 默认排最后（asc）→ 输出尾部 NULL；比较器将 NULL 视为最大（asc）。
- **输出**：复用现有 Arrow 组装/写 Parquet 管道，按叶链顺序 WriteTable（row group 内+跨组全局有序）。

### 3.3 对照实验
D2 `COPY (SELECT * FROM postgres_scan_pushdown(...,'poc_orders') ORDER BY <key>) TO ...`（PG 服务端排序成本对照）+ 物理顺序基线（现有 pgbin）。

## 4. 范围外
- 1 亿行重跑（1M 决策）；外排/分片排序模式；TOAST 直读实现（仅识别与行为记录）；checksum 校验实现（若库未开启）；复合键索引；pg_catalog schema 直读实现；增量/CDC。

## 5. 风险
- btree 页结构解析工程量（预计 300-500 行 C）；PG 18 btree 细节（dedup 默认关、LP_DEAD 删除位）以实测页内容为准，发现偏离时记录并调整。
- 建索引+CHECKPOINT+拷贝：1M 表索引各 ~20-30MB，磁盘 26G 充足。
- 容器环境（podman host 网络，PG 55432）数据演变需小心：E1 UPDATE 影响 poc_orders——**btree 实验需在建索引后**；顺序：先 E1/E4（基于当前无索引表）→ 再建索引做 AC-2/AC-3 → E2/E5 独立表随时。

## 6. 产出
- 任务目录：难点矩阵（research-report.md 章节）、btree 直读源码（pg_btree_enum.c + main 改造）、复现手册、四键 Parquet 产物
- evidence：metrics JSON（AC-2/AC-3）、报告、manifest 登记
