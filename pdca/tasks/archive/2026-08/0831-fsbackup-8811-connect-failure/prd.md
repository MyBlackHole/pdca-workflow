# 修复 fsbackup 添加备份目录时 8811 端口连接失败诊断与端口冲突处理

## 背景

用户在宿主机+qemu VM 混合环境中运行 `fsdeamon --data-path /tmp/fsbackup/data --log-path /tmp/fsbackup/log`（监听 8901）+ `aio-speedd -p 8811 --daemon`（VM 内监听 8811，宿主机通过 `hostfwd=tcp::8811-:8811` 转发）。执行：

```bash
# AddSource 成功
16:29:12 AddSource wdg 127.0.0.1:8811 success
# AddTrackup 连续失败
16:29:20/16:29:38/16:32:58 fsbacup_dev_ioctl 127.0.0.1:8811 failure
16:29:20/16:29:38/16:32:58 FsKernel_AddTrackup connect to 127.0.0.1:8811 failure
→ fs-cli 响应 {"msg":"add trackup dir failure."}
```

宿主机 `ss -tlnp` 显示 `qemu` 占用 `0.0.0.0:8811`（hostfwd），`bash /dev/tcp/127.0.0.1/8811` TCP 可连通，VM 内 `netstat -an` 确认 `0.0.0.0:8811 LISTEN` 且 `aio-speedd -p 8811` 双进程存活。`strace` 显示 `fsdeamon` 的 `connect(14, 127.0.0.1:8811)=0` 成功后立即 `close(14)`，未进行 `do_fsbacup_dev_ioctl` 的 RPC 往返，日志却统一归为 `connect to failure`，原始 `ioctl_buff` 细节被丢弃。VM 内初始 `/dev/fsbackup` 不存在（`lsmod` 未加载），`insmod fsbackup.ko` 后 MAJOR 248 才出现，但宿主机链路仍失败，说明还有 TLS/握手或 ioctl 错误被掩盖。

## 根因分析

### R1 — 错误归类不精确（P0）`rpc/rpc-io.cpp:connect_server_session` / `rpc/rpc.cpp:fsbacup_dev_ioctl`

`connect_server_session` 内 TCP `connect` 成功后，若 `rpc_handshake_client` 失败（mTLS 协商、证书缺失、协议不匹配），统一 `goto error_session → close(fd) → return -1`。上层 `fsbacup_dev_ioctl` 将所有非零统一 `snprintf("connect to:[%s:%d] failure")` 并 `ErrorLog`，丢失 `handshake rejected`、`TLS handshake failed`、`cert_dir missing` 等细分。`FsKernel_AddTrackup` 再将该串原样 `ErrorLog`，未透出 `errno`/`handshake result`。

### R2 — 错误链路透出丢失（P0）`fs-backup/fsdeamon/fs_source.cpp:ChangeTrackup`

```cpp
ret = FsKernel_AddTrackup(..., &conn);
if (ret != 0) { msg = "add trackup dir failure."; goto exit__; }
```
`FsKernel_AddTrackup` 已将细节写入 `ioctl_buff`（`connect to...` / `handshake ...`），但 `ChangeTrackup` 丢弃该 buff，仅用固定文案写入 `json_response["msg"]`，客户端与日志均无法自诊断是端口被 qemu 占用、内核模块未加载还是 `/opt/aio/` 路径在 VM 内不存在。

### R3 — AddSource 无预检（P1）`fs-backup/fsdeamon/fs_service.cpp:AddSource`

`AddSource` 仅持久化 `source_host/port` 到 `FsSource` 与 `m_MapSource`，不做 `open_service`/`connect_server_session` 可达性探测，导致配置阶段成功，首次 `AddTrackup` 才暴露，排查成本高。同期 `UpdateSourceHost` 已有 `open_service` 探测，应对齐。

## 修复方案

### F1 — 细分 connect vs handshake 错误并透出细节

