# Triage Brief: T0162 抓包验证 NBU DTE 协商机制

## 分类

- 类别: enhancement
- scenario_type: research
- 请求: 验证"单端口同时支持 TLS 与明文"结论的实证性

## 查重结果

| 来源 | 内容 | 与本次关系 |
|------|------|-----------|
| T0148 (0731-nbu-transfer-encrypt-research) | DTE 全量调研，confirmed | **前置任务**；其 conclusion.md 明确留待办："可在测试环境运行一次抓包验证 DTE TLS 1.2 握手证书详情" |
| R0084 (0727-nbu-encryption) | 传输加密配置综述 | 背景，不冲突 |
| knowledge/nbu/nbu-dte-architecture.md | DTE 架构沉淀 | 结论应回写此处 |

**结论**: 非重复任务，是 T0148 明确遗留的增量验证步骤。

## Claim 验证

T0148 已实证:
- DTE=On 作业存在（bpdbjobs DTEMode=On）
- bpbrm 符号 vnet_set_dte_mode_in_tss / inapp_tls_enabled_for_snap_backup（连接级协商存在）
- 通信矩阵 13782 端口标注 IN-APP-TLS/vnetd 双路径

未实证（本次目标）:
- 明文协议头存在性与魔数
- TLS 升级时序（明文头后跟 ClientHello）
- 同端口明文连接无 TLS 握手
- DTE 配置动态生效（无需重启）的直接观测

## 信息缺口

- 无。抓包方法、环境、命令均已明确（见 prd.md）。

## 推荐下一步

1. Plan 阶段完成 P1-P6（用户终审）
2. Do: 抓包 + 分析 + AC-4 动态生效实验
3. 结论回写 knowledge/nbu/nbu-dte-architecture.md
