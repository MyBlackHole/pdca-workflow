# CI 硬门禁固化

## 背景
T0471/T0477 已硬化拆分/测试/树/闭环 4门禁，但仅本地 `ontology-validate + graph + frontier + scaffold` 可跑，CI 未阻断，后续提交可绕过。

## 目标
将本次 4门禁接入 `pre-commit` 与 `.github/workflows`，PR 缺 `fragment/disposition` 或 `validate/islands` 失败直接 `rejected`。

## 功能需求
1. `scripts/install-git-hook.sh` 已存在，补 `pre-commit` 校验 `ontology-validate` 与 `disposition` 关键词
2. 新增/更新 `.github/workflows/ontology-gate.yml` 跑 `validate + graph + frontier + validate-convergence`，非 0 即 fail
3. 保持 `LEGACY_SUPPORT_KINDS` 豁免历史任务，仅新任务阻断

## 非功能
- 本地与远端同一校验脚本 `ci-ontology-gate.py`

## 验收标准
- [ ] AC-1 本地门禁：无 `fragment` 且非豁免的 `development` 提交被 `pre-commit` 拒
- [ ] AC-2 远端门禁：`ontology-validate` 或 `islands>0` 时 workflow fail
- [ ] AC-3 无回退：历史 `archive` 任务不受新校验影响

## 关联本体节点
```
ontology:entity/ontology-deep-integration-knowledge
ontology:concept/pdca-ontology-ready
```
## 拆分映射
- CI 硬门禁 -> ontology:entity/ontology-deep-integration-knowledge
