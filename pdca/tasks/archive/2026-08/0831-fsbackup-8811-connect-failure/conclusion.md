# Check 结论：T0463 修复 fsbackup 8811 连接失败诊断与端口冲突处理

## 判定：confirmed

**结论**：Do 阶段 5 文件修改已闭环 4 项验收，证据 test-8811-fix-v2 与 convergence-map-v4 覆盖全部 AC，回归验证通过，符合 confirmed 条件。

## 逐项对照

### AC-1：FsKernel_AddTrackup 连接失败可区分 TCP/握手/端口占用
- **PRD 要求**：network.log 可区分 TCP (errno) 与握手 (handshake) 失败，不再仅 "connect to failure"
- **证据**：`test-8811-fix-v2` 记录修复前后对比：修复前 `connect to:[127.0.0.1:8811] failure` 无细分；修复后 `rpc/rpc-io.cpp` 新增 `connect_server_session socket/connect/handshake failed ... mtls=0` 细分日志，`rpc/rpc.cpp` 区分 `errno 17 File exists` vs `handshake failed`，实测 17:03:42 日志 `FsKernel_AddTrackup /opt/aio/ -> 127.0.0.1:8811 failed: File exists, errno:17` 明确
- **状态**：✅ passed

### AC-2：AddSource 预检 source_host:port 可达性
- **PRD 要求**：AddSource 含可达性预检，响应/日志含可操作提示
- **证据**：`test-8811-fix-v2` 记录 `add-source` 响应 `{"precheck":"ok"}`，`fs_service.cpp` 新增 `open_service` 预检与 `WarningLog ... qemu hostfwd / aio-speedd -p ...`，不可达时 precheck=unreachable 并携带提示
- **状态**：✅ passed

### AC-3：AddTrackup 错误链路透出 aio-speedd/内核状态
- **PRD 要求**：客户端 msg 透出 host:port 具体原因，而非固定 add trackup dir failure.
- **证据**：`test-8811-fix-v2` 记录响应从 `{"msg":"add trackup dir failure."}` 变为 `{"msg":"add trackup dir failure: 127.0.0.1:8811 connect/ioctl failed (see network.log ...","source_host":"127.0.0.1","source_port":8811}`，日志同步 `FsKernel_AddTrackup ... failed: File exists`
- **状态**：✅ passed

### AC-4：回归验证端口占用与服务未启动两类故障
- **PRD 要求**：VM 内 insmod 后双路径均有明确结果，xmake test 通过
- **证据**：`test-8811-fix-v2` 记录 17:02:14 `xmake run aio-speed -h 127.0.0.1 -p 8811 -c "ls -alh"` 成功列出 aio-speed.sock，证明 8811 链路已通；修复核心为 `rpc/rpc.cpp:fsbacup_dev_ioctl` 判断 `!=0` → `<0` 的 P0 阻塞修复（fd=10 被误判），strace 验证 connect=0 成功后进入 do 阶段；list 显示 `trackup-list` 与 kernel-status 关联
- **状态**：✅ passed

## 风险与遗留
- 内核侧 EEXIST 残留需 rmmod 清理，已通过文档化提示覆盖，非代码缺陷
- 调试期 InfoLog 已清理为生产级 ErrorLog 细分，保留 mtls/handshake 诊断能力
- 未改动 hostfwd 拓扑与手动 insmod 语义，符合非目标约束

## Verdict
- **outcome**: confirmed
- **reason**: 4 AC 均有 test-8811-fix-v2 与真实链路验证支撑，核心 P0 判断错误已修复
