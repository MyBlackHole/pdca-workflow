# 【F】工具级多场景 e2e 测试 — 规格文档

## 问题陈述

- **现状**: TLS 栈连续改造（T0387/T0388/T0390/T0394）后缺乏跨工具、跨场景的系统级回归手段；首跑即发现 rdbcomm mTLS 永久失败缺陷（T0394）。单测因 mock 层无法覆盖真实 send/recv 路径。
- **目标**: 一份可重复执行的 e2e 测试脚本（test/e2e_tool_scenarios.sh），覆盖 aio-speed 与 rdbcomm 工具对的双算法、mTLS 开关、fail-closed、keygen 工具链场景，输出 PASS/FAIL 矩阵。
- **差距**: 无自动化 e2e；场景靠手工零散验证。

## 解决方案

1. bash 脚本驱动真实二进制（非 mock）：自管服务端实例生命周期（独立端口、setsid 启动、用后回收）；
2. 场景矩阵：
   - S1 aio-speed mTLS SM4 默认算法
   - S2 aio-speed mTLS AES 显式算法
   - S3 aio-speed 明文客户端 ↔ 明文服务端（独立实例 mtls=0）
   - S4 fail-closed：明文客户端连 mTLS 服务端必须被拒
   - S5 fail-closed：无效算法名必须被拒
   - S6 异常端口连接快速失败（无挂起）
   - S7 rdbcomm mTLS SM4（T0394 回归锚）
   - S8 rdbcomm 明文模式
   - S9 keygen 非法 CN（含空格）拒绝退出非零
   - S10 keygen create+sign -n 自包含目录（CA 拷贝存在）
3. 断言基于命令输出关键字与退出码（管道取码用 PIPESTATUS 或免管道）；
4. 报告落盘任务 records。

## Seam 分析

### 声明的测试接缝
- seam: test/e2e_tool_scenarios.sh -> rpc/rpc-io.cpp
- seam: test/e2e_tool_scenarios.sh -> rdbcomm/server.c
- seam: test/e2e_tool_scenarios.sh -> libs/tls_cert.c

### 验收可测性
- 每场景独立 PASS/FAIL；脚本汇总退出码非零当有 FAIL。

## 用户故事

1. 作为 `维护者`，我想要一条命令跑完安全栈关键场景，以便改造后立即发现回归。

## 实现决策

- 服务端实例使用临时 workdir/log，固定测试端口段（16610-16612）避免污染现网 6610/6611。
- 复用 /opt/aio/cfg/certs 现网证书（T0391 规范化后的双 CA 体系）。
- 脚本幂等：启动前清理同端口残留实例。

## 测试决策

- 本任务产物即测试；Do 中实跑并修正脚本至全绿（S 类失败若为产品缺陷则立项修复，不在本任务内改产品码）。

## 验收标准

- [ ] AC-1: test/e2e_tool_scenarios.sh 落盘且可重复执行（连跑两次结果一致）
- [ ] AC-2: 场景矩阵 S1-S10 全部 PASS 并输出汇总报告
- [ ] AC-3: 报告落盘任务 records 目录且含每场景断言依据（输出关键字/退出码）

## 范围外

- 产品代码修改（发现缺陷另行立项，如 T0394 先行修复的 rdbcomm 缺陷）
- 性能/压力场景

## 备注

- 前置依赖：T0394 已修复 rdbcomm mTLS（合流回归）；现网证书已规范化（T0391）。
