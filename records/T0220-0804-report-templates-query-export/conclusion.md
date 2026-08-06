---
schema: pdca.asset/v1
id: T0220-0804-report-templates-query-export
phase: check
source_ids: [e1b, e2, e3, e4b, e5, e6, e6b, e7, e8, e9, e10c, e10s, e11c, e11r]
---

## 上下文

report-web 报表模块：16 套固定模板查询与 CSV/PDF 同步导出。核心工程目标：
模板注册表（YAML 清单 + Handler 固定 SQL）、Keyset 分页与多域 K 路归并、
CSV 流式截断导出、PDF 表格/图表分页、读池逻辑配额。依赖 T0215/T0216/T0219。

## 假设与结果

| 假设/验收 | 结果 |
|-----------|------|
| AC-1 16 套模板 YAML 随包管理、index.yaml 清单加载、启动校验（e1b/e3/e8） | 达成：全量 284 passed |
| AC-2 固定参数化 SQL，请求不能指定表/列/排序（e4b） | 达成：全参数 %s 绑定，无拼接 |
| AC-3 16 套读模型 golden 通过 PG17 seed（e10s/e11c/e11r） | 达成：新增全 16 套真实 PG 执行冒烟 2 passed + 6 精确单测 |
| AC-4 Keyset 无重复/漏页、多域 K 路归并、禁全局 OFFSET（e5） | 达成 |
| AC-5 CSV 流式、4000 行 +1 探测截断标记（e6） | 达成 |
| AC-6 PDF 50/页分页重复列头、图表分页、上限同 CSV（e6b） | 达成：ExportService 51 passed |
| AC-7 读池配额 16/2/2、耗尽 429、超时 503（e7） | 达成 |
| AC-8 data_state 区分无匹配/覆盖不足，明细不进页面（e9） | 达成 |

## 分析

Check 阶段新增 16 套模板真实 PG 执行冒烟测试（test_all_templates_execute.py），
暴露并修复 3 个真实 SQL bug（commit e173de4，0.3.0 -> 0.4.0）：

1. **_pick_filter_column 子串误判**：`prefix in from_sql` 用子串匹配，`t` 误命中
   `agg_task_daily` 等含该字母的表名，选中不存在别名 `t.`，导致 missing
   FROM-clause。修复为 `别名.`（代点）断言。
2. **_domain_predicate 域列歧义**：裸 `backup_domain_id` 在多表 JOIN 中歧义。
   为 HandlerSpec 新增 `domain_col` 字段，所有 JOIN 模板显式使用主体列别名
   （`a.`/`c.`/`ds.`/`po.`/`t.`）。
3. **常量 GROUP BY**：storage_capacity_trend 在 group_mode=overall 时
   GROUP BY 字符串常量 `'overall'` 非法。改为 group_key 常量不入 GROUP BY。

修复后用 6 个 SQL 片段级精确单测锁定根因（test_query_handlers_sql.py），
防止回归。全量回归 284 passed（6 个 JWT error 为既有 REPORT_TOKEN_PRIVATE_KEY
未配置环境问题，与 T0220 无关）。

Grill 确认 4 项关键决策（clarinifications.jsonl）：
- 导出并发上限 Export2，接受导出期间占用读连接 trade-off
- 保持 2s 页面/30s 导出超时边界
- 保持 4000 行导出截断
- 为 3 个根因补精确单测锁定回归

收敛验证：convergence-map-v4，`valid: true`。

## 失败原因

无（结论成立，无 rejected/partial 部分）。

## 适用边界

- 模板为 16 套固定集，新增模板需扩展 registry + handler。
- 导出限 4000 行截断，全量导出不在本次范围（T0221 异步方案）。
- 单进程 BoundedSemaphore 配额，多实例部署需分布式配额（见下一轮建议）。
- 页面查询 2s 超时，超大域趋势模板可能超时（当前 keyset 分页缓解）。

## 下一轮建议

- T0221：异步/后台导出（用户确认延后），覆盖任意大数据量。
- 多实例部署时读池配额需外部化（Redis/DB），当前仅单进程内存信号量。
- 报表模板/超时/截断值参数化为部署可配置，减少硬编码默认值。