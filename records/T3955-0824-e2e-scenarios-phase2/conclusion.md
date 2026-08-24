---
schema: pdca.asset/v1
id: T3955-0824-e2e-scenarios-phase2
phase: check
source_ids: [verify-log]
---

## 上下文

一期矩阵（S1-S10）落地后的进阶扩充：CRL 吊销、并发、大输出、双算法交替、rdbcomm AES。

## 假设与结果

- **假设**：CRL 场景可用 openssl 迷你 CA 工具化构造。→ **成立**：S11 独立临时 cert_dir + crl.pem，被吊销客户端被 fail-closed 拒绝。
- **假设**：并发断言可靠。→ **修正一次**：后台子 shell 变量递增不回传父进程（bash 语义），改为文件计数后 6/6 通过——属脚本缺陷非产品问题。

## 分析

- **AC-1** ✅ 脚本扩展至 S16，连跑两轮 exit=0 且 PASS=16 FAIL=0（verify-log）
- **AC-2** ✅ 一期 S1-S10 零劣化全 PASS（verify-log）
- **AC-3** ✅ S11 CRL 拒绝 / S12 无效目录兜底 / S13 并发 6/6 / S14 5000 行完整 / S15 交替 6/6 / S16 rdbcomm AES 全部 PASS（verify-log）
- **AC-4** ✅ 报告落盘 records/evidence/verify-log（convergence-map）

可复核途径：`test/e2e_tool_scenarios.sh`；records/T3955-0824-e2e-scenarios-phase2/evidence/verify.log。

## 适用边界

- S11 依赖系统 openssl ca 子命令与 SM2 签发能力；S13 并发度固定 6（更高并发需调参）。
- 二期场景运行时长增加约 40s（CRL 构造与交替轮次）。

## 下一轮建议

- 证书过期边界（时间旅行不可行，可考虑 keygen 支持 --not-before 参数后覆盖）。
- 多实例混合端口矩阵参数化（当前固定端口段）。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "四条 AC 达成：十六场景全绿且幂等，安全语义(CRL/fail-closed)与稳定性(并发/大输出/交替)均有自动化锚点",
  "verdict_id": "T3955-verdict-001",
  "at": "2026-08-24T16:30:00+08:00"
}
```
