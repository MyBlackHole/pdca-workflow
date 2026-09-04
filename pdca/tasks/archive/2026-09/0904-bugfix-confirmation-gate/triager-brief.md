# Triage Brief — 0904-bugfix-confirmation-gate

- **category**: bug
- **scenario_type**: bugfix
- **summary**: Bug 分析/诊断流程在 Do 阶段可直接修改代码，未经过用户确认；且现有根因模板表述不准确
- **current behavior**: diagnosing-bugs Phase 4→5 无强制确认，Phase 3 仅“Show to user if present”软约束；bug-analysis 步骤 6 直通修复建议；flow-do bugfix 路径无“确认修复方案”标记；clarification schema 无 fix_confirmation 类型；gate 无 Do 内校验
- **desired behavior**: 诊断完成→修复前必须向用户展示已验证假设/根因/修复方案/回归计划/影响范围并获书面确认（fix_confirmation:confirmed, captured:true）方可改代码；根因模板修正为与诊断结论一致、可追溯、区分假设/实现/流程三类且与 commit 格式对齐
- **key interfaces**: diagnosing-bugs 诊断环、bug-analysis 根因分析、bug-commit-format 提交格式、flow-do 执行契约、clarification 确认机制、flow_audit 审计
- **acceptance criteria**: 运行 grep -q "确认修复方案" flow-do.md 得到命中；运行 grep -q "fix_confirmation" schemas/clarification.schema.json 得到命中；运行 python3 scripts/flow_audit.py 相关校验通过；根因模板与 diagnosing-bugs 假设双向预测一致
- **out of scope**: 不引入 do→check 强阻断（存量兼容）；不改变 plan→do 的 final_confirmation 语义
- **information gaps**: 根因模板具体哪几处措辞需修正已通过追问确认为“现有模板不对”，需在 Grill 中细化
- **dedup results**: 检索 pdca/tasks/**/task.json 与 ontology/domain/*.md，未发现同类“修复前确认门禁”任务；最接近为 T0519 bug-scenario-mismatch（场景错配）与 T0243 diagnosing-bugs 增强，已归档不冲突
- **recommended next steps**: 按档 B 实施：schema + append-confirmation + 双 skill 文本 + flow-do marker + execution-contract + audit WARN + 契约测试
