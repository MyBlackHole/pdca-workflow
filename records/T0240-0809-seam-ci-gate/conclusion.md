# Conclusion — T0240 seam_contract 集成 CI 门禁

## 结论

**已解决。** 仓库级 seam 契约门禁已实现：批量扫描活跃任务 spec 并校验
seam 声明与实际测试一致性，全通过退出 0，存在失败退出非 0。

## 对照 PRD

| AC | 描述 | 状态 |
|----|------|------|
| AC-1 | 脚本扫描活跃 spec 并校验 | ✅ 实测 valid |
| AC-2 | 全通过退出码 0 | ✅ 单测覆盖 |
| AC-3 | 有失败退出非 0 | ✅ 单测覆盖 |
| AC-4 | 归档 spec 不扫描 | ✅ 单测覆盖 + 实测 5 归档 spec 未计入 |
| AC-5 | 全套件通过 | ✅ 145 passed + 13 subtests |

## 证据链

- `ci-script`：scripts/check-seam-contracts.py 实现
- `ci-tests`：5 个测试覆盖扫描/聚合/退出码/归档排除
- `convergence-map`：AC↔证据映射

## 关键发现

1. **P0 实测揭露归档 spec seam 漂移**：T0234 FastAPI 归档 spec 的 seam
   指向 tests/test_service.py、test_api.py，这些测试随外部项目生命周期已
   不存在于本仓库。若校验含归档 spec 会误报——这直接决定了"仅活跃任务"
   的范围决策，且归档 spec 为不可变记录不应修改。
2. **开发期即拦截**：T0240 自身 PRD 声明 seam 后，check-seam-contracts 在
   test_seam_ci_gate.py 创建前即报"测试文件缺失"，证明门禁能防"PRD 声明了
   seam 但测试未落地"的漏检。
3. **base-dir 默认 = root**：避免调用者传 --root 与 --base-dir 不一致的坑
   （初版默认 cwd 导致子进程误报，已修正为默认 root）。

## 收敛条件

CC-1 ✅ 全部 AC 满足
CC-2 ✅ 复用 seam_contract.validate_seams，未重复实现
