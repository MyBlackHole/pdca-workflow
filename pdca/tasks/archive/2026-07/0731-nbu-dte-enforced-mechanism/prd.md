# PRD: NBU 强制加密（Enforced）服务端实现机制与重启需求调研

> 任务: T0163 | 类型: research | 创建: 2026-07-31

## 问题陈述

T0148 已确认 Enforced 模式的**决策层**行为（全局 Enforced → 客户端 Off/<9.1 → 作业失败，错误码 8301/8308/8310/8311/8314），T0162 已实证单端口协商机制与"Preferred On 动态生效"。

但以下**服务端实现机制**尚未调研：
1. 全局 DTE 模式（含 Enforced）在服务端的**存储与下发链路**（nbseccmd → EMM → nbjm → bpbrm？）
2. `refreshDteCache`（nbjm 端 DTE 缓存）的**缓存窗口与失效时机**——是否意味着 Enforced 有生效延迟？
3. Enforced 模式下服务端是否有**独立强制守卫**（拒绝明文连接的执行点），还是仅依赖作业启动时决策？
4. **修改为 Enforced 后是否需要重启服务端**——与 Preferred On 有何不同？
5. 强制加密与"禁用不安全通信"（insecurecommunication off，官方文档要求重启）的关联

## 验收标准

- [ ] AC-1: 完整绘制 Enforced 配置的存储/下发/执行链路（配置变更 → 生效的执行点）
- [ ] AC-2: 明确 refreshDteCache 的缓存机制：缓存内容、刷新时机、是否存在延迟窗口
- [ ] AC-3: 明确强制守卫的执行点：明文连接在何处被拒绝（作业调度期 or 连接建立期）
- [ ] AC-4: 给出"修改为 Enforced 后是否需要重启"的明确结论（含与 Preferred On 的差异）
- [ ] AC-5: 澄清 Enforced 与 insecurecommunication off 的关系
- [ ] AC-6: 结论回写知识库 `knowledge/nbu/nbu-dte-architecture.md`

## 范围

**目标环境**: nbusvr103 (10.6.67.187) + nbumed103 (10.6.67.251), NBU 10.3.0.1
**方法**: 静态分析（nbjm/bpbrm/nbseccmd 二进制符号与字符串）+ 官方文档（SecEncryp/AdminGuide）+ 现有日志
**不做**: 不在生产环境切换 Enforced 模式（避免作业失败影响）；不修改配置

## 备注

- 依赖 T0148 符号表（refreshDteCache、emmlib_QueryMediaDTESetting、g_dte_mode 等）
- 若静态分析不足以确认缓存窗口，可分析 nbjm 日志中的 DTE 决策时间点
