# 用户态挂载体系本体化

## 背景
20 轮规划第 1 轮。T0490 深挖用户态 mount 15 条机制但未建本体（除解锁策略外）。本次将挂载体系沉淀为本体节点（基于本地现树旧形态核实）。

## 目标
深挖 mount 降级问答、设备扫描、等盘机制；新增至少 2 个不重复 domain 节点。

## 功能需求
1. 深挖 src/commands/mount.rs、device_scan.rs、wait_devices.rs，每条带 file:line 佐证
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
- 风险：本地 main 落后，v1.39.3 重构未合入。对策：按现树核实并在节点正文中注明形态版本
