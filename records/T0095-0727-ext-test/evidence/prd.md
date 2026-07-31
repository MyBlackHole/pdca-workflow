# 外部项目模式端到端验证

## 目标
验证外部项目通过 PDCA_HOME 引用本工作流的完整路径解析。

## 验证清单
- [x] `$PDCA_HOME/skills/triage/SKILL.md` → 已解析（53 行）
- [x] `$PDCA_HOME/flows/flow-plan/SKILL.md` → 已解析（118 行）
- [x] `$PDCA_HOME/skills/advance-phase/SKILL.md` → 已解析（25 行）
- [x] `$PDCA_HOME/templates/PDCA_HOME.md` → 已解析
- [x] `$PDCA_HOME/pdca/tasks/` → 任务可写入
- [x] `$PDCA_HOME/records/` → 记录目录存在
- [ ] `$PDCA_HOME/docs/adr/` → 目录缺失，需创建

## 任务
在外部测试项目 `/tmp/test-pdca-ext` 中添加 `.gitignore` 文件。