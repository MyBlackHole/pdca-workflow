# P2补强：tdd seams前置与diagnosing-bugs十回路及wayfinder HITL/AFK

## 背景

T0489 P1（wizard+多上下文）后，T0487 gap矩阵剩余P2三项：`tdd` seam需书面确认、 `diagnosing-bugs` 10回路未完整枚举、 `wayfinder` HITL/AFK 需与 mattpocock 4 label对齐。本任务打包一次性深化3个domain节点，补齐mattpocock P2差距，关闭T0450后新增gap。

## 目标

- `skill-tdd` 增加 `##Seam分析` 机器可读书面确认段与校验门禁
- `skill-diagnosing-bugs` 完整枚举10回路+ tighten三维（更快/更锐/更确定）
- `skill-wayfinder` 对齐 mattpocock `wayfinder:<type>` 4 label（research/prototype/grilling/task）与 HITL/AFK 约束

## 范围

- 输入：`ontology/domain/skill-tdd.md:1` `skill-diagnosing-bugs.md:1` `skill-wayfinder.md:1` + mattpocock `tdd/SKILL.md` `diagnosing-bugs/SKILL.md` `wayfinder/SKILL.md`
- 输出：3节点深化 + `SKILLS-INDEX` 重生成 + 全绿校验
- 不做：不引入 `teach`，不改业务代码，不改 schema

## 功能需求

1. tdd书面确认：`## Seam分析` 段含 `- seam: <test-file> -> <module>` 机器可读清单，写测试前必须列清单并与用户/AI书面确认，未经确认不写测试；模板指向 `templates/to-spec/SPEC.md`
2. 十回路：Phase1枚举10种回路（failing test/curl/CLI/browser trace/harness/property/bisection/differential/HITL）按序尝试，tighten三维可复核
3. wayfinder：Ticket 4类 `wayfinder:research/prototype/grilling/task` 分HITL/AFK（research AFK/prototype HITL/grilling HITL/task混合），声明 `skill-wayfinder` 为 HITL 约束

## 非功能需求

- 门禁：`ontology-validate 0 issues, islands:0`，`grep -q "Seam分析" skill-tdd.md` 等可命中
- 可观测：`ontology_graph --format dot` 含新边

## 验收标准

- [ ] AC-1 tdd书面确认：`skill-tdd.md` 含 `##Seam分析` 与 `- seam:` 机器可读且 `grep -q "预先约定的 seam"` 通过
- [ ] AC-2 十回路：`skill-diagnosing-bugs.md` 枚举10回路且含 tighten三维（更快/更锐/更确定）可 `grep -q "10" `命中
- [ ] AC-3 wayfinder HITL/AFK：`skill-wayfinder.md` 含 `wayfinder:research|prototype|grilling|task` 与 HITL/AFK 分类且 `grep` 可命中
- [ ] AC-4 索引与图谱：`SKILLS-INDEX.md` 重生成且 `ontology_graph islands:0`
- [ ] AC-5 收敛可验证：`convergence.json` 回链AC与证据，`validate-convergence valid:true`

## 关联本体节点

```
ontology:domain/skill-tdd
ontology:domain/skill-diagnosing-bugs
ontology:domain/skill-wayfinder
ontology:concept/phase-boundary-decision-tree
ontology:concept/skill-mechanics
```

## 拆分映射

- tdd书面确认 -> ontology:domain/skill-tdd
- 十回路 -> ontology:domain/skill-diagnosing-bugs
- wayfinder HITL/AFK -> ontology:domain/skill-wayfinder
