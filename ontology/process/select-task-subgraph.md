---
schema: pdca.asset/v2
id: ontology:process/select-task-subgraph
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 4.0.0-rc.5
dcterms_modified: '2026-09-27'
summary: CONTEXT-01：按本体关系选择任务最小必要子图，隔离父兄弟活动上下文
---

# CONTEXT-01：选择正式 task 的 minimum sufficient context

CONTEXT-01 只回答：**这个正式 task 初始需要哪些固定输入，以及默认不应继承什么。**
Task 身份由 TASK-01 定义，宿主 fresh 能力由 CAP-01 判断，实际创建由 agent-dispatch 执行。

初始上下文是工作起点，不是事实发现上限；必须区分：
**initial context / allowed read scope / allowed write scope**。

## 根 modeling bootstrap

唯一 root modeling bootstrap 尚无 ontology subgraph。其 initial context 只包含：

- 用户确认的 root goal seed；
- 允许的事实来源；
- 已明确采用的复用定义；
- 项目绑定；
- 当前 modeling / PDCA 必要 authority；
- 当前创建授权引用。

不得因为尚无 node 就默认传整个 ontology、source tree、project history 或父 conversation。
root modeling Act 固定 node/revision 后，后续 task 使用下面的普通规则。

## 普通 ontology-backed task

从 TASK-01 已固定的 node/revision/scene 与相关 dependency refs 开始，而不是从父 conversation 开始。
按实际语义关系加入：

1. **current node**：定义、work instance、responsibility、I/O、constraints、AC；
2. **parent boundary**：直接 parent seed、composition relation、当前职责所需共享接口；
3. **required relation endpoints**：解释当前 I/O/constraint 必需的具名端点；
4. **dependency deliverables**：当前 task 真正消费的固定 interface/version/output；
5. **shared invariants**：明确适用于当前 node 的跨节点约束；
6. **original requirements**：当前 node/scene 要覆盖的用户需求与来源；
7. **scene inputs**：model 的事实/复用定义，implement 的固定 model/mapping/写域，
   verify 的固定 requirement/model/implementation/mapping/行为证据；
8. **current-event authority**：按 LOAD-MAP 只加入当前创建/phase/资源/恢复事件需要的规则。

关系存在不等于必须读取另一端全部内容；只取完成当前语义所需的端点定义或固定交付。

## 默认排除

除非当前 task 能说明具体用途，否则不加入：

- 整个 ontology 或 source tree；
- 父/兄弟完整 conversation 和 phase 活动历史；
- sibling 的临时假设、调试日志或中间思考；
- unrelated ontology branches；
- 未经 REUSE/ADOPT 的 reference；
- 仅因为“以后也许有用”的项目历史或共享记忆。

上下文质量以“足以执行当前职责且没有无关活动历史”判断，不以 token 数越少越好。

## 落地

不创建 `subgraph.json`、ContextManifest 或平行 schema。
选择结果直接写入现有 refs：

- task：语义身份与顶层 context refs；
- assignment：实际传给 fresh Agent 的 input/definition/context refs；
- baseline：Plan 后冻结的输入/定义 refs；
- evidence：运行期间实际核验的补充对象与来源。

每个 ref 必须能说明用途、固定版本/摘要和角色；无法说明用途的材料不默认加入。

## 运行中追加事实

执行中可沿实际调用、配置、行为证据或反例的**具体线索**读取获准范围内的具名材料，
但新增读取不反写原 assignment/baseline，也不自动扩大 write scope。

补充事实与替换固定输入必须区分：
切换模型/依赖版本、改变 task 对象、目标、AC/oracle 或计划时，按 CONFIRM-01 重新沟通；
未采用 reference 仍只按 REUSE/ADOPT 处理。

发现新 ontology responsibility 时先按 EVOLVE-01 形成 model revision candidate；经 TREE/NODE 与 Modeling Act 固定成正式 node 后，才由 DECOMP-01 形成 task seed candidate。CONTEXT 不把草稿 responsibility 直接升级成 task。
Do-only Work Unit 的局部 context 由 CONTRACT-01 从本 task context 继续切片；
恢复/压缩由 RECOVERY-01 重新读取原 refs，不由 CONTEXT-01 定义另一套恢复摘要。
