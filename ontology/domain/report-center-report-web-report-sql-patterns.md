---
schema: pdca.asset/v1
id: ontology:domain/report-center-report-web-report-sql-patterns
type: domain
layer: Knowledge
status: active
summary: report-web 固定报表 SQL 构建模式与坑位
domain:
- ontology:domain/report-center
relations:
  specializes:
  - ontology:domain/report-center
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# report-web 固定报表 SQL 构建模式与坑位

> 来源：T0220（报表模板注册表、16 套固定查询与 CSV/PDF 同步导出）Check 阶段实测。
> 适用：report-center 后续报表模板/查询/导出类任务（T0221~ 及更多固定报表）。

## 背景

固定报表模板通过「HandlerSpec 声明式 SQL 构造」产出固定参数化查询。模板运行期
按域/时间/枚举筛选动态拼 SQL，但**表、列、排序均固定于声明**，请求不注入。
该类「声明式 select 渲染」是报表模块核心模式，需规避以下三个实测坑。

## 坑 1：表别名子串误判（missing FROM-clause）

**现象**：聚合模板（如 backup_task_count_trend）构造筛选列时，`t` 别名被误选，
SQL 报 `missing FROM-clause entry for table "t"`。

**根因**：用 `prefix in from_sql` 子串判断形如 `t.` 的列别名是否存在。`"t" in
"agg_task_daily"` 为 True，误命中含字母 `t` 的表名，选中不存在别名 `t.task_type`。

**修复**：改为 `f"{prefix}." in from_sql`（「别名.」代点断言）做单词边界；对
同名前缀特例（如 `ds`）额外检查主表名 `dim_data_source`。

**复用法则**：
- 判断列是否存在时，用「`别名.`」而非「别名裸字符串」，避免子串误匹配任意列名/表名。
- 若多个候选列（如 `a.task_type` 与 `t.task_type`）用同一语义键，按 from_sql 中
  实际出现的别名顺序选第一个存在列。

## 坑 2：JOIN 多表域列歧义（ambiguous column）

**现象**：storage_worker_usage 等 JOIN 多表模板做域过滤时，
`WHERE backup_domain_id = ANY(...)` 报 `column reference "backup_domain_id" is ambiguous`。

**根因**：域过滤谓词默认裸列 `backup_domain_id`，多表 JOIN 出现同名列（域表、
维表、事实表均含）。

**修复**：为查询声明增加 `domain_col` 字段（默认 `"backup_domain_id"`），每个
JOIN 模板显式使用主体表别名（`a.`/`c.`/`ds.`/`po.`/`t.`），域谓词拼接该限定列。

**复用法**：
- 联合/JOIN 查询中所有**来自 WHERE 的隐式列引用**都必须限定表别名，不依赖同名
  默认列。
- 为每类模板声明「域列」元数据，聚合/维表/事实表分别规范化限定列。

## 坑 3：GROUP BY 常量字符串

**现象**：storage_capacity_trend 在 group_mode=overall 时
`GROUP BY date_trunc('day', c.stat_date), 'overall'` 报
`non-integer constant in GROUP BY`。

**根因**：SELECT 中的 `group_key` 是常量 `'overall'`，GROUP BY 把该常量字符串
当作一个分组列，PG 禁止按常量分组。

**修复**：GROUP BY 展开时若 group_key 表达式是常量（以 `'` 开头），跳过不加入
GROUP BY —— 常量分组无意义。

**复用法**：SELECT 里的常量派生列绝不可进 GROUP BY；用「是否以引号开头」判断
常量并过滤。趋势分组用 `date_trunc` 时间桶即可。

## 共识：导出与分页

- Keyset 分页（`(k1,k2) < (v1,v2)`）而非 OFFSET，多域用 K 路归并，禁全局 OFFSET。
- 固定页面/导出超时：页面查询 2s、导出 30s（独立连接池），避免慢查询占用读连接。
- CSV 按 keyset 小批读取，`max_rows+1` 探测截断并返回截断标志（而非无界全量）。
- 单进程用 `BoundedSemaphore` 配额（Query16/Export2/Metric2）；多实例需外部化。

## 验证建议

- 报表模板新增/修改时必须跑「全 16 套真实 PG 执行冒烟」（见
  `tests/test_all_templates_execute.py`），逐套在 seed fixture 可执行且返回结构。
- 对 SQL 构造函数补「SQL 片段级精确单测」（无 DB），锁定根因防回归
  （见 `tests/test_query_handlers_sql.py`）。