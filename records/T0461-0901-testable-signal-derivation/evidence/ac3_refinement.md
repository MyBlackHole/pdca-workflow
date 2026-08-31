# AC-3 示范精化说明

## 修改节点 1：ontology/domain/ai-efficiency-contract-test-pattern.md
- 原 testable_signal: 由领域实践与测试验证
- 新 testable_signal: 运行 scripts/seam_contract.py 校验 PRD 声明的 seam 清单与实际测试文件的一致性，且契约测试套件 SourceConsistencyContractTest/DesignVocabContractTest/SeamFileExistenceTest 全部通过，不一致时退出非0并报告缺失项
- 派生模式：契约测试（Contract Test）
- 验证：ontology-validate.py 通过，图谱 islands:0

## 修改节点 2：ontology/domain/ai-efficiency-knowledge-assets-and-ai-workflow.md
- 原 testable_signal: 由领域实践与测试验证
- 新 testable_signal: 检查资产 source_ids 非空且可追溯至 Evidence/Experience，并对抽样查询执行 retrieval/groundedness/relevance/completeness 四维评估达标，缺失来源链或任一维度未通过时报告具体资产与维度
- 派生模式：收敛验证 + 属性断言
- 验证：ontology-validate.py 通过，图谱 islands:0

两个节点均保持 frontmatter 合法、relations 不变，signals 已具体化可直接派生断言脚本。
