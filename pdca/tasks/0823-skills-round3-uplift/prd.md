# skills 三轮借鉴：grilling 非阻塞/git 防护/存量体检 — PRD

## 来源

二轮后第三轮扫描发现三处剩余差距，其中 G3 是把前两轮学到的写作理论反哺自身存量的"自我提升"本体。

## 方案（documentation 场景，三个子项）

### G1 grilling 规则 4 非阻塞并行细化（真实差距）
原版有 "Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait; ask the rest of the frontier now"，PDCA 版规则 4 缺该细节。补：事实探索进行中时仅其下游问题等待，其余 frontier 照常问。

### G2 git 危险命令防护约定（学 git-guardrails-claude-code）
AGENTS.md 沟通与维护约定追加一条 git 安全纪律：禁 --force push/reset --hard/clean -f/branch -D 对本仓库的操作；mv 或批量变更前必须确认目标 phase。不建 hook 机制（平台差异），以纪律条目落地。

### G3 存量资产 no-op/sediment 体检（自我提升本体）
用 writing-great-skills 的杠杆（必要性测试/no-op 判定/沉积检查）对 baseline 内 45 个资产跑一次体检：
- 逐文件扫描可疑行：纯复述他处内容的缓存行、模型默认即遵守的 no-op、与 SSOT 冲突的重复表述
- 产出体检清单（文件/行/问题类型/建议动作），仅记录不直接删除——删除决策留用户或后续任务
- 抽样 3 个最严重文件做 before/bytes-after 对比示例

## 测试接缝声明

### 声明的测试接缝
- seam: 无独立测试——documentation 场景惯例，G3 体检结果以清单证据登记

## 验收标准

- [ ] AC-1: grilling 规则 4 含非阻塞并行细节（探索中仅下游等待）
- [ ] AC-2: AGENTS.md 含 git 危险命令防护纪律条目
- [ ] AC-3: 体检清单覆盖 baseline 全部 45 资产，每条发现含 文件:行/类型/建议；登记 evidence
- [ ] AC-4: 抽样 3 文件完成清理示例且 audit 零 issue；evidence 齐备 convergence valid

## 范围外

- 不删任何行（清理决策留后续）
- 不建 git hooks（平台绑定）

## 备注

baseline 会因 G1/G2 增量再豁免。
