# T0161 实施清单

## 1. Contract 与公共 CLI

- [ ] 定义 execution/invocation contract schema，包含路径安全、枚举、唯一性和最小结构。
- [ ] 实现 execution resolver 的 scenario 查询、文档锚点/marker 顺序校验和稳定错误输出。
- [ ] 实现 invocation resolver 的 frontmatter catalog、alias 查询、边类型校验与显式引用校验。
- [ ] 保持 route resolver 的现有 CLI 和输出不变。

## 2. 文档与调用迁移

- [ ] 重写 flow-do A/B，使 Red/Green 发生在编码/修复之前，并明确 slice/final 验证语义。
- [ ] 抽取 `triage-work`、`domain-modeling-work`、`handoff-work`，将保留的 manual skill 变为入口薄壳。
- [ ] 迁移 flow、grill 和 wayfinding 的 direct manual 引用；更新 `ask-matt` 为有效 alias。
- [ ] 更新 SKILLS-INDEX 和内容 baseline，逐个新增/增长资产写明必要性。

## 3. 验证与防回归

- [ ] 为两个 resolver 添加正常、非法输入、文档漂移、真实引用缺失和类型违规单元测试。
- [ ] 扩展公共 fixture，包含顺序交换但标题不变、automatic-to-manual 边和 stale alias 等反例。
- [ ] 将新验证接入内容审计，确保 budget 更新不能隐藏 contract 行为回归。
- [ ] 运行并登记以下验证：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/run-ai-friendliness-fixtures.py --all
python3 scripts/generate-skills-index.py --check
python3 scripts/audit-skill-content.py --check-budget
python3 scripts/pdca-doctor.py --json
python3 -m compileall -q scripts
```

## 回滚点

- Contract/schema/resolver 与相应测试作为一个提交；任一 contract 校验失败时先回滚该提交，而不保留半迁移的 flow/worker 引用。
- baseline 只在所有 fixture 通过后更新；若验证失败，恢复原 baseline 值并修复行为，不以放宽预算通过。
