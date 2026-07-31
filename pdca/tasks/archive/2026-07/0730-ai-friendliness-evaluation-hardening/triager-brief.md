# T0160 Triage Brief

## 分类

- 分类：enhancement
- 场景：development
- 来源：T0159 归档后的 AI 友好评测复核，而非对已归档任务的回写。

## 已验证事实

- `scripts/run-ai-friendliness-fixtures.py` 的正常 route fixture 只检查 `flow-do/SKILL.md` 中的路径标题，未按 fixture `scenario` 执行选择。
- `missing_reference` 故障直接返回预期错误码，没有经过引用解析。
- 现有通用 harness 没有对 Check/Act 的 evidence、verdict 与 disposition 做完整生命周期验证。
- 内容审计可测 bytes 和断链，但没有保存基线或预算门禁。

## 查重

- `R0135-ai-friendliness-hardening`、`R0139-ai-friendliness-harness` 和 `knowledge/ai-efficiency/ai-friendliness-review-methodology.md` 是既有基线与方法论。
- 未发现处理上述四个当前实现缺口的活跃任务；不与现有任务重复。

## 信息缺口与建议

- 需要确定机器可执行的路由合约应以何种单一事实源表达，避免测试重复解析自然语言。
- 需要确定内容成本预算的粒度与基线更新规则。
- 推荐不引入真实 LLM 成功率、模型比较或外部 Agent runtime；先把确定性评测的结论变为可证伪的行为测试。
