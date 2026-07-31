# T0121 审查报告：门禁和核心技能的 AI 友好度

## 审查范围

| 文件 | 行数 | 职责 |
|------|------|------|
| advance-phase/SKILL.md | 36 | 阶段转换门禁 |
| grilling/SKILL.md | 53 | 追问对齐 |
| register-evidence/SKILL.md | 19 | 证据登记 |
| verify-convergence/SKILL.md | 13 | 收敛验证 |
| write-conclusion/SKILL.md | 35 | 结论撰写 |
| write-journal/SKILL.md | 33 | 工作日志 |
| handoff/SKILL.md | 23 | 会话交接 |
| to-tickets/SKILL.md | 48 | 任务拆解 |

## 逐项评分（1-5）

### 3. 门禁自检 — 总分：3.6/5

| 文件 | 评分 | 分析 |
|------|------|------|
| advance-phase | 3 | 四阶段门禁逻辑清晰但以自然语言描述，无可执行校验脚本；`do→check` 仅检查 manifest 存在性而非内容完整性；校验逻辑分散在 advance-phase 和各 flow 中 |
| grilling | 4 | 规则明确，三类场景追问清晰；但无"所有分支走完"的自动检测标准，依赖 AI 判断 |
| register-evidence | 4 | 命令明确可预期；无自动验证复制是否成功 |
| verify-convergence | 4 | 逻辑清晰；`meta.convergence` 为空时行为未定义 |
| write-conclusion | 4 | 完成条件明确；无 schema 校验 |
| write-journal | 3 | Mode A 依赖 disposition 存在但无跳过机制 |
| handoff | 3 | 完成条件模糊（"总结当前会话"标准不明确） |
| to-tickets | 4 | ID 扫描逻辑明确；"拷贝相关章节"依赖 AI 判断 |

### 4. 工具对齐 — 总分：3.5/5

| 文件 | 评分 | 分析 |
|------|------|------|
| advance-phase | 3 | 基本操作为编辑 JSON（edit/write），但无辅助校验脚本或命令 |
| grilling | 3 | 主要使用 question 工具对齐良好，但"走决策树"是抽象概念，实现差异大 |
| register-evidence | 5 | 完美对齐 bash 工具，命令即执行 |
| verify-convergence | 3 | 需 AI 自行读取 JSON 比对，无辅助脚本 |
| write-conclusion | 4 | 模板+JSON 格式明确，需写两处稍繁琐 |
| write-journal | 4 | 两种模式清晰，格式明确 |
| handoff | 3 | `disable-model-invocation: true` 是非标准语法；去敏标准依赖 AI |
| to-tickets | 4 | 完整 JSON 模板，但"拷贝相关章节"需 AI 自行判断 |

### 6. 容错与恢复 — 总分：2.5/5

| 文件 | 评分 | 分析 |
|------|------|------|
| advance-phase | 2 | 无回滚机制；无部分推进支持。仅有基础的"找不到则终止" |
| grilling | 3 | 有 blocking issue 出口；用户不回复无超时处理 |
| register-evidence | 3 | mkdir -p 自动创建目录；artifact 路径错误无校验 |
| verify-convergence | 2 | 缺失时"报告用户"但无重试/恢复路径定义 |
| write-conclusion | 3 | 写入两处有一处失败时无回滚策略 |
| write-journal | 2 | 前置条件不满足时终止，无替代方案 |
| handoff | 2 | 单次写入，无校验和重试 |
| to-tickets | 3 | 子任务创建后父任务更新失败无回滚 |

## 不友好之处定位与严重程度

| # | 位置 | 问题 | 影响 | 严重度 |
|---|------|------|------|--------|
| G01 | advance-phase:9-31 | 门禁条件为自然语言描述，无可执行校验 | AI 自主校验误差，阶段推进错误 | **高** |
| G02 | advance-phase:all | 无回滚机制 | 误推进后无法回退 | **高** |
| G03 | handoff:4 | `disable-model-invocation: true` 非标准语法 | 部分 AI 模型忽略此标记 | 中 |
| G04 | verify-convergence:1-13 | meta.convergence 为空时行为未定义 | 边界情况下校验跳过 | 中 |
| G05 | advance-phase:16 | do→check 仅检查 manifest 存在性 | 可登记空清单绕过校验 | 中 |
| G06 | write-journal:11 | Mode A 无跳过 disposition 的机制 | disposition 未设置时阻塞日志写入 | 低 |
| G07 | grilling:6-15 | "走决策树"无自动完成检测 | AI 可能提前退出追问 | 中 |
| G08 | to-tickets:41 | 父任务更新失败无回滚 | 子任务创建后父任务不一致 | 中 |

## 改进建议

### 高优先级
1. **G01+G04+G05**：将门禁条件实现为可执行的 JSON Schema + 校验脚本，放在 `scripts/validate-gate.sh` 中
2. **G02**：advance-phase 增加 rollback 命令（从当前 phase 回退到上一 phase，附带状态恢复）

### 中优先级
3. **G03**：将 `disable-model-invocation` 替换为标准 frontmatter 或明确说明"需用户主动加载"
4. **G07**：grilling 增加"无新问题可问"的自动检测标准（所有推荐答案已被用户确认过）
5. **G08**：to-tickets 增加事务性 — "创建子任务后再更新父任务，任一失败整体回滚"

### 低优先级
6. **G06**：write-journal Mode A 增加 disposition 不存在时的降级选项
