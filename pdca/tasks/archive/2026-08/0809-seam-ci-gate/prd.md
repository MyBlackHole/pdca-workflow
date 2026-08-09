# PRD — seam_contract 集成 CI 门禁

## 背景

T0233 建立了 PRD seam 契约（spec 的 `### 声明的测试接缝` 子节与实际测试一致性），
并在 flow-plan P6 单任务门禁校验。但缺少**仓库级批量校验**：每次提交无法
自动发现活跃任务 spec 的 seam 漂移。T0233 conclusion 建议集成 CI 门禁。

## 需求

### R1 批量校验脚本
新增 `scripts/check-seam-contracts.py`：
- 扫描 `pdca/tasks/`（不含 archive）下所有含 `### 声明的测试接缝` 的 spec（prd.md）
- 对每个 spec 运行 seam_contract 校验（复用 scripts/seam_contract.py）
- 输出 JSON 结果：{valid, checked, issues_per_spec}
- 任一活跃任务 spec 校验失败 → 退出码非 0

### R2 测试
新增测试覆盖：
- 扫描逻辑：只扫活跃目录、识别含 seam 的 spec
- 批量结果聚合：全部 valid / 部分 invalid
- 退出码语义

## 验收标准

- [ ] AC-1: check-seam-contracts.py 能扫描活跃任务 spec 并校验
- [ ] AC-2: 全部活跃任务 spec 通过时退出码 0
- [ ] AC-3: 存在失败 spec 时退出码非 0
- [ ] AC-4: 归档任务 spec 不被扫描（范围限定）
- [ ] AC-5: 现有测试套件全通过

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足
- [ ] CC-2: 复用 seam_contract.py 核心逻辑（不重复实现）

### 声明的测试接缝

- seam: tests/test_seam_ci_gate.py -> scripts/check-seam-contracts.py
