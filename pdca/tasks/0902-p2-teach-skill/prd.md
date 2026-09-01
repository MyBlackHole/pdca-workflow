# P2补强：teach连续教学工作空间

## 背景

mattpocock `teach` 为 productivity 教学生态（stateful，多session，以当前目录为教学工作空间），以 mission 为牵引、reference 为压缩知识、lesson 为HTML可交互单元、assets 复用。本地此前未覆盖，T0487 gap矩阵列为P2（低优但完整度）。本次补齐使“教授新技能/概念”可本体化、可追溯。

## 目标

- 新增 `ontology/domain/skill-teach.md`（user-invoked），完整复刻 teaching workspace、mission、ZPD、知识/技能/智慧三支、lesson/assets/reference/learning-records/RESOURCES/NOTES 结构
- 与 `skill-grill`/`domain-modeling` 联动：mission未清时先追问

## 范围

- 输入：`mattpocock/skills productivity/teach/SKILL.md` + MISSION/RESOURCES/LEARNING-RECORD 格式
- 输出：1 domain节点 + 索引重生成 + 全绿
- 不做：不改业务代码，不新增 lessons 实例（仅 skill 定义）

## 功能需求

1. skill-teach：`invocation: manual`，描述 Teaching Workspace（MISSION.md/reference/*.html/RESOURCES.md/learning-records/*.md/lessons/*.html/assets/* /NOTES.md），Philosophy（知识/技能/智慧）、Fluency vs Storage、Lessons（HTML、短赢、ZPD、引用）、Assets复用、Mission牵引、ZPD计算、Acquiring Wisdom（社区委派）
2. 门禁：`grep -q "TEACHING WORKSPACE\|Teaching Workspace" skill-teach.md` 可命中

## 非功能需求

- `ontology-validate 0 issues, islands:0`

## 验收标准

- [ ] AC-1 teach节点已创建：`ontology/domain/skill-teach.md` 存在且 `ontology-validate` 通过且 `grep -q "Teaching Workspace" `通过
- [ ] AC-2 内容完整：含 MISSION/reference/RESOURCES/learning-records/lessons/assets/NOTES 且含 Fluency vs Storage 与 Wisdom 社区委派
- [ ] AC-3 索引与图谱：`SKILLS-INDEX` 含 teach 且 `islands:0`
- [ ] AC-4 收敛可验证：`convergence.json` 回链AC与证据 `valid:true`

## 关联本体节点

```
ontology:domain/skill-teach
ontology:concept/skill-mechanics
ontology:concept/domain-modeling
```

## 拆分映射

- teach工作空间 -> ontology:domain/skill-teach
