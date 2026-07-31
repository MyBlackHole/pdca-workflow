# T0135 实施检查清单

## 执行前

- [ ] 用户完成 P6 方案终审，parent 与四个 child 均记录同一终审范围。
- [ ] `PDCA_HOME` 解析为仓库根目录。
- [ ] 工作树基线已记录，提交只包含本任务范围。
- [ ] 四个子任务边界与验收标准冻结。

## 子任务顺序

1. T0136：先交付 schema、验证器和 dry-run manifest；schema 测试通过前禁止删除。
2. T0137：交付 doctor、能力协议和生成索引。
3. T0139：交付六场景确定性 harness，作为内容精简的效果保持基线。
4. T0138：运行内容量审查，选择 Pareto 候选并逐项配对精简。
5. 回到 T0136：使用已冻结 schema 和已登记 manifest 执行历史清理并复验。
6. 父任务聚合所有 evidence，执行端到端 Check。

## 验证命令目标

具体 CLI 名称由子任务设计，但必须提供等价入口：

```bash
python3 -m unittest discover -s tests
python3 scripts/validate-workflow.py --all
python3 scripts/pdca-doctor.py --json
python3 scripts/generate-skills-index.py --check
python3 scripts/audit-skill-content.py --format json
python3 scripts/run-ai-friendliness-fixtures.py --all
python3 scripts/audit-history.py --dry-run --output deletion-manifest.json
```

## 删除门禁

- [ ] schema 版本已冻结。
- [ ] schema/语义验证正反例全部通过。
- [ ] 删除 manifest 已登记为 evidence。
- [ ] manifest 不包含 `records/`、`knowledge/`、`pdca/journal/`。
- [ ] 每个目标是已解析的具体任务目录，不含 glob 或未解析变量。
- [ ] Git 能列出并恢复全部目标。

## 内容精简门禁

- [ ] UTF-8 bytes 口径及其适用边界写入报告。
- [ ] 保存每个候选的 before digest 与指标。
- [ ] UTF-8 bytes 降幅 >= 15%。
- [ ] 同一组既定 fixture 全部通过。
- [ ] rubric 明确说明未覆盖场景和定性限制。

## 证据

- schema 与错误码规范
- 正反例及故障注入结果
- doctor 和索引生成报告
- 全量 skill 内容指标与 rubric
- 每项精简的 before/after 配对数据
- 历史删除 dry-run manifest 与执行后复验
- 六场景 fixture 结果

所有产物通过 register-evidence 登记后才能进入 Check。
