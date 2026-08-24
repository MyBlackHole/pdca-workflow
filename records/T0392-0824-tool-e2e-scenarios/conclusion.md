---
schema: pdca.asset/v1
id: T0392-0824-tool-e2e-scenarios
phase: check
source_ids: [e2e-script, verify-log]
---

## 上下文

TLS 栈连续四轮改造（T0387-T0390/T0394）后建立工具级 e2e 回归手段。首跑即暴露 rdbcomm mTLS 永久失败缺陷，已由 T0394 先行修复（send_handshake_resp 返回值误判），本任务完成场景矩阵全量回归。

## 假设与结果

- **假设**：真实二进制驱动可覆盖 mock 层盲区。→ **成立**：S7 首跑即抓到单测漏掉的返回值误判缺陷。
- **假设**：脚本可重复执行。→ **成立**：连跑两次 PASS=10 FAIL=0。

## 分析

- **AC-1** ✅ test/e2e_tool_scenarios.sh 落盘且连跑两次结果一致（exit=0，PASS=10 FAIL=0）（e2e-script + verify-log）
- **AC-2** ✅ S1-S10 全 PASS：双算法 mTLS、明文互通、三类 fail-closed、快速失败、rdbcomm 双模式、keygen CN 校验与自包含目录（verify-log）
- **AC-3** ✅ 报告落盘 records/evidence/verify-log，含每场景输出关键字/退出码断言依据（convergence-map）

可复核途径：`test/e2e_tool_scenarios.sh` 直接执行；records/T0392-0824-tool-e2e-scenarios/evidence/verify.log。

## 适用边界

- 依赖现网 /opt/aio/cfg/certs 双 CA 体系（T0391）；证书变更需先恢复该基线。
- S10 会临时生成 E2E_Test_CA 目录并在脚本内清理；中途中断可能残留。
- 端口占用 16610/16611/16613/16614，与其他服务冲突时需调整。

## 下一轮建议

- 场景可持续扩充：CRL 吊销拒绝、证书过期、并发客户端、大输出命令。
- rdbcomm 明文实例当前依赖 RPC_TLS_CERT_DIR=/nonexistent 触发 plain only，若配置语义变化需同步脚本。

## verdict

```json
{
  "outcome": "confirmed",
  "reason": "三条 AC 达成：脚本落盘幂等可跑、十场景全绿、报告留痕",
  "verdict_id": "T0392-verdict-001",
  "at": "2026-08-24T15:52:00+08:00"
}
```