* `rpc/rpc-io.cpp:connect_server_session`：区分 `connect` 失败（`errno`）与 `rpc_handshake_client` 失败（已有的 `ErrorLog("handshake rejected...")`），在 `ErrorLog` 中分别打印 `connect to %s:%d failed: %s(errno %d)` 与 `handshake to %s:%d failed`，必要时将 `hs_err_str` 写入返回 `buf`。
* `rpc/rpc.cpp:fsbacup_dev_ioctl`：`connect_server_session` 失败时保留 `errno/handshake` 文案到 `buf`，而非仅 `connect to failure`；`do_fsbacup_dev_ioctl` 失败时同样将 `resp_host->err_no`/`strerror` 透出。
* `fs-backup/fsdeamon/fs_kernel_sync.cpp:FsKernel_AddTrackup`：`ErrorLog("%s (host %s:%d, errno %d)", ioctl_buff, conn->host, conn->port, errno)`，使宿主机日志可直接区分 qemu 转发通但 handshake 失败 vs 内核 ioctl 失败。

### F2 — 修复 ChangeTrackup/AddSource 错误透出

* `FsSource::ChangeTrackup`：失败分支 `msg = std::string(ioctl_buff)`（若 `ioctl_buff` 非空）而非固定文案，并将 `source_host:source_port` 回显到 `json_response["source_host"]`/`["source_port"]`，供客户端直接定位。
* `FsService::AddSource`：在 `InitEnv` 后、`Start` 前增加轻量可达性探测（`open_service` 或 `FsKernel_AddTrackup` dry-run 的 `host:port` 连通性），探测失败时 `json_response["msg"]` 携带细节并 `WarningLog`，避免静默入库后批量失败。探测失败不阻塞入库（保持现有语义），但日志与响应需可诊断。

### F3 — 增强验收与文档

* 新增可回归探针：`scripts/check-fsbackup-8811.sh` 或 `rpc/tests` 扩展，模拟 `connect` 成功但 `handshake` 失败、`port 被占用`、`fsbackup.ko 未加载` 三类故障，断言日志与响应包含可操作关键词（`handshake`/`connect`/`fsbackup`）。
* 文档：在 `fs-backup/doc/readme.md` 常见问题新增条目：`qemu hostfwd 占用 8811`、`VM 内需 insmod fsbackup.ko`、`AddSource 后建议用 check 方法验证`。

## 验收标准

- [ ] AC-1：`FsKernel_AddTrackup` 连接失败时宿主机 `/tmp/fsbackup/log/network.log` 可区分 TCP 连接失败（`errno`）与握手失败（`handshake rejected`/`TLS`），不再仅有 `connect to:[127.0.0.1:8811] failure`（以 `strace connect=0` 但 handshake 失败、以及 `iptables -j REJECT` 两种注入验证）。
- [ ] AC-2：`AddTrackup` 失败时客户端 `json_response["msg"]` 透出 `ioctl_buff` 具体原因（含 `host:port`），而非固定 `add trackup dir failure.`（以 `fs-cli --method=add-trackup --bak-path=/opt/aio/` 在端口占用与内核未加载两类故障下验证）。
- [ ] AC-3：`AddSource` 阶段新增可达性预检日志/响应，`host:port` 不可达时 `AddSource` 响应或 `network.log` 含可操作提示（`open_service`/`connect`/`handshake` 细节），回归不阻塞既有入库语义。
- [ ] AC-4：回归验证——VM 内 `insmod fsbackup.ko` 后，`fs-cli --method=add-trackup --bak-path=/opt/aio/` 在宿主机与 VM 双路径下均有明确结果（宿主机路径不存在时报 `path not exist/ioctl` 而非 `connect failure`；VM 内路径存在时成功），且 `xmake test` 相关用例通过。

## 非目标

- 不改变现有 `hostfwd` 端口规划与 `aio-speedd -p 8811` 部署拓扑（仅增强诊断，不改网络转发规则）。
- 不引入 `fsdeamon` 对内核模块的自动 `insmod`（保持手动 `insmod fsbackup.ko` 语义，仅在日志中提示 `/dev/fsbackup` 缺失）。
- 不修改 `fsbackup.ko` 内部 ioctl 语义，仅透出既有 `err_no`/`strerror`。

## 关联本体节点

```
ontology:concept/pdca-task
ontology:domain/backup
ontology:domain/backup-fs
```

## 风险

- 错误文案从固定串改为 `ioctl_buff` 透出，需确保 `buf` 以 `\0` 结尾且不越界（`snprintf` 已保证 4096 边界）。
- `AddSource` 预检仅为 warned 诊断，不改变入库成功语义，避免对离线数据源的误拒绝；`open_service` 超时需设为短超时（3s）防止阻塞。
- `connect_server_session` 的细分日志需避免泄露敏感证书路径以外的信息，仅记录 `host:port` 与 `hs_err_str`。

