# 本体深化收敛：信号去泛化×模板硬化×复用检索×Act门禁收紧

## 背景

`T0471` 已将本体从顾问式推为默认路径，`skill-to-tickets:3.5`默认跑`ontology_tree_split`、`ontology_test_scaffold`三模式、`composed_of`叶→根、`ontology_anchor`默认。但存量 `attributes.testable_signal` 仍有泛化残留可派生性差，PRD仍可无`## 拆分映射`通关，Act仅关键词检`ontology:`未验节点存在，全任务检索复用仍靠人工。

## 目标

- 质量：泛化信号清零可机检，三模式均可自动生骨架
- 模板：新建任务默认带拆分映射与fragment，缺失即阻断而非告警
- 复用：新建/拆分时自动推荐可复用本体，`clash-check`阻断可追溯
- 闭环：Act从字符串含`ontology:`升级为节点存在性+`validate`校验

## 范围

- 输入：`ontology/` 363节点、T0471四叶实体树、`ontology_test_scaffold.py`、`ontology_tree_split.py`、`compute-frontier.py`、`ontology_gate.py`
- 输出：泛化治理脚本+模板硬化+检索提示+Act严格门禁，全绿归档
- 不做：不引入图数据库，不改`task.schema.json`结构，不追溯重写历史任务

## 功能需求

1. 存量信号去泛化：全量扫描`attributes.testable_signal`，含`由领域实践与测试验证`等判泛化，精化为含动词+对象+判定+脚本的三模式信号，抽检`ontology_test_scaffold --node`可生成
2. PRD模板硬化：`to-tickets`与`triage`产出PRD默认含`## 拆分映射`与`## 关联本体节点`，`task_identity`无`fragment`新建时`doctor`告警，`ontology_tree_split`缺映射报错不回退
3. 复用检索联动：候选slug在`ontology-clash-check`前经`ontology_graph`检索相似本体（字面/relations），提示`ontology:xxx`复用边，`relations`强引用可被`validate`校验
4. Act门禁收紧：`ontology_gate.archive_ontology_ready`外，新增Act阶段校验`meta.disposition`中`ontology:`串确为已存在`pdca.asset/v1`节点且`ontology-validate`与`islands:0`通过，否则`transition-phase.py → archive`拒收；`records-only`须`evidence/manifest.jsonl`非空

## 非功能需求

- 兼容：历史任务不强制补fragment，仅新任务生效
- 可观测：`ontology_graph --format summary`与`scaffold`产出机器可读
- 门禁零回退：`ontology-validate`+`graph islands`+`frontier valid`全绿

## 验收标准

- [ ] AC-1 存量去泛化：`grep -r "由领域实践与测试验证" ontology --include="*.md" | wc -l == 0`，抽样10节点`ontology_test_scaffold --node`均产`test_*.py`与`scaffold-map.json`且`pytest`可收集
- [ ] AC-2 模板硬化：新建development任务PRD必含`## 拆分映射`，`meta.ontology_fragment`缺失时`pdca-doctor --json`报`ONTOLOGY_FRAGMENT_MISSING`，有fragment无映射时`ontology_tree_split` `ERROR`退出
- [ ] AC-3 复用联动：`ontology-clash-check --candidates <近似既有节点名>` 阻断并提示`ontology:xxx`复用，`relations`强引用可被`ontology-validate`与`ontology_graph`追溯
- [ ] AC-4 Act收紧：`meta.disposition`含伪`ontology:xxx`（不存在节点）时`transition-phase.py → archive`被`ontology_gate`拒收；`records-only`无evidence时同样拒收，真节点+0 islands放行
- [ ] AC-5 全链路绿：`ontology-validate` 0 issues，`ontology_graph --format summary` `islands:0`，对拆分后DAG `compute-frontier` `valid:true`，`validate-convergence` `valid:true`

## 关联本体节点

```
ontology:entity/ontology-deep-integration
ontology:pattern/testable-signal-to-test-derivation
ontology:pattern/ontology-modular-reference
ontology:concept/pdca-task
ontology:concept/ontology-validate
ontology:domain/skill-to-tickets
ontology:domain/skill-testing-strategy
```

## 拆分映射

- 存量信号去泛化 -> ontology:pattern/testable-signal-to-test-derivation
- PRD模板硬化与fragment默认 -> ontology:domain/skill-to-tickets
- 复用检索与clash联动 -> ontology:pattern/ontology-modular-reference
- Act知识闭环收紧 -> ontology:entity/ontology-deep-integration-knowledge

## 风险与对策

- 风险：全量精化信号工作量大。对策：分批治理，先堵新增门禁，存量按`T0461`分域优先级精化
- 风险：模板硬化误伤research豁免。对策：`ontology_exempt=true`任务豁免fragment/映射校验

## 开放问题

- 是否将Act节点校验设为`archive`硬门禁而非仅`act`提示，本PRD取硬门禁
