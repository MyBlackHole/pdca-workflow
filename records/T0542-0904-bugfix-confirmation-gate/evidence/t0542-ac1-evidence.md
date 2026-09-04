# AC-1 证据：诊断到修复的确认门禁已落地且可审计

## 检查命令与结果

```bash
grep -q "确认修复方案" ontology/process/flow-do.md && echo "flow-do OK"
# flow-do OK

grep -q "fix_confirmation" schemas/clarification.schema.json && echo "schema OK"
# schema OK

grep -q "fix_confirmation" scripts/append-confirmation.py && echo "cli OK"
# cli OK

grep -q "fix-approval" pdca/ai-execution-contract.json && echo "contract OK"
# contract OK

grep -q "fix-confirmation" scripts/flow_audit.py && echo "audit OK"
# audit OK
```

## 新增 Phase 4.5 说明

`skill-diagnosing-bugs.md` 新增 Phase 4.5 Fix Approval，要求：
- 展示已验证假设/根因（区分三类）、修复方案、回归计划、影响范围、回滚策略
- 获 fix_confirmation:confirmed（captured:true，CLI 落盘）方可进入 Phase 5

## flow-do 与 contract 同步

- flow-do 路径 B 在“先复现并写出失败的回归测试”后增加“确认修复方案”，并移入“## 路径 B”段落内以通过 verify-document
- ai-execution-contract bugfix 新增 fix-approval phase（id=fix-approval, marker=确认修复方案）
- schema ai-execution-contract 扩展 fix-approval 枚举与 6-7 长度容差

## 审计

flow_audit.py 新增 fix-confirmation 检查：bugfix 缺 fix_confirmation:confirmed 记 FIX_CONFIRMATION_MISSING（audit WARN，不阻断存量）

## 科学依据

- HITL Approval-Gate（Velyr/Allsrc/Agent Patterns Catalog）：Agent 做事、Human 做决策，权限隔离+分支保护强制门禁
- Zeller 科学调试法：观察→假设→预测→实验→结论，Fix 前确认点
- Strategic Human Gate：2-3 个战略门禁优于全量门禁，固定展示 Divergence from plan
