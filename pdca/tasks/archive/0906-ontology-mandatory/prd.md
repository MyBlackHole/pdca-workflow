# 本体Act强制产生流程改进

## 背景
用户要求修改 PDCA 流程：本体在 Act 阶段强制产生，适用于全部任务（仅自举任务豁免），取消 records-only 通道。授权方式：立项改进任务。

## 目标
flow-act、skill-research、pdca_core.py、check-research-ontology-settlement.py 四处取消 records-only，自举豁免保留；全量回归验证通过。

## 功能需求
1. flow-act.md 步骤 30：改写知识处置，取消 records-only，要求新建/更新本体节点（自举除外）
2. skill-research.md 本体沉淀决策节：分流判定改为强制本体化，保留判定记录格式
3. pdca_core.py disposition_ontology_issues：records-only 改为拒收（保留 ontology_exempt 自举豁免）
4. check-research-ontology-settlement.py：同步拒收 records-only
5. 全量 ontology-validate.py + 门禁回归验证通过

## 非功能需求
- 真实时间戳；改动可 diff 审计；不破坏现有已归档任务校验（只影响新转换）

## 验收标准
- [ ] AC-1 四处改动完成，records-only 通道关闭，自举豁免保留
- [ ] AC-2 全量 ontology-validate.py 0 issues
- [ ] AC-3 门禁回归：records-only fixture 被拒，自举豁免通过，既有归档任务不受影响
- [ ] AC-4 T0512 按新流程可归档（新建节点后通过）

### 声明的测试接缝
- seam: scripts/pdca_core.py -> disposition 门禁（records-only 拒收）
- seam: scripts/ontology-validate.py -> ontology/process/flow-act.md（流程节点合法）

## 风险与对策
- 风险：改坏门禁致全仓库任务卡死。对策：改前备份，改后全量回归 + 既有归档任务抽查
- 风险：历史 records-only 任务被追溯拒收。对策：门禁只校验当前转换，不重跑历史
