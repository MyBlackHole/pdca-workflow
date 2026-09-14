---
schema: pdca.asset/v2
id: ontology:concept/pdca-recovery
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-14'
summary: RECOVERY-01：每次恢复先核对，不靠对话记忆
---

# RECOVERY-01：每次恢复先核对，不靠对话记忆

恢复从PDCA_ROOT/records中的具名项目context读取固定根与集中协议快照，定位自己的task、dispatch原生身份、最后完整事件、当前run、待请求／响应／消费、固定输入和未决操作。只读本任务及明确采用材料，不载入其他任务完整对话。

先核对原会话能够继续且状态完整；恢复返回新实例或同ID失去状态均阻断。不能用新spawn替代resume。压缩摘要只保存指针、当前目标、未决项和已知限制，不能用它代替真实确认、写权或本体源。

| 已有事实 | 恢复行为 |
|---|---|
| 阶段完成且下一阶段未批准 | 维持等待，展示原待确认目标 |
| 当前run已启动未完成 | 核对原授权仍有效及operation状态，原Agent继续该run |
| 请求已有合法消费但未开始 | 重新核对固定对象和撤权后幂等处理，不产生第二run |
| completed／interrupted | 只读；不复活，不因新消息自动创建attempt |
| 输入漂移／链分叉／未决业务结果 | 阻断对应操作，保全证据并对账 |

宿主级发现入口或用户显式Skill调用必须真实加载并测试；没有原生重载能力时明确要求用户显式调用pdca继续。文档中的“先读状态”不是永不遗忘保证。项目index是派生导航，不覆盖任务事件；索引丢失可由具名任务记录重建，不据目录数量推断完成。根不可访问时阻断，不新建本地.pdca或第二个中心。入口升级不改变原task的规则快照；跨版本只定位，不混用新的阶段方法。
