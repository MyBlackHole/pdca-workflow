# 按需读集

本文件定义 **AI 如何最小化读取当前规则与知识**。它是加载方法，不是第二套规则清单。
当前规则身份以 [INDEX](INDEX.md)、当前运行 Skill、phase flow、SCENE-01 和它们明确引用的当前契约为准。

链接存在、搜索命中、同领域、文件更详细或 frontmatter 含 `authority`，都不等于必须加载或已经采用。

## 入口与恢复

任何入口先读当前运行 Skill；随后只按事件追加：

- **`pdca` 定位/绑定**：读取 [project-workspace](contracts/project-workspace.md) 和当前 project context；只有状态/继续/恢复涉及具体 task 时才追加 [entry-recovery](contracts/entry-recovery.md)。
- **`pdca-assist`**：读取 project-workspace、当前项目导航以及形成候选真正需要的 records/获准业务材料；只有候选依赖某个 task 的连续性时才追加 entry-recovery。
- **phase / 已有 scene task**：读取自己的 task、最后完整事件、待确认 request/response 与 entry-recovery。
- **正式 task creation**：依次读取 TASK-01（身份/attempt）、CONTEXT-01（assignment refs）、CAP-01（宿主资格）、CONFIRM-01（具名 creation authorization）与 agent-dispatch（一次原生创建）；创建成功仍等待新 Agent 的 Plan 操作。

只有需要解析某个规则 ID 时才查看 [INDEX](INDEX.md) 对应项；不要先把 28 项全部读入上下文。
不要默认扫描 `domain/`、`entity/`、`pattern/`、legacy、整个 source tree 或兄弟任务历史。
Assist 的“查重/历史拒绝”也只沿当前候选的具体对象和获准读域检查，不构成全项目扫描授权。

## 新建正式任务

按职责读取，不互相替代：

1. TASK-01 固定 task/attempt 的语义身份；
2. CONTEXT-01 选择 minimum sufficient assignment refs；
3. CAP-01 核验当前宿主/配置是否具备所需原生能力；
4. CONFIRM-01 核验用户对该具名 task 的 creation authorization；
5. 只有需要真实创建时才读 [agent-dispatch](contracts/agent-dispatch.md)，执行一次原生创建事务。

项目新增或改绑时才读 [project-workspace](contracts/project-workspace.md)。

## 启动与完成阶段

### phase_start

按职责顺序读取：

1. CONFIRM-01：核对真实用户 response 是否已消费为当前固定 phase/run/subject 的 positive authorization；
2. GATE-01：结合 identity、predecessor、freshness、control、resource/capability 判断当前是否 ready；
3. ready 后按 TRANSITION-01 写入匹配的 `phase_started` receipt；
4. 按 STATE-01 从新事件链投影 `phase=<current>, execution_state=running`；
5. 再执行当前 phase 的 `process/flow-*.md` 与 SCENE-01 中当前 `task.scene` 对应业务方法。

`confirmed` 不等于 ready，ready 也不等于 running；缺少 `phase_started` receipt 时不得仅靠 task 状态字段冒充已启动。

### phase completion

业务方法产生固定结果后：

1. 按 TRANSITION-01 写同 run 的 `phase_completed`；
2. Plan/Do/Check：按 STATE-01 保持最后实际 phase 并投影 `awaiting_confirmation`；可以展示下一固定对象，但不生成授权；
3. Act：不进入 awaiting_confirmation；同一已授权 Act 继续终态收尾，完成后写 `archived` 并由 STATE 投影 `phase=archive, completed`；
4. Act terminalization 若因未知副作用、资源或控制事实无法继续，按 STATE/CONTROL 投影真实 blocked/stopping/interrupted，不请求“第五阶段确认”来掩盖问题。

scene Skill 只在用户显式选择/定位场景时作为入口读取；phase 执行不为取得重复方法再次加载它。
不要因为 authority 数量有限就全量注入；业务方法引用某规则时，再读取该规则。

## 参考知识

Plan/Check 需要领域知识时：

1. 用 REUSE-01 搜索候选；
2. 检查来源、版本、适用性与限制；
3. 只有经 ADOPT-01 固定采用的资产才进入任务输入；
4. reference/retired/legacy 不能授予权限、恢复用户响应、覆盖当前 authority 或复制旧 PASS。

Do-only Work Unit 与独立 review pass 都只接收 minimum sufficient context，不继承整个知识库和父/兄弟活动历史。

## Check

Check 直接读取权威、Plan、真实对象、diff/产物与证据，按 [flow-check](process/flow-check.md)
执行 Scope / Consistency / Adversarial / Evidence 四遍 AI 审查。

**不要创建项目专用 semantic validator 来重新实现 PDCA 规则。**
通用工具可以提供事实；规则解释与符合性判断由 AI 直接完成。

## 事件触发读取

按事实类型只追加对应 authority：

- **恢复／压缩／重启**：RECOVERY-01 只判定原 task/attempt/Agent 连续性；发现未决 control/resource/dependency 后再分别追加对应 authority；
- **pause / cancel / revoke / stop**：CONTROL-01；它只产生停止约束，不替资源结清或新 attempt；
- **资源冲突／取得／撤销／释放／retained**：RESOURCE-01；若有关副作用调用，再只读相关 operation record；
- **dependency output/version ready 或 stale**：DEPENDENCY-01；它只产生输入可用性/失效事实，不授权 task/phase；
- **phase_start**：GATE-01 只消费上述已固定事实，不在 Gate 内重新实现 recovery/control/resource/dependency；
- **正式工作节点分解**：DECOMP-01；
- **知识复用／采用**：REUSE-01、ADOPT-01；
- **写某类 record**：先读 [record shape 索引](contracts/record-shapes/index.md)，再只读该具体类型契约。

不要因为一次 recovery 同时看到了 resource + dependency + control，就把三套规则默认全部加载；
只读取当前阻断或动作真正涉及的那一类。

## 禁止的默认行为

- 不递归加载 `ontology/`；
- 不全量加载 28 个规则 ID；
- 不读取兄弟任务完整历史；
- 不因 reference 更详细就让它覆盖当前规则；
- 不把 retired、legacy、未采用知识放入默认上下文；
- 不用 Python/Shell/测试代码复制一遍 PDCA 语义。

未知引用先定位，未知事实保持 unknown。
