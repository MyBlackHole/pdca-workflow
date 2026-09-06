# 老节点信号治理I（journal/alloc系）

## 背景
20 轮规划第 8 轮。历史 core-* 节点 testable_signal 多为泛化模板。本轮治理 journal/alloc 系 8 个。

## 目标
将 8 个老节点的泛化信号改写为可执行句式（运行/通读+对象+判定），不改其他内容。

## 功能需求
1. 逐节点 Read 正文，按正文主题定制信号（非模板套话）
2. 只改 testable_signal 行，不动 id/relations/正文
3. 全量 ontology-validate.py 0 issues

## 非功能需求
- 真实时间戳；改写前后 diff 可审

## 验收标准
- [ ] AC-1 8个节点信号全改写为可执行句式
- [ ] AC-2 diff 仅涉及 testable_signal 行，语义不变
- [ ] AC-3 validate 全量 0 issues
- [ ] AC-4 无新增泛化信号（抽查）

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（改动节点）

## 风险与对策
- 风险：改坏 frontmatter。对策：逐个改写后即时 validate
