---
schema: pdca.asset/v1
id: 2026-08-07-rpc-conn-idle-implement
phase: check
source_ids: [do]
---

## 上下文

任务 T0226（附于 T0227 研究）：落地 T0227 选定方案中的 **EOF 判定** 部分。
经 grilling 3 轮收缩范围：只修 rpc_recv/socket 层的 EOF 判定，不新增空闲回收、
不新增配置项（理由：服务端已能靠 EOF/read_timeout 回收；idle 主动回收依赖配置，
成本大于当前收益，留待后续）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| rpc_recv 将 nread==0(EOF) 误当错误（AC-1） | 成立并已修：rpc-io.hpp 两处 recv 循环 nread==0 → eof=1 break；结束分支返回 IO_EOF(-3) 且 ErrorLog 降为 InfoLog |
| 网络错误路径不变（AC-2） | 成立：EINTR/EAGAIN→WarningLog+continue；RST/其他→ErrorLog+break；-100/-200/IO_TRUNCATE 返回不变 |
| 调用点行为不变无回归（AC-3） | 成立：IO_EOF<0，`<0`/`<1` 判定均按原退出路径；主循环坏网络 ErrorLog 显式处理 EOF（rpc-server.cpp:221 `bytes==(int)IO_EOF` → InfoLog） |
| 编译回归（AC-4） | 成立：xmake build rpc 通过（librpc.a；IO_EOF 比较用 (int) 强转规避 -Werror sign-compare） |

## 分析

- 核心缺陷确认（与 T0227 AC-6 一致）：空对端正常 close(FIN) 被 recv==0 触发
  `ErrorLog("receive failure...nread:0")` 进而主循环打 `"bad network"`，3 条 Error 噪音。
- 修复：EOF 在 rpc_recv 内识别并上抛专用负值 IO_EOF(-3)；服务端 worker 主循环
  识别 IO_EOF 走干净关闭（InfoLog），不再误打 bad network。
- 收敛：仅 rpc-io.h（+1 枚举）、rpc-io.cpp（EOF 判定）、rpc-server.cpp（主循环
  EOF 分支）3 文件；调用点零改动，符合"只修 EOF"范围。
- 未实现空闲主动回收/idle_timeout 配置（明确移出范围），由 T0227 convergence
  保留，若后续需要另立任务。

## 适用边界

- 面向 F/131 rpc_recv / StartRPCServiceWorker 结构。
- EOF 判定仅覆盖主会话回收循环；其余 rpc_recv 调用点（command/scp 读响应）对
  EOF 仍走原 `<1` 失败分支（语义保守，非本次噪音源）。
- 未做真实网络压力回归；以 xmake 编译 + POC 场景 02（EOF 判定）为参照。

## 下一轮建议

1. 全量回归（rpc/fsbackup 集成）后随版本发布。
2. 若需"客户端空闲主动回收"，基于 T0227 ADR-0016 + 本任务 EOF 通道另立实现任务
   （rpc_conn last_used/idle_timeout + reconn 懒回收 + rpc-config 配置项）。
3. 提交引用 T0227 决策 + 本任务 conclusion。