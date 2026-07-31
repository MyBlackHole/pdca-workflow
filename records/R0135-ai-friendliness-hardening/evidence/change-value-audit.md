# T0135 变更价值门禁

判定规则：每个变更必须直接改善 AI 的门禁正确率、导航成功率、上下文成本或故障恢复，并有当前可运行的验证；否则终止并删除。

## 保留项

| 变更组 | 文件/资产 | AI 提升 | 验证信号 | 判定 |
|--------|-----------|---------|----------|------|
| 严格状态合约 | `schemas/task*`、clarification/evidence schema、`pdca_core.py`、validate/transition wrappers | 拒绝伪确认、空证据和矛盾状态，提高阶段判断准确度 | schema 正反例、确认拒绝、未来时间戳和 archive 矛盾测试通过 | 保留 |
| 原子推进与恢复 | `transition-phase.py`、`rollback-phase.py`、advance-phase skill | 减少直接改 JSON、非相邻推进和错误回滚 | 相邻转换、receipt、重复调用幂等测试通过 | 保留 |
| 历史安全审计 | `audit-history.py`、deletion manifest | 防止 AI 用宽泛 glob 或错误恢复假设删除数据 | 13 个具体目标；识别 11 个不可 Git 恢复并默认拒绝 apply | 保留 |
| 入口 doctor | `pdca-doctor.py`、capabilities、AGENTS 入口 | 首次进入自动发现断链、必需能力和 fallback | doctor valid；missing references=0；agent/context fallback 明确 | 保留 |
| 单一技能索引 | generator + `SKILLS-INDEX.md` | 减少入口断链和手工索引漂移 | 41 个资产；重复生成检查通过 | 保留 |
| 平台能力解耦 | flow-do、flow-plan、code-review、context-retrieval、to-tickets、wayfinding-chart | 避免 AI 调用不存在的 `task()`/`pdca context` | 活跃 flow/skill 中上述硬编码为 0；doctor 提供 fallback | 保留 |
| 内容成本审查 | bytes/结构/重复/引用脚本、rubric、测试 | 用客观门槛删除高成本内容，避免“越短越好”主观化 | 两次运行一致；断链=0；Pareto 候选可复现 | 保留 |
| flow-plan 精简 | `flows/flow-plan/SKILL.md` | 降低 Plan 默认上下文，同时保留 P0–P7、唯一终审和 fallback | 5503→3535 bytes，-35.76%；配对时 10 个测试、当前 13 个测试均通过 | 保留 |
| 六场景 harness | fixture、runner、harness test | 提高优化前后效果判断准确度 | development/bugfix/research/documentation/design/review 共 12/12 通过 | 保留 |
| 术语与 ADR | CONTEXT、ADR-0002、capability protocol | 统一严格 schema、能力与成本术语，避免子任务解释分叉 | doctor 引用完整；四子任务使用相同定义 | 保留 |
| PDCA 任务与证据 | T0135–T0139 PRD/design/clarifications/evidence | 约束范围、删除门禁、回滚和结论来源 | final_confirmation、scope_change、配对和 dry-run 证据可追溯 | 保留 |
| 固定运行依赖 | `requirements-audit.txt` | 避免 schema/YAML 解析版本漂移导致 AI 校验不一致 | 当前测试在声明版本下可运行 | 保留 |

## 已终止并删除

| 删除项 | 删除原因 |
|--------|----------|
| `tiktoken` 依赖与参考 token 指标 | 与 bytes 得到完全相同 Pareto 候选；增加 Python/Rust/网络兼容成本 |
| Unicode 字符指标 | 候选集合与 tokenizer 不一致并漏掉 flow-plan；不提高决策准确度 |
| Agent trial schema、future runner 协议、not-run fixture | 当前没有独立 runner，不产生当前 AI 效率或准确度提升 |
| `network.fetch` 未使用能力 | 本任务没有消费者或验证路径 |
| `skills-index.json` | 没有消费者，与已引用 Markdown 索引重复 |
| baseline/after Markdown 自动报告 | 与 JSON 重复且增加漂移面；保留配对结论和 rubric 即可 |

## 当前限制

- bytes 是内容成本代理，不等同模型真实 token；它被保留是因为零依赖且与 tokenizer 候选实测一致。
- “零回归”只适用于当前确定性夹具。
- 13 个不兼容历史归档目录已按确认 manifest 删除；其中 11 个原本未被 Git 跟踪，删除不可逆。
