# Do 阶段验证记录

## 自动化验证

- 命令：`python3 -m unittest discover -s tests`
- 结果：40 tests，全部通过；耗时约 4.8 秒。
- 语法检查：`python3 -m py_compile scripts/flow_audit.py scripts/transition-phase.py tests/test_flow_audit.py` 通过。
- 差异检查：`git diff --cached --check` 通过。

## 行为覆盖

- Plan→Do：验证缺失子任务、inactive 子任务和 final confirmation；inactive 问题不会额外阻断既有转换。
- Do→Check：验证 evidence 注册、AC 覆盖、manifest/文件摘要一致性和 convergence map；保留失败与成功尝试。
- Check→Act：验证 conclusion 与 verdict。
- Act→Archive：验证 disposition。
- 路径安全：非法 `meta.record` 不会使审计文件逃逸 `records/`。

## 当前任务实证

T0158 在 evidence 注册前执行了预期失败的 Do→Check 尝试；
`records/T0158/flow-audit.json` 已记录 `EVIDENCE_MANIFEST_MISSING`、
`AC_COVERAGE_UNVERIFIABLE`、`EVIDENCE_INTEGRITY_UNVERIFIABLE` 和
`CONVERGENCE_MAP_MISSING`。审计记录不会替代或绕过原有 transition gate。
