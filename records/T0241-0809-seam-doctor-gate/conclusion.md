# Conclusion — T0241 seam 门禁接入 pdca-doctor

## 结论

**已解决。** seam 门禁已接入 pdca-doctor：`pdca-doctor.py --json` 输出新增
`seam_contracts` 段，批量校验活跃任务 spec 的 seam 声明，失败即 valid=false
并退出码非 0。doctor 成为无需 CI 基础设施的自动门禁入口。

## 对照 PRD

| AC | 描述 | 状态 |
|----|------|------|
| AC-1 | doctor --json 含 seam_contracts 段 | ✅ 实测含 checked/clean/issues |
| AC-2 | 全部通过时 valid=true | ✅ 真实仓库实测 valid |
| AC-3 | seam 失败时 valid=false + 退出非 0 | ✅ 单测覆盖（临时 root） |
| AC-4 | 现有 doctor 测试仍通过 | ✅ test_doctor_uses_explicit_fallbacks 通过 |
| AC-5 | 全套件通过 | ✅ 147 passed + 13 subtests |

## 证据链

- `doctor-seam`：pdca-doctor.py seam 段（importlib 加载 + 聚合）
- `doctor-tests`：2 个新测试（段存在 / seam 失败阻断）
- `convergence-map`：AC↔证据映射

## 关键发现

1. **脚本定位陷阱**：初版用 `root/"scripts/check-seam-contracts.py"` 定位
   校验脚本，导致临时 root（无 scripts/）加载失败返回 None，checked=0。
   修正为 `Path(__file__).parent`（doctor 自身同目录），与被检 root 解耦——
   校验脚本来自仓库，扫描/校验目标来自被检 root。
2. **doctor 完整依赖仓库结构**：临时 root 测试需 AGENTS.md + flows/flow-plan/
   SKILL.md + schemas + config/capabilities.yaml，否则 local_references 或
   capabilities 读取崩溃（测试 fixture 据此补全）。
3. **自动门禁闭环**：seam 门禁现在随 doctor 自动执行（doctor 是既有体检
   入口），无 CI 基础设施也能在每次体检时拦截 seam 漂移。

## 收敛条件

CC-1 ✅ 全部 AC 满足
CC-2 ✅ 复用 check-seam-contracts.find_active_specs/check_all（importlib 加载）
