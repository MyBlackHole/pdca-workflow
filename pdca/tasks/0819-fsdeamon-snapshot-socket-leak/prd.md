# 修复 fsdeamon snapshot 引发的 socket 泄漏

## 验收标准

- [ ] AC-1: 连续执行 3 次增量 snapshot（inc），fsdeamon 子进程到 source(8811) 的 TCP 连接数不再增长（稳定在基线水平，无 CLOSE-WAIT 累积）。
- [ ] AC-2: 运行 strace 验证 snapshot 期间新建的到 8811 的 socket 均被 close（每次 snapshot 无未关闭 socket）。
- [ ] AC-3: 单次 snapshot 后 `ls /proc/<fsdeamon_pid>/fd | wc -l` 前后保持一致（除临时文件 fd 外）。
- [ ] AC-4: 运行 `xmake build` 和既有测试，全部通过；不修改协议字段和业务逻辑。
- [ ] AC-5: 修复仅作用于 FilesMeta 的 session 生命周期管理（主动释放），不影响快照数据正确性（增量/全量均正常）。
- [ ] AC-6: 快照成功与失败路径（SnapshotSync/SnapshotEnd/SnapshotFailed）均正确释放 ver/bak 的 session，DEFAULT session 保持常驻不受影响。

## 方案（方案 B：仅主动释放）

给 FilesMeta 新增 `CloseSession()`，在快照流程的三个结束点主动释放 ver/bak 的 rpc session：

1. `SnapshotSync`（ver 用完后）：`m_FilesMeta_ver.CloseSession()`
2. `SnapshotEnd`（bak 用完后）：`m_FilesMeta_bak.CloseSession()`
3. `SnapshotFailed`（失败路径）：ver 与 bak 同时 `CloseSession()`

DEFAULT（m_FilesMeta）session 仅启动时创建、运行期常驻，不做主动释放，随对象析构释放。并发安全：三处释放点均在 m_pBackupMutex 保护下，与 ParserLogDispatch 的 session 使用互斥；释放后 ver/bak 已从 m_MetasList 移除，不会被遍历。

## 范围

- 纳入：FilesMeta 新增 CloseSession 方法、三处快照结束点主动释放、验证脚本（fd/连接数统计）、回归验证。
- 排除：修改协议字段、FsKernelSync 常驻 session 的复用逻辑、快照数据格式和业务功能。

## Seam 分析

### 声明的测试接缝

- seam: `fs-backup/fsdeamon/files_meta.cpp` -> FilesMeta::CloseSession 与 rpc_session_stop
- seam: `fs-backup/fsdeamon/files_meta_mgr.cpp` -> SnapshotSync/SnapshotEnd/SnapshotFailed 主动释放触发路径
- seam: `fs-backup/fsdeamon/fsdeamon.cpp` -> AsyncRequest/OnCliService/Snapshot 调用链（验证入口）