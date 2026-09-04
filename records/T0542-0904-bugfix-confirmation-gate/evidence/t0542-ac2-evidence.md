# AC-2 证据：根因模板已修正且与诊断结论一致

## skill-bug-analysis.md 修正

- 新增科学方法内核段落（Zeller）：closest possible world 最小差异定义因果，需实验验证
- 步骤 2 增加可证伪假设与双向预测格式
- 步骤 5 明确：根因≠现象，追到代码/配置/流程层面且与诊断假设双向预测一致，区分三类：
  - 假设/设计错误
  - 实现/环境错误
  - 流程/证据遗漏
- 新增“修复前确认门禁”章节，要求 fix_confirmation:confirmed 方可改代码

```bash
grep -q "根因≠现象" ontology/domain/skill-bug-analysis.md && echo "analysis root OK"
grep -q "fix_confirmation" ontology/domain/skill-bug-analysis.md && echo "analysis gate OK"
grep -q "双向预测" ontology/domain/skill-bug-analysis.md && echo "two-sided OK"
```

## skill-bug-commit-format.md 修正

- 铁律“根因 ≠ 现象，必须追到代码层面” → “必须追到代码/配置/流程层面且与诊断假设的双向预测一致；区分三类”
- 新增“未获 fix_confirmation:confirmed 不得提交修复”

```bash
grep -q "根因 ≠ 现象" ontology/domain/skill-bug-commit-format.md && echo "commit root OK"
grep -q "假设/设计错误" ontology/domain/skill-bug-commit-format.md && echo "categories OK"
```

## skill-diagnosing-bugs.md 关联

- Phase 4.5 要求展示“已验证假设/根因（区分三类）”与诊断 Phase 3 双向预测一致
