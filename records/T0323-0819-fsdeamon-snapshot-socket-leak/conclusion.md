---
schema: pdca.asset/v1
id: T0323-0819-fsdeamon-snapshot-socket-leak
phase: check
source_ids:
  - ac1-regression-snapshot
  - ac2-strace-close
  - ac3-fd-stable
  - ac4-build-data
  - ac5-data-correctness
  - ac6-release-paths
  - convergence-map
---

## 上下文

fsdeamon 每次执行 snapshot 泄漏 2 个到 source(8811) 的 TCP 连接。根因：
`FilesMeta::Init_FilesMeta()` 直接 `m_session = rpc_session_start(&m_args)` 覆盖旧
session 指针，未先 `rpc_session_stop`。`m_FilesMeta_ver`/`m_FilesMeta_bak` 为
FilesMetaMgr 值成员，仅进程退出才析构。每次 `SnapshotFilesMeta()` 对 ver/bak
各调一次 Init_FilesMeta，故每次快照泄漏 2 个连接。修复前实测：6 次增量快照后
8811 连接 8→20，fd 18→30。

## 假设与结果

采用方案 B（仅主动释放）：新增 `FilesMeta::CloseSession()`，在 SnapshotSync（释放
ver）、SnapshotEnd（释放 bak）、SnapshotFailed（统一 error__ 出口释放 ver+bak）
三处主动释放；DEFAULT session 常驻不受影响。

| AC | 假设 | 结果 |
|----|------|------|
| AC-1 | 3 次增量快照后连接数不增长 | 通过：fd 14/连接 4 稳定（基线） |
| AC-2 | strace 验证 socket 均被 close | 通过：socket(14)/(17) 均配对关闭 |
| AC-3 | 单次快照前后 fd 数一致 | 通过：14→14 |
| AC-4 | xmake build + 既有测试通过 | 通过：build ok；无既有单测套件 |
| AC-5 | 不影响快照数据正确性 | 通过：J1~J4 增量快照均成功 |
| AC-6 | 三路径正确释放，DEFAULT 常驻 | 通过：代码审查确认 + 运行验证 |

## 分析

- 回归验证在真实环境（qemu source 8811）执行 4 次增量快照（J1~J4），修复后
  fd 与连接数均稳定在基线（14 / 4），修复前为 30 / 20，泄漏已消除。
- strace 直接对比：修复前快照线程 socket(26)/(31) connect 后无 close 退出；
  修复后 socket(14)/(17) 在 [14:00:59.304925]/[14:00:59.304830] 被 close。
- 并发安全：三处释放点均在 m_pBackupMutex 下，与 ParserLogDispatch 的 session
  使用互斥；释放后 ver/bak 已从 m_MetasList 移除，无并发访问风险。
- SnapshotFailed 统一 error__ 出口覆盖 FlushMetaCache/OnRestoreSnapshot 提前
  失败路径，无泄漏遗漏。
- 失败路径（SnapshotFailed）未实际触发测试，经用户确认接受代码审查覆盖。
- 版本 3.6.3.13 → 3.6.3.14（xmake.lua rpc_version），提交 90e714ca。

## 适用边界

- 修复仅作用于 fsdeamon 快照结束路径的 session 生命周期，不修改协议与业务逻辑。
- 3 个 DEFAULT 常驻 session 在 qemu 端主动关闭后处于 CLOSE-WAIT，属既有现象
  （RPC_OPT_RETRY 触发 rpc_session_restart 重连），不随快照累积，不在本修复范围。
- 项目无既有单测套件，验证方式为集成回归（真实环境）+ 代码审查双轴。

## 下一轮建议

- 若需进一步消除 CLOSE-WAIT 常驻连接，可评估对 qemu 端 keepalive 或
  rpc_session_restart 时机做优化，属独立任务。
- 可考虑为 FilesMeta session 生命周期补充单元测试框架接入点。

## 验收标准逐条判定

- AC-1: PASS — ac1-regression-snapshot
- AC-2: PASS — ac2-strace-close
- AC-3: PASS — ac3-fd-stable
- AC-4: PASS — ac4-build-data
- AC-5: PASS — ac5-data-correctness
- AC-6: PASS — ac6-release-paths

## Verdict

outcome: confirmed
reason: 6 条验收标准全部通过，真实环境回归验证泄漏消除，代码审查与收敛验证通过。
verdict_id: T0323-v1
