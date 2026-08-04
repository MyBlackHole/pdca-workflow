# Triage Brief: T0163 NBU 强制加密服务端机制调研

## 分类

- 类别: enhancement
- scenario_type: research
- 请求: NBU 强制加密参数的服务端实现机制 + 重启需求

## 查重结果

| 来源 | 覆盖内容 | 缺口 |
|------|---------|------|
| T0148 (DTE 全量调研) | Enforced **决策层**：bpbrm 状态机、错误码 8301-8314、降级链 | ❌ 服务端存储/下发链路、缓存窗口、强制守卫执行点 |
| T0162 (抓包实证) | 单端口协商机制、dte_mode 字段、Preferred On 动态生效 | ❌ Enforced 与 Preferred 的生效差异、insecurecommunication 关联 |
| knowledge/nbu/nbu-dte-architecture.md | 四层决策矩阵、错误码 | ❌ 同上 |

**关键线索（未调研）**: `refreshDteCache`（nbjm 端 DTE 缓存）——若存在缓存窗口，Enforced 生效可能有延迟，直接影响"是否需要重启"的答案。

## Claim 验证

- T0148 符号表确认 `nbjm::JobManager::refreshDteCache()` 存在（决策点 1）
- 官方文档确认"禁用不安全通信需重启主服务器服务"（SecEncryp Guide）
- 但 Enforced 切换是否需重启：**无明确答案**（文档未直接说明，需静态分析+日志佐证）

## 信息缺口

- nbjm DTE 缓存的具体刷新时机（作业调度时？定时？配置变更事件？）
- Enforced 的强制守卫位于调度期还是连接期
- EMM 中 DTE 配置的存储结构

## 推荐下一步

1. Plan 阶段 P2 方向确认 + P6 终审
2. Do: 二进制静态分析（nbjm/bpbrm/nbseccmd strings+nm）+ nbjm 日志时间线 + 官方文档
3. 结论回写 knowledge/nbu/nbu-dte-architecture.md
