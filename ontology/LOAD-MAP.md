# 按需读集

本文件定义 **AI 如何最小化读取当前规则与知识**。它是加载方法，不是第二套规则清单。
当前规则身份以 [INDEX](INDEX.md)、当前 Skill、phase/scene 方法和它们明确引用的当前契约为准。

链接存在、搜索命中、同领域、文件更详细或 frontmatter 含 `authority`，都不等于必须加载或已经采用。

## 开始／恢复

先读最小集合：

1. 当前运行 Skill；
2. 当前项目 context、自己的 task、最后完整事件和待确认 request/response；
3. [共同恢复入口](contracts/entry-recovery.md)。

只有需要解析某个规则 ID 时才查看 [INDEX](INDEX.md) 对应项；不要先把 28 项全部读入上下文。
不要默认扫描 `domain/`、`entity/`、`pattern/`、legacy 或兄弟任务历史。

## 新建正式任务

按事件追加读取：

- TASK-01；
- CAP-01；
- CONFIRM-01；
- 需要真实创建时读 [agent-dispatch](contracts/agent-dispatch.md)。

项目新增或改绑时才读 [project-workspace](contracts/project-workspace.md)。

## 启动阶段

追加读取：

- GATE-01；
- 当前 phase 的 `process/flow-*.md`；
- SCENE-01；
- 当前 scene Skill 中对应阶段方法；
- Plan 已固定、当前阶段确实需要的其他 authority。

不要因为 authority 数量有限就全量注入。阶段方法引用某规则时，再读取该规则。

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

- 恢复失败／压缩：RECOVERY-01；
- 停止／取消：CONTROL-01；
- 实际资源冲突：RESOURCE-01；
- 正式工作节点分解：DECOMP-01；
- 知识复用／采用：REUSE-01、ADOPT-01；
- 写某类 record：先读 [record shape 索引](contracts/record-shapes/index.md)，再只读该具体类型契约。

## 禁止的默认行为

- 不递归加载 `ontology/`；
- 不全量加载 28 个规则 ID；
- 不读取兄弟任务完整历史；
- 不因 reference 更详细就让它覆盖当前规则；
- 不把 retired、legacy、未采用知识放入默认上下文；
- 不用 Python/Shell/测试代码复制一遍 PDCA 语义。

未知引用先定位，未知事实保持 unknown。
