# PRD — seam 门禁接入 pdca-doctor

## 背景

T0240 实现 check-seam-contracts.py（仓库级 seam 批量校验）但无自动触发点。
仓库无 CI 基础设施。pdca-doctor.py 是现有体检入口，接入 seam 段使其成为
自动门禁：每次运行 `pdca-doctor.py --json` 即校验全部活跃 spec seam。

## 需求

### R1 doctor 新增 seam_contracts 段
`scripts/pdca-doctor.py`：
- 用 importlib 加载 check-seam-contracts（连字符文件名），复用
  find_active_specs + check_all
- payload 增 `seam_contracts` 段：{checked, clean, issues}
- seam 校验失败（issues 非空）→ payload.valid = false，退出码非 0

### R2 向后兼容
现有段（capabilities/references/task_timeline）不变，新增段不破坏结构。

### R3 测试
- doctor --json 输出含 seam_contracts 段
- 活跃 spec seam 全部通过 → valid true
- 存在 seam 失败 → valid false 且退出码非 0

## 验收标准

- [ ] AC-1: doctor --json 输出含 seam_contracts 段
- [ ] AC-2: 全部活跃 spec seam 通过时 valid=true
- [ ] AC-3: 存在 seam 失败时 valid=false 且退出码非 0
- [ ] AC-4: 现有 doctor 测试仍通过（向后兼容）
- [ ] AC-5: 全套件通过

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足
- [ ] CC-2: 复用 check-seam-contracts 逻辑（importlib 加载，不重复实现）

### 声明的测试接缝

- seam: tests/test_operations.py -> scripts/pdca-doctor.py
