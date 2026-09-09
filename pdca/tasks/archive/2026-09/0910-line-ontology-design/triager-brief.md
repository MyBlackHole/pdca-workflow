# Triage Brief — 0910-line-ontology-design

- **category**: enhancement
- **scenario_type**: design
- **summary**: 设计行级本体表达门禁：每行更改可回链到本体节点
- **current behavior**: 证据粒度到文件digest，处置到任务级ontology引用；行与本体无机器可检关联
- **desired behavior**: 双方案对比（提交 trailer 声明 vs hunk 映射表），选seam/adapter/depth最优，产design.md
- **key interfaces**: git diff hunk、evidence manifest、disposition引用、pre-commit/archive门禁点
- **acceptance criteria**: 双方案对比可检；推荐方案有接口契约与测试seam；登记为证据
- **out of scope**: 不实现门禁代码，仅设计；另起development实施
- **information gaps**: 行豁免清单、映射载体、 enforcement 点需对齐
- **dedup results**: 无行级设计任务，属新设计
- **recommended next steps**: design-it-twice双方案后grilling复核
