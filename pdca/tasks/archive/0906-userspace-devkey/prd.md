# 用户态设备密钥管理本体化

## 背景
20 轮规划第 3 轮。解锁策略已建节点；本次覆盖密钥命令、设备管理命令（增删上下线疏散用户态侧）。

## 目标
深挖 key 命令、device 命令；新增至少 2 个不重复 domain 节点。

## 功能需求
1. 深挖 src/commands/key.rs、device 相关命令、src/key.rs 残余，每条带 file:line 佐证
2. 新增至少 2 个 domain 节点，specializes ontology:domain/core，避开 unlock-keyring-policy
3. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析；真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 深挖每条有代码位置佐证
- [ ] AC-2 新增至少 2 个不重复 domain 节点且 frontmatter 合法
- [ ] AC-3 关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增节点）

## 风险与对策
- 风险：与 unlock-keyring-policy 重复。对策：prompt 明确排除解锁策略主题
