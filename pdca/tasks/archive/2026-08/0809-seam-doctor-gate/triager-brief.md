# T0241 Triage Brief — seam 门禁接入 pdca-doctor

## 来源
T0240 conclusion 遗留缺口：check-seam-contracts.py 已实现但**无自动触发点**
（仓库无 CI 基础设施）。用户决策：接入 pdca-doctor.py，形成自动门禁。

## Claim 验证（P0）
- pdca-doctor.py main() 聚合多段（capabilities/references/task_timeline），
  payload.valid 由 missing_required + missing_references 决定 ✅
- active_task_timeline(root) 是现有段函数先例（L20-37）✅
- check-seam-contracts.py 提供 find_active_specs + check_all 可复用 ✅
- doctor 已有测试先例（test_operations.py:63 test_doctor_uses_explicit_fallbacks）✅

## 方案
在 pdca-doctor.py：
1. 新增 seam 段：调用 check_seam_contracts.find_active_specs + check_all，
   输出 {checked, clean, issues}
2. payload 增 "seam_contracts" 段；valid 聚合：seam issues 非空 → invalid
3. 保持 --json 输出结构向后兼容（新增段不破坏现有字段）
4. 测试：doctor --json 含 seam_contracts 段；有 seam 失败 → valid false

## 后续
P2 Grill → P3 PRD → P3.5 seam → P4 → P5 → P6 → Do
