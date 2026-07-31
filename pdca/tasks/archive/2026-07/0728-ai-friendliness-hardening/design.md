# T0135 设计：可验证 AI 友好度协议

## 1. 边界

系统分成四个可独立验证的模块，父任务只编排共同合约与最终证据：

| 模块 | 输入 | 输出 | 禁止事项 |
|------|------|------|----------|
| 状态合约 | task、clarification、evidence、conclusion 元数据 | schema 校验结果、transition receipt、清理 dry-run manifest | 未冻结 schema 前删除；只凭文件存在通过 |
| 能力与入口 | 环境、frontmatter、本地引用 | doctor 报告、能力映射、生成索引 | 在核心 flow 写平台专用分支 |
| 内容量审查 | flow/skill Markdown | 自动指标、rubric、Pareto 候选、配对结果 | 以行数或主观总分单独判定 |
| 确定性评测 | 六类 scenario fixture、故障 fixture | 机器可读结果 | 增加没有当前 runner 的未来协议 |

## 2. 状态模型

允许的 phase 顺序固定为：

```text
plan -> do -> check -> act -> archive
```

跨字段不变量：

| phase | status | active | 必需状态时间 | 核心语义门禁 |
|------|--------|--------|--------------|--------------|
| plan | Pending | true | created、plan | PRD 存在 |
| do | InProgress | true | do | `final_confirmation.response=confirmed` |
| check | Completed | true | check | 有效 evidence manifest 且验收映射完整 |
| act | Completed | true | act | conclusion、verdict、check confirmation 有效 |
| archive | Completed | false | archive | disposition、journal、清理后的终态一致 |

结构校验使用 JSON Schema；引用目标、digest、时间顺序、phase/status 对应关系由语义验证器处理。所有失败返回结构化错误码、对象路径和修复提示。

阶段转换写 transition receipt，绑定转换前 task digest、目标 phase、验证结果和时间。更新采用临时文件后原子替换；重复相同转换返回既有 receipt，参数冲突则拒绝。

## 3. 历史清理数据流

```text
冻结 schema
  -> schema 正反例全通过
  -> 扫描历史 task
  -> dry-run manifest（路径、失败规则、摘要）
  -> protected-path 校验
  -> 保存 manifest 证据
  -> Git 可恢复删除
  -> 重新扫描应为 0 个不合规历史任务
```

受保护前缀固定为 `records/`、`knowledge/`、`pdca/journal/`。清理目标必须是 `pdca/tasks/archive/<年月>/<任务目录>` 或明确确认的重复活跃任务目录；不接受 glob、仓库根目录或未解析变量作为删除目标。

## 4. 能力协议

每项能力包含：

```yaml
name: agent.spawn
required: false
probe: current-environment
fallback: execute-in-main-session
```

首版能力至少覆盖：

- filesystem.read / filesystem.write
- process.exec
- git.versioning
- agent.spawn
- context.retrieve

doctor 先解析 `$PDCA_HOME`，再检查入口引用、运行依赖和能力。required 缺失返回失败；optional 缺失必须显示 fallback。能力结果只描述当前运行环境，不缓存为跨会话授权。

## 5. 技能索引

索引生成器扫描 flow/skill frontmatter，以稳定字段生成机器可读索引和 Markdown 索引。排序按稳定 ID；重复 ID、缺 description、引用不存在或 frontmatter 无法解析均失败。行数不进入长期索引。

## 6. 内容量审查

### 自动指标

- UTF-8 bytes
- 标题数量与最大深度
- 规范化重复片段
- 本地引用扇入/扇出和断链

### 独立 rubric

信息密度、渐进披露、角色表达和错误恢复分别给出定义、锚点样例和证据引用。rubric 结果不得与自动指标相加形成总分。

### 精简接受规则

候选来自 bytes Pareto 前沿和重复热点。每项变更必须同时满足：

1. UTF-8 bytes 降幅 >= 15%。
2. 所有既定确定性夹具通过。
3. 必需输入、输出、门禁、失败处理和适用边界未丢失。

## 7. 评测与证据

六类 scenario 各有正常路径和至少一个故障路径。结果记录 fixture ID、输入 digest、预期、实际、pass/fail、错误码和运行环境。没有当前 runner 的 Agent trial 不纳入本次设计。

## 8. 回滚

- schema/validator：回退提交并恢复 transition 前 task 快照。
- 内容精简：逐文件回退未达 bytes 门槛候选。
- 历史清理：只通过 Git 恢复 dry-run manifest 中的明确路径。
- doctor/index/harness：删除新增生成物并回退对应提交，不触碰保留目录。
