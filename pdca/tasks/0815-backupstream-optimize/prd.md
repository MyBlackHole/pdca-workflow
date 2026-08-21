# backupstream 80.0.0 进一步优化 — 规格文档

## 问题陈述

- **现状**: backupstream 80.0.0 架构健康（80 轮 review、构建通过、资格文档齐全），但存在三类可改进点：① 构建存在 1 个 `-Wmisleading-indentation` 警告，与文档"0 warnings"声明不符，且无 -Werror 门禁阻止回归；② 性能指标已有散落量化（ROUND79/80），但无统一、可复现、跨版本对比的专用基准；③ ROUND80 明确标记的下一个架构瓶颈（后续控制帧仍占用阻塞 worker）尚未解决，v81 需要实现后续帧非阻塞化。
- **目标**: 三个方向全部落地：警告清零并建立 -Werror 门禁；新增专用性能基准并建立 v80 基线；实现 v81 控制面后续帧非阻塞化（含必要能力位），性能不回归且资源占用改善。
- **差距**: 门禁缺失、基准缺失、v81 架构演进未实现。

## 解决方案

按「门禁 → 性能 → 架构」顺序推进，各自独立可验收：

1. **门禁修复与警告清零**：修复现有警告（逻辑正确但缩进误导，需改写为明确分支），新增/修改门禁脚本使 `-Werror` 成为构建门禁。
2. **性能/资源量化优化**：新增专用基准测试脚本（覆盖控制面短会话、长 FILE/TREE 传输、背压场景），建立 v80 基线（吞吐/时延/线程数/RSS），量化口径与 ROUND79/80 一致。
3. **v81 架构演进（后续帧非阻塞化）**：公共非阻塞前端在 HELLO 认证后保留后续控制帧，解析出完整 work-ready 请求再分派阻塞 worker；不复制 TREE/FILE 状态机、不削弱每会话有序性；EXEC 维持既有 shard 移交；数据面（Data Lane）保持既有非阻塞架构仅做验证；必要时引入新能力位（协议保持向后兼容）。

## Seam 分析

### 测试接缝
- 门禁修复：构建命令（`make`）本身是接缝——通过编译输出断言零警告；门禁脚本判定 `make` 退出码与警告计数。
- 性能基准：新增基准脚本直接调用既有测试框架（benchmark_data_lanes.sh 等）模式，被测模块为 Agent/backupctl 端到端路径。
- v81 后续帧非阻塞化：新增集成测试脚本，在既有 `tests/plain_ingress_integration.sh` 模式上扩展，覆盖「HELLO 后发送一个完整操作、再继续发送后续控制帧」的分片/背压/有序性场景；复用既有会话池/弹性/pidfd 回归。
- 协议兼容性：既有 `protocol_version_integration.sh` 与跨版本互操作测试作为回归接缝。

### 声明的测试接缝
- seam: tests/gate_warnings.sh -> src/*.cpp
- seam: tests/benchmark_control_plane.sh -> src/agent_plain_ingress.cpp
- seam: tests/benchmark_data_path.sh -> src/agent_tree_runtime.cpp
- seam: tests/v81_control_frame_integration.sh -> src/agent_plain_ingress.cpp
- seam: tests/plain_ingress_integration.sh -> src/agent_plain_ingress.cpp

### 验收可测性
- 每个 AC 有明确 pass/fail：警告计数=0、基准脚本输出对比表、v81 回归脚本 PASS/FAIL、线程数/RSS 测量值。
- 边界路径可独立构造：分片字节流、背压、慢客户端、超时、断连重试。

## 用户故事

1. 作为部署方，我希望构建门禁在警告出现时直接失败，以便新代码不引入编译警告回归。
2. 作为性能评估者，我希望有一套可复现的专用基准与 v80 基线，以便量化 v81 收益。
3. 作为备份管理员，我希望 Agent 在客户端不发送数据时也不消耗业务工作线程，以便避免慢客户端耗尽 worker 池。
4. 作为开发者，我希望 v81 后续控制帧被非阻塞前端接管，以便单会话不长期占死一个 worker。

## 实现决策

- 门禁：修复 `agent_tree_runtime.cpp` 中 misleading-indentation 分支（改写为显式块）；新增 `tests/gate_warnings.sh` 断言 `make clean && make` 输出零 warning 且 -Werror 门禁生效。
- 基准：新增专用基准脚本，复用既有测试工具（backupstream-event-bench 等）与 benchmark_data_lanes.sh 的执行模式，输出可对比的表格化结果（吞吐/时延/线程数/RSS）。
- v81：在既有非阻塞 ingress 基础上扩展，使认证后后续控制帧留在 ingress/reactor 侧解析，仅将完整 work-ready 操作分派给阻塞 worker；保持每会话有序；引入能力位需通过既有跨版本互操作验证。
- 架构决策需同步记入 ADR。
- 数据面（Data Lane）保持现状，仅验证并发不回归。
- 兼容性：协议保持向后兼容，新增能力位必须协商降级。

## 测试决策

- 好的测试定义：门禁测试只断言构建无警告；基准测试只测端到端外部行为（吞吐/时延/资源）；v81 回归测试只测行为（分片重构、背压、有序、超时、断连），不测实现细节。
- 被测模块：构建系统、Agent 非阻塞前端、会话池、work pool。
- 现有先例：tests/plain_ingress_integration.sh、tests/benchmark_data_lanes.sh、tests/session_pool_integration.sh。

## 验收标准

- [ ] 运行 `make clean && make` 输出 0 条 warning，且通过新增门禁脚本判定（exit 0）。
- [ ] 新增门禁脚本将 `-Werror` 纳入构建，构造一个故意警告的探针代码时门禁失败，移除探针后门禁通过。
- [ ] 新增专用性能基准脚本可运行，并输出包含吞吐/时延/线程数/RSS 的对比结果（v80 基线值）。
- [ ] v81 集成回归脚本通过：HELLO 认证后分片发送后续控制帧可正确重构并分派，会话有序性保持。
- [ ] v81 慢客户端场景：不发送完整操作的会话不消耗业务 worker（线程数不随 stalled 会话增长）。
- [ ] v81 数据面并发验证：多通道并发传输结果正确，吞吐不低于 v80 基线 97%。
- [ ] v81 跨版本互操作：新客户端↔旧 Agent 与旧客户端↔新 Agent 均通过既有互操作测试。
- [ ] v81 资源改善：相对 v80，控制面会话线程数峰值下降 ≥50%，RSS 不上升。
- [ ] 既有全部回归测试（TREE/catalog/data-lane/System RPC/会话池/EXEC）保持通过。

## 范围外

- 不做 TREE/FILE 事务状态机的非阻塞重写（不复制状态机）。
- 不做 EXEC 事件域重构（维持 v79/v80 既有 shard 移交）。
- 不做数据面（Data Lane）的每-session 线程改事件驱动重构（仅验证）。
- 不做持久状态 schema 迁移（沿用既有 no-migration 策略，schema 81 不迁移）。
- 文档滞后刷新不纳入本次（TEST_REPORT.md/README 版本标注）。

## 备注

- v81 完整实现为大型工程，拆为独立子任务，父任务 T0288 统一验收。
- 性能指标为「相对 v80 系数」表达，硬性目标为线程数 ≥50% 下降 + 吞吐不回归 ≥97%。
- 门禁修复与性能基线先行，为 v81 提供干净的开发与对比基础。
- 数据面保持+验证的决策已确认（用户指定），避免范围过度扩张。
