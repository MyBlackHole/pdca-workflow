# Triage Brief — 0819-fsdeamon-snapshot-socket-leak

- **category**: bug
- **scenario_type**: bugfix
- **summary**: 每次执行 `fs-cli --method=snapshot` 后，wdg 子 fsdeamon 到 source(127.0.0.1:8811) 的 TCP 连接泄漏 2 个 fd，连接在 CLOSE-WAIT 状态永久积压，长期运行将耗尽 fd。
- **current behavior**: 快照前 fd=18/连接=8；I4 后 fd=20/连接=10；I5 后 fd=22/连接=12；I6 后 fd=24/连接=14；I9 后 fd=30/连接=20。每次 snapshot 稳定 +2。泄漏连接处于 CLOSE-WAIT（对端 qemu 已 FIN，本地未 close）。
- **root cause**: `FilesMeta::Init_FilesMeta()`（files_meta.cpp:56）直接 `m_session = rpc_session_start(&m_args)` 覆盖旧 session 指针，未先 `rpc_session_stop` 释放旧连接。每次快照 `SnapshotFilesMeta()`（files_meta_mgr.cpp:236）对 `m_FilesMeta_ver` 和 `m_FilesMeta_bak` 各调用一次 Init_FilesMeta，因此每次快照泄漏恰好 2 个连接。这两个 FilesMeta 为 FilesMetaMgr 长生命周期成员，只有进程退出才析构释放。
- **fix**: 方案 B（仅主动释放）——给 FilesMeta 新增 `CloseSession()`，在快照结束点 SnapshotSync（ver）、SnapshotEnd（bak）、SnapshotFailed（ver+bak）主动释放；DEFAULT session 常驻不释放。
- **evidence**: strace（-f 跟踪 pid 1553045）确认线程创建 socket(26)/socket(31) connect 8811 后线程退出但无对应 close；fd 数与 8811 连接数逐次增长；CLOSE-WAIT 状态确认对端已关闭。
- **desired behavior**: 每次快照结束后不残留到 8811 的连接；长期多次快照 fd 数保持稳定。
- **key interfaces**: `fs-backup/fsdeamon/files_meta.cpp`（Init_FilesMeta/CloseMetas/~FilesMeta）、`fs-backup/fsdeamon/files_meta_mgr.cpp`（SnapshotFilesMeta/SnapshotEnd）、`rpc/rpc.cpp`（rpc_session_start/stop）。
- **acceptance criteria**: 连续 3 次增量快照连接数不增长；strace 无未关闭 socket；fd 数前后一致；build/测试通过；修复仅限 session 生命周期管理。
- **out of scope**: 协议字段、FsKernelSync 常驻 session 复用、快照数据格式和业务逻辑。
- **information gaps**: 无；根因、触发路径、复现与修复方向均已确认。
- **dedup results**: T0227（0807-rpc-socket-reuse-idle-reclaim）为 rpc 空闲回收 research 任务，非同一 bug，无直接重复。
- **recommended next steps**: 在 Init_FilesMeta 的 rpc_session_start 前若 m_session!=NULL 先 rpc_session_stop；写回归验证脚本统计 fd/连接数；跑增量与全量快照验证。