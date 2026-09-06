# 老节点信号治理II（btree/snapshot/fsck系）

## 背景
20 轮规划第 9 轮。治理 btree3/snapshot1/fsck3 共 7 个泛化信号。

## 目标
7 个老节点信号改写为可执行句式，不改其他内容。

## 功能需求
1. 逐节点 Read 正文定制信号
2. 只改 testable_signal 行
3. 全量 ontology-validate.py 0 issues

## 非功能需求
- 真实时间戳；diff 可审

## 验收标准
- [ ] AC-1 7个节点信号全改写为可执行句式
- [ ] AC-2 diff 仅涉及 testable_signal 行，语义不变
- [ ] AC-3 validate 全量 0 issues
- [ ] AC-4 无新增泛化信号（抽查）

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（改动节点）

## 风险与对策
- 风险：改坏 frontmatter。对策：改写后即时 validate
