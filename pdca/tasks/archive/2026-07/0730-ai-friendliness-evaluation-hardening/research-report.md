# T0160 评测依据

## 可执行 oracle

- Memon、Banerjee、Nagarajan 在 ASE 2003 的实证研究表明，test oracle 的信息与比较过程会显著影响测试有效性与成本。T0160 因此把 scenario→route 的预期行为从 Markdown 标题存在性升级为可执行合约，而不是增加无判别力案例。
- 参考：[What Test Oracle Should I Use for Effective GUI Testing?](https://www.cs.umd.edu/~atif/papers/MemonASE2003-abstract.html)

## 结构化约束的边界

- JSONSchemaBench 说明 JSON Schema 是约束结构化输出的常用方法，可提高格式合规；但它评测的仍包括效率、约束覆盖和输出质量，不能从 schema 合规推出语义成功。T0160 因此同时要求真实 resolver、mutation 反例和 fail-closed 门禁。
- 参考：[Generating Structured Outputs from Language Models: Benchmark and Studies](https://arxiv.org/abs/2501.10868)

## 真实 Agent 外部效度

- AgentBench 在多轮交互环境中评测推理、决策和指令遵循，说明确定性合约回归不能替代交互式 Agent 评测。
- SWE-bench 使用真实仓库和 fail-to-pass 测试；GAIA 保留部分答案；SWE-bench-Live 采用新鲜实例降低静态基准过拟合。这些方法支持未来采用固定 runner 与保留任务集的准入条件。
- 参考：[AgentBench](https://arxiv.org/abs/2308.03688)、[SWE-bench](https://www.swebench.com/original.html)、[GAIA](https://arxiv.org/abs/2311.12983)、[SWE-bench-Live](https://arxiv.org/abs/2505.23419)

## 结论

本任务的目标是让本地确定性评测的 oracle 真实、可重复且不自证；不声称仅靠机器可读合约提升模型能力，也不以现有通过率表示真实 Agent 成功率。
