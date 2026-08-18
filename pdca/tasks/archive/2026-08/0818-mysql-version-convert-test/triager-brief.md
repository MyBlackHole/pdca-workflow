# T0300 Triage Brief — MySQL 四版本每个版本的转换测试

## 分类
- category: enhancement | scenario_type: development
- 依据：scenario-boundary-check 判定"可测试代码产出"（mysqlbin + gen_mysql_versions.py + 逐版本验证），走 development 路径。

## 查重
- 归档 T0250（0813-mysql-parquet-physical，AC-1）：已做四版本 **1M 行解析验证**（rows=1M、count/SUM/distinct/active 聚合一致），但：
  1. 聚合校验表缺 8.0 列（仅 5.6/5.7/8.4 列出）
  2. 四版本转换产物（parquet）未系统保留到 evidence（仅 8.0 的 poc_orders.ibd/.parquet 在）
  3. 未按"每个版本一个转换测试记录"组织
- knowledge/data-formats/mysql-innodb-physical-read-notes.md 已含版本差异矩阵 → 直接复用
- 无其他重复任务。

## Claim 验证（事实勘察，非询问）
- 容器：t0250-mysql56(5.6.51)/mysql57(5.7.44)/mysql8(8.0)/mysql84(8.4.11) 均在（Exited 0）
- 数据：四版本 volume 内 poct25.poc_orders 存在，但 .ibd 权限受限（drwx------，root 属主），
  且四版本 .ibd 未保留在 evidence（仅 8.0）；5.6/5.7 无 SDI 需 `--schema=`（bench/poc_orders.schema）
- 工具：build/mysqlbin 支持 SDI(8.0+) 与 schema(5.6/5.7) 双路径；--rows= 显式参数

## 结论
任务成立：需为 5.6/5.7/8.0/8.4 各执行 .ibd→Parquet 转换测试并逐版本验证、补 8.0 聚合、保留每版本产物为 evidence。

## 待澄清（P1/P2 grill）
- 数据获取：volume 内已有 .ibd 可 unshare 提取，还是重新灌数？（推荐：先尝试 unshare 提取既有库，避免重灌 4×1M）
- 验证深度：仅聚合(count/SUM/distinct)，还是加列值抽样/全量对照？（推荐：聚合 + 每版本随机 N 行抽样字段对照，兼顾深度与成本）
- 8.0 聚合缺口补验方式（推荐：与其余版本同口径补测）