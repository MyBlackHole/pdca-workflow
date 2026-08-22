---
schema: pdca.asset/v1
id: T0356-0822-libobk-handshake-fix
phase: check
source_ids: [verify-log, impl-diff, asan-log]
---

## 上下文

修复父任务 T0355 发现的 libobk mTLS 握手两项 CRITICAL 缺陷（C1 栈溢出 / C2 帧长度校验必败+越界读），并补齐真实 TLS 往返集成测试。bugfix 场景，TDD 路径。

## 假设与结果

- 假设 H1：帧长度单点宏 + 缓冲区按总长分配可同时消除 C1/C2 → **成立**。`OBK_HS_RESP_BODY_SIZE (4 + OBK_HS_MAX_NAME)` 双端共用后，握手成功路径真实可达（往返用例 tssl 断言通过、echo 链路互通）。
- 假设 H2：新增往返测试对缺陷有判别力 → **成立**。变异测试（服务端发送长度回退 205）立即触发客户端 assert 失败；ASan 构建运行零报告。
- 假设 H3：修复不破坏既有行为 → **成立**。libobk_session_test/libobk_protocol_test/rdbcomm/rpc/dmsbtex 五套件全绿；明文零握手路径不受影响。

## 分析

逐条 AC 判定（证据见 evidence/manifest）：

| AC | 判定 | 证据 |
|----|------|------|
| AC-1 构建+用例全绿含新往返用例 | pass | verify-log：五套件 exit=0 |
| AC-2 双方会话切 TLS 断言 | pass | impl-diff：cio.tssl!=NULL 断言 + 子进程 io.tssl 检查(_exit(3)) |
| AC-3 长度字面量清零 | pass | verify-log：grep 0 处残留，宏引用 7 处 |
| AC-4 ASan 干净 | pass | asan-log：RUN_EXIT=0，0 条 AddressSanitizer 报告 |

B4 双轴审查：标准轴 0 Blocking（memmove 消除重叠拷贝 UB 为额外收益）；规范轴 PRD 全项落实，dmsbtex 未动（范围外遵守）。xmake.lua 测试目标补 compress.c/quickLZ 为 ASan 插桩暴露的真实链接依赖补全。

提交：【B-T0356】libobk: 修复 mTLS 握手栈溢出与帧长度必败, 1.0.0.0 -> 1.0.0.1（commit 582c380，含 bug-commit-format 十要素）。

## 适用边界

- wire 帧长度变化仅影响 mTLS 握手路径；旧版本双端在 mTLS 下本就无法完成握手，无兼容性损失；明文模式字节不变。
- 往返测试为 socketpair 级链接测试，未覆盖真实 TCP + 真实进程部署形态（与知识库 link-level-mtls-test-pattern 同级限制）。
- dmsbtex/rdbcomm 与基准 rpc 的语义收敛项（T0355 H1–H4/M1/M3）不在本任务范围，仍待后续任务。

## 下一轮建议

1. 真实进程级验证：SBT_MTLS_ENABLE=1 下 RMAN→libobk→FileTransferAgent 端到端备份演练（建议并入 0820-tls-session-integration-test 任务线）。
2. 后续任务收敛 T0355 剩余 HIGH/MEDIUM 偏差（错误码语义统一、ca_cn 失败回帧、启动策略 ADR）。

## verdict

- verdict_id: V-T0356-check-01
- outcome: confirmed
- reason: 四条 AC 全部有实证证据支持；变异测试证明测试判别力；五套件回归全绿且 ASan 干净；提交含完整十要素分析与版本号升级。
