# T0411 对话日志

## Plan 阶段
- 用户问"PDCA 方法论的本体是否完善"，经本体核验给出结论：主体正确但尚不完善——G1（pdca.md 根正文空）、G2（pdca-transition.md 正文空）、G3（act→plan 仅概念非转换边，设计取舍）、G4（缺科学方法内核）。
- 立项 T0411 补全：写 prd.md（AC-1 根正文、AC-2 转换元概念正文、AC-3 四阶段科学方法内核、AC-4 测试、AC-5 指南/校验），用户 final_confirmation 确认进入 Do。

## Do 阶段
- AC-1/AC-2：充实 `ontology/concept/pdca.md`（定义/起源/四阶段指针/循环指针/子概念枚举）与 `ontology/concept/pdca-transition.md`（合法边编码方式/当前边清单/act→plan 仅概念说明）。
- AC-3：phase-plan/do/check/act 四阶段贯通科学方法内核（Plan 预测/假说→Do 小试验验+原始观测→Check 比对观测与预测(偏差即信号)→Act 采纳/放弃并固化学习）。
- AC-4/AC-5：`tests/test_pdca_ontology_correct.py` 增根/转换非空 + 科学方法断言（11 用例）；`ONTOLOGY_GUIDE.md` 第 12 节完善说明。
- 用户中途"审查修改"选"深化科学方法表述"，将科学方法内核深化贯通至四阶段全部正文。
- 校验：ontology-validate OK（无环）、11 测试通过、validate-convergence valid:true、route 自检 ok；登记 11 条证据，进入 Check。

## Check 阶段
- 写 conclusion.md，逐 AC 回链证据；verdict=confirmed（已同步四阶段深化文案）。
- 用户检查确认后进入 Act。

## Act 阶段
- 知识决策：成果沉淀于 ontology 节点与 ONTOLOGY_GUIDE，不产孤立 knowledge/ 文件（knowledge_decision: skipped）。
- disposition=projected（PDCA 元本体完善模式可复用）。
- 写 journal 当日摘要，归档任务目录。
