---
schema: pdca.evidence-index/v3
task_id: null
revision: 0
entries: []
protocol_revision: 3.4.10
---

# 证据索引

空索引不是执行成功证明。每条entries使用如下逻辑字段，逐项从实际资料填入：

| 字段 | 实际要求 |
|---|---|
| evidence_id | 当前任务内唯一标识 |
| evidence_type_ref | 实际存在的evidence类型节点 |
| source_ref | 工具回执、来源版本或可定位原始记录 |
| artifact_ref | 获授权的固定产物位置 |
| digest | 真实读取字节计算的摘要 |
| result | 真实观察/失败/未执行情况 |
| ac_ids | 支持或反驳的AC列表 |
| supersedes | 更正时引用旧版本，不抹掉原始事实 |

## AC覆盖映射

| AC ID | 证据ID/失败或未执行说明 | 当前观察 | 局限 |
|---|---|---|---|

映射本身不能证明业务通过。实际测试日志需保存命令、工作目录、版本、退出状态和原始输出。
