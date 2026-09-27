---
schema: pdca.asset/v2
id: ontology:concept/task-control
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: CONTROL-01：取消、撤权、暂停与安全停止
---

# CONTROL-01：控制事实优先于新业务动作

CONTROL-01 只定义 **pause / cancel / revoke / stop 等控制事实的语义与优先级**。
它不释放资源、不重试 operation、不创建新 attempt，也不直接写 phase transition。

## 控制事实

控制必须有可信原生来源和真实顺序。文件 mtime、Agent 自填时间、父 Agent 转述都不能单独裁定
“phase_start 与撤权谁先发生”。

- **pause**：暂停新增业务动作，保留当前事实，等待用户后续决定；
- **cancel**：终止当前 task/attempt 的继续执行意图；
- **revoke**：撤销此前授予的特定权限/作用域；
- **system stop**：宿主/安全边界要求立即停止新增动作。

收到已经生效的 stop/cancel/revoke 后，不再开始新的业务副作用；
但允许在原安全范围内执行**止损、对账、证据保全、资源撤销/隔离**，这些不是新的业务目标。

## 与其他规则的边界

- 用户授权是否仍匹配固定 phase_start：CONFIRM-01 / GATE-01；
- stopping/interrupted 状态如何显示：STATE-01；
- 资源 revoking / released / retained：RESOURCE-01；
- unknown operation 如何对账：operation record + RESOURCE-01；
- 新 attempt 是否可创建：TASK-01 / CONFIRM-01。

CONTROL 只产生“当前控制事实必须被尊重”的约束，不替这些规则完成各自工作。

## 停止完成

安全停止完成必须有真实依据：在途 operation 已 settled/隔离，资源已按 RESOURCE-01
进入 released 或 retained，必要证据已固定。仅仅会话消失、父 Agent 不再轮询、租期到期或 task 文件写 completed
都不能证明副作用已经停止。

已 completed 的 attempt 收到迟到控制消息只作审计，不复活；
interrupted attempt 也不因新消息自动继续或创建新 attempt。
