---
schema: pdca.asset/v2
id: ontology:concept/work-dependency-graph
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: DEPENDENCY-01：固定交付依赖的 ready / stale 事实
---

# DEPENDENCY-01：任务输入依赖

DEPENDENCY-01 只回答：**一个 task 真正消费的固定交付/interface 是否可用，以及源变化后哪些消费者输入变 stale。**
它不授权 task/phase、不创建 Agent、不直接改变 execution_state。

## Dependency edge

dependency edge 必须来自能解释的 ontology/work relation，并固定：

- source node / target node；
- 来源 relation；
- consumer 真正需要的 output/interface；
- 固定 version/digest；
- ready 的实际交付证据；
- source 变化时受影响的 consumer refs/evidence。

composition 与 dependency 分开：父“包含”子不等于父一定消费子交付。
只有当前 consumer 确实需要某个固定 output/interface 时才建立数据/产物 dependency。

## Ready

`ready` 只表示：**这个 dependency edge 指向的固定交付当前可作为 consumer 输入。**

它不表示：

- consumer task 已获用户授权；
- phase Gate ready；
- task execution_state=running；
- source task 的完整历史可以被读取。

SCHED-01 可以消费 ready 事实产生 **task creation candidate**。若用户选择创建，走 TASK/CONTEXT/CAP/CONFIRM/agent-dispatch；已存在 task 的 phase 是否可启动，则另走 CONFIRM/GATE。dependency ready 不把这两条链合并。

## Stale

当 source ontology revision、relation、output/interface 或固定 version/digest 变化时，
只把**受影响的 consumer dependency refs、mapping、baseline/evidence** 标为 stale。
历史 evidence 不覆盖或删除，保留它当时对应的旧 subject。

stale 的后续影响按消费者当前时点决定：

- 尚未启动的新 phase：GATE-01 的 freshness/predecessor 检查会阻断旧 subject；
- 正在运行的 phase：如果固定输入已经被实际替换或不再适用，按 CONFIRM/GATE/CONTROL 的边界停止受影响动作；
- recovery：RECOVERY-01 只识别 stale fact 并路由到本规则，不自行重算依赖；
- 新版本采用：按 ADOPT-01 / CONTEXT-01 固定新的 consumer 输入，不静默改写旧 assignment/baseline。

## Context consumption

CONTEXT-01 对 dependency 只读取 consumer 真正需要的固定 deliverable/interface、relation、version/digest 与 limitation。
不读取 source task 的完整 Plan/Do/Check/Act 历史，也不用 source PASS 代替 consumer 自己的验证。
