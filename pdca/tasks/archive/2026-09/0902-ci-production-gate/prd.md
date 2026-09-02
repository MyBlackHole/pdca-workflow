# CI硬拦接入production-ontology-gate --all

## 背景
`production-ontology-gate --all` 已 `GATE OK`（`392 nodes 1008 edges islands:0`），但 `scripts/ci-ontology-gate.py:34` 仅拦 `validate + scenario双层`，未拦六维科学门禁，`pre-commit`/`ontology-gate.yml` 可绕过 `mermaid/P08/hundred` 缺口。需将生产门禁接入提交级硬拦。

## 目标
- `ci-ontology-gate.py` 在 `validate` 后追加 `production-ontology-gate --all --json` 解析，任一维 `FAIL` 即 `GATE FAILED` 非0
- `.github/workflows/ontology-gate.yml` 与 `scripts/install-git-hook.sh` 均复用同一 `ci-ontology-gate`（不新增独立校验路径）
- 本地 `python3 scripts/ci-ontology-gate.py` `GATE OK` 可复核

## 范围
- 输入：`scripts/ci-ontology-gate.py` 现状 `scripts/production-ontology-gate.py` `ontology/pattern/production-ontology-scientific-gate.md`
- 输出：`ci-ontology-gate.py` 接线版 + `validate 0` + `gate --all OK` + `ci-gate` 本地 `GATE OK`
- 不做：不改其他业务逻辑

## 功能需求
1. `ci-ontology-gate.py` 追加 `production-ontology-gate --all` 调用，解析 `gate` 字段，`OK` 才放行
2. `pre-commit` 与 `workflow` 均调 `ci-ontology-gate`（已是），无需新增脚本路径
3. `gate --all` 失败时输出 `GATE FAILED: production-ontology-gate` 并非0

## 非功能需求
- 中文；`validate 0`；不破坏现有 `validate + scenario` 双层

## 验收标准
- [ ] AC-1 ci接gate：`grep -q 'production-ontology-gate' scripts/ci-ontology-gate.py` 且 `ci-gate` 调 `--all` 且 `FAIL` 时非0
- [ ] AC-2 hook复用：`grep -q 'ci-ontology-gate' .github/workflows/ontology-gate.yml` 且 `scripts/install-git-hook.sh` 含 `ci-ontology-gate`
- [ ] AC-3 全绿：`validate 0` + `islands:0` + `gate --all OK` + `ci-ontology-gate` 本地 `GATE OK`
- [ ] AC-4 收敛 valid:true

## 关联本体节点
```
ontology:pattern/production-ontology-scientific-gate
scripts/ci-ontology-gate.py
```

## 拆分映射
- 接gate -> ci-ontology-gate.py
- hook复用 -> yml/sh
