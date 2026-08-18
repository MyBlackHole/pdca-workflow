# PG→Parquet 转换校验方法：五维校验 + mutation 基线

> 来源：T0311 POC（0818-pg-consistency-poc）。将 T0301 的"全量逐字段规范化对照 +
> 行数 + 聚合"三路扩展为五维，并用 mutation 注入反向验证灵敏度。结论：好数据
> 五维全 PASS、12 类注入 100% 捕获，方法可信。

## 方法（五维）

1. **行数**：parquet 行数 == SQL 基准行数。
2. **逐字段全值**：每行每列规范化文本对照（差异数 = 0）。规范化约定与 SQL 导出
   一致：NULL→`NULL` 文本、decimal→固定 2 位、timestamp→`%Y-%m-%d %H:%M:%S.%f`、
   bool→1/0。**NULL 与空串必须可区分**（用 `COALESCE(col::text,'NULL')` 导出）。
3. **聚合**：count / sum(amount) / count(distinct status) / active=true / id 范围 /
   各列 NULL 计数。
4. **schema 元数据**：parquet 列名+类型 vs pg_catalog（信息模式列名/序/类型映射）。
5. **类型语义**：decimal 精度、时间微秒、bool 值域、NULL vs 空串——由 2/3 维的
   规范化约定隐式覆盖，需在报告显式声明。

## mutation 注入（反向验证，捕获率须 100%）

对基准 tsv 逐一注入单类变异，校验脚本必须 FAIL。12 类样例：
改值 / 值→NULL / 时间精度丢失 / 删行 / 重复行 / 换列序 / decimal 精度 / bool 翻转 /
NULL↔空串 / 文本截断 / id 错位 / 尾随空格。

实现：`bench/verify_consistency.py`（五维）+ `bench/mutate_consistency.py`（注入 +
调用 verify 断言 FAIL）。parquet 读取用 duckdb（SQL 层规范化可保留 DECIMAL 精度，
勿经 pandas 转 float）。

## 已知盲区（T0311 实测暴露）

- **TOAST（2KB+ 字段）**：pgbin 按设计跳过，值为空串，只能登记行数不能判值——
  需在 T0308 实现值对照。
- **类型全集**（float/uuid/json/bytea 等）：pgbin 列集硬编码，schema 维度仅覆盖
  现有 7 列映射。
- **共享假设缺陷**：校验与转换器共享 varlena 头/布局假设，整体解读错误可能两边
  一致漏检——需独立权威源（pageinspect/源码 offsetof）交叉复核。

## 流程改进（默认做法）

转换/解析类任务默认用**合成表注入形态**（NULL/空串/多字节/边界值）而非复用旧数据
（T0301 全 NOT NULL 曾掩盖 3 个 NULL 缺陷）；校验脚本必须含 mutation 反向验证；
物理偏移常量用 offsetof/权威源复核。
