# T0240 Triage Brief — seam_contract 集成 CI 门禁

## 来源
T0233 conclusion 下一轮建议："seam 契约可在 CI 中作为门禁：运行
scripts/seam_contract.py 校验每个 development spec。"

## Claim 验证（P0）
- seam_contract.py 存在，CLI 接受 spec 路径 + --base-dir，输出 {valid, issues} ✅
- 已接入 flow-plan P6 门禁（每任务开发时校验）✅
- 仓库无 CI 基础设施（无 .github/workflows、Makefile）⚠️
- 批量实测（P0 关键发现）：
  - 0809-mechanism-fixes/prd.md → valid ✅
  - 0809-fastapi-service/prd.md → INVALID（tests/test_service.py 缺失）
  - 0809-fastapi-api/prd.md → INVALID（tests/test_api.py 缺失）
  - 原因：T0234 FastAPI 验证在外部项目，测试不在本仓库；归档 spec 的
    seam 指向已不存在的测试文件

## 设计决策点
1. 校验范围：仅活跃任务 vs 含归档任务
2. 归档任务 seam 不匹配的处理：容忍跳过 / 修复 spec / 仅校验活跃
3. CI 形态：仓库无 CI → 用脚本（scripts/check-seam-contracts.py）+ 测试，
   而非 GitHub Actions

## 后续
P2 Grill → P3 PRD → P3.5 seam → P4 → P5 → P6 → Do
