# POC：PG 转换全面数据一致性校验方法完备性验证（T0301 后续）

## 问题

T0301（PG 9.6/11/18）与 T0300（MySQL 4 版本）的转换对照均基于 poc_orders 单表：仅
7 列（bigint/int/numeric/varchar/timestamp/boolean/varchar），数据形态单一（无 NULL、
无空串、无超长文本、无复杂类型）。现有校验方法是"全量逐字段字符串规范化对照 +
行数 + 聚合"三路验证，但：

1. 校验盲区未被系统评估——对数值精度、时间微秒/时区、NULL/空串与空值语义、列顺序、
   schema 类型元数据等维度的覆盖是隐式的；
2. 对照脚本本身从未被"反向验证"——它是否真的能捕获转换错误（包括被注入的错误），
   尚无证据。若校验方法存在盲区，后续任务（T0308 的 4B 头/TOAST 扩展、多版本回归）
   的对照结论都不可信。

## 方案

1. 合成表 `poc_consistency`（PG18 容器 t0216-pg），复用 pgbin 支持的 7 列结构（int8
   id / int4 customer_id / numeric(12,2) amount / timestamp created_at / text status /
   text payload / bool active），但在**值形态**上做足（POC 聚焦校验方法的形态盲区，
   类型全集转换能力不在本任务，见"范围外"）：
   - NULL 三形态：全 NULL 列、部分 NULL 列、稀疏 NULL 列（仅 id 与活跃键非 NULL）
   - 文本形态：空串、全空白、多字节（中文/emoji）、超长 payload（>127B 触发 4B 头
     varlena；>2KB 触发 TOAST 仅登记不判错，属 T0308）
   - 数值形态：amount 边界（0/0.00/负/最大精度/舍入），customer_id 含 0 与负数
   - 时间形态：epoch、微秒边界（999999）、秒与跨日
   - bool/status 边界：全部 false、四态轮转含空
2. 复用 pgbin 自解码转换 → parquet。
3. 五维校验（`bench/verify_consistency.py`）：
   - 行数、逐字段差异、聚合（count/sum/avg/min/max）、schema 元数据（parquet schema
     vs pg_catalog 的列名/序/类型映射）、类型语义（numeric 精度、时间精度、NULL vs
     空串区分）
4. mutation 测试：对生成 parquet 注入错误（改值/改类型/删行/换列序/改精度/改 NULL
   语义/多行错位等 ≥10 种），逐一验证对照脚本 100% 捕获 → "校验方法可信"直接证据。

## 用户故事

作为转换管线消费者，我希望校验方法能确定性捕获一切转换错误（值/类型/schema/语义），
而不是"看起来对"，从而放心让 parquet 进入下游。

## 实现/测试决策

- research 场景：产出评估结论，不进入生产测试接缝（无 seam 要求）。
- 容器：单一 PG18（t0216-pg），校验方法验证不引入版本差异变量。
- 数据：合成宽表 ~10 万行（覆盖边界 + 快），灌数脚本 `bench/gen_consistency.py`。
- 校验工具：扩展/新建 `bench/verify_consistency.py`（基于 T0301 verify_version_convert.py
  的规范化对照内核）。
- 不修改 src/pg 解码逻辑（若发现真实转换缺陷，记录为 T0308 或新 bug 任务输入）。

## 范围外

- 4B 头 varlena/TOAST 正式对照（T0308；本任务仅登记超长形态并验证对照脚本能正确
  呈现差异面）。
- float4/float8/uuid/json/bytea/date/time/timestamptz 等 pgbin 未支持类型的转换对照
  （pgbin 列集硬编码 poc_orders 7 列；类型全集转换能力为后续任务）。
- PG 多版本差异校验（T0301 已覆盖）。
- 性能/吞吐测量。
- 在线数据一致性（WAL/复制）校验。

## 备注

- 产出：校验方法评估报告（盲区清单 + 固化建议）+ mutation 测试记录，决定 T0308 及
  后续回归的校验基线。
- 容器沿用 T0301 约束（test/test、库 poct25）。
- 决策记录：POC 用 pgbin 现有 7 列结构 + 形态丰富（不动 src/pg），见 clarifications。

## 验收标准

- [ ] AC-1: 合成表 poc_consistency 覆盖 NULL 三形态 + 空串/空白/多字节/超长文本 +
      数值边界 + 时间微秒边界，灌数成功
- [ ] AC-2: pgbin 转换成功，parquet 生成
- [ ] AC-3: 五维校验全部 PASS（行数/逐字段/聚合/schema 元数据/类型语义）
- [ ] AC-4: mutation 注入 ≥10 种错误，对照脚本捕获率 100%
- [ ] AC-5: 校验方法评估结论写入 evidence（盲区清单 + 校验基线固化建议）