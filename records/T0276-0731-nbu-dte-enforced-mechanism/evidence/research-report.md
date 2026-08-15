# 调研报告：NBU 强制加密（Enforced）服务端实现机制与重启需求

> 任务: T0163 | 类型: research | 日期: 2026-07-31
> 环境: nbusvr103 (10.6.67.187) + nbumed103 (10.6.67.251), NBU 10.3.0.1
> 方法: 纯静态分析（nbjm/nbemm/bprd/nbseccmd/libVemmMT.so 二进制符号与字符串）+ 官方文档（SecEncryp Guide）+ T0162 抓包实证结论。未修改任何生产配置。

## 调研目标

1. 绘制 Enforced 配置的存储/下发/执行链路（配置变更 → 生效的执行点）
2. 明确 refreshDteCache 缓存机制（内容、刷新时机、延迟窗口）
3. 明确强制守卫的执行点（作业调度期 or 连接建立期）
4. 结论：修改为 Enforced 后是否需要重启（与 Preferred On 差异）
5. 澄清 Enforced 与 insecurecommunication off 的关系

## 方法

1. **符号级静态分析**: 对 nbusvr103 上的 nbjm、nbemm、bprd、nbseccmd、libVemmMT.so 执行 `strings`/`nm -D`，提取 DTE 相关函数符号、CORBA skeleton、日志串、错误串
2. **配置存储定位**: 检查 `/usr/openv/netbackup/db/mds.db`（SQLite，实测为媒体设备缓存无 DTE）、`/usr/openv/var/global/` 等候选位置
3. **文档对照**: NetBackup 10.5 SecEncryp Guide（本地 pdftotext 版）+ nbseccmd man 页
4. **实证交叉验证**: 复用 T0162 抓包结论（uptime 84 天 + DTEMode=On 作业正常）

## 发现

### F1: 配置入口与存储（nbseccmd）

- 修改命令: `nbseccmd -setsecurityconfig -dteglobalmode 0|1|2`（0=Preferred Off, 1=Preferred On, 2=Enforced），另有 `-dtemediamode off|on -mediaserver <ms>` 按媒体服务器覆盖
- 查看命令: `nbseccmd -getsecurityconfig -dteglobalmode`（需 bpnbat WEB 登录授权，实测返回 5930 未授权）
- 隐藏排障命令: `nbseccmd -cleardtecache`（存在 `nbseccmd::clear_dte_cache` 方法）
- 关键符号: nbseccmd 引用 **`bpcr_refresh_dte_global_config_rqst`**（U = 外部调用）→ **配置修改后主动发起"刷新 DTE 全局配置"请求**，非重启触发

### F2: 刷新请求的接收端（bprd）

bprd 同时含 **实现** `bpcr_refresh_dte_global_config_rqst` 与执行逻辑：

- 操作名: `Refresh DTE Cache`
- 权限校验: `Not a valid server to request DTE cache refresh`（非有效服务器拒绝）
- 集群处理: `refresh_dte_for_cluster failed with error : %d`（集群场景广播刷新）
- 失败路径: `bpcr_refresh_dte_global_config_rqst failed with error %d`

→ bprd 是刷新请求的接收/分发端（CORBA/bpcr 通道），链路为: nbseccmd → bprd →（集群）→ nbjm/nbemm。

### F3: 缓存刷新执行点（nbjm + nbemm）

**nbjm（作业管理）** — 刷新进程内 DTE 缓存:

- CORBA 方法: `JobManager_i::refreshDteCache`（完整 TAO skeleton 链: `POA_Veritas::NetBackup::JM::refreshDteCache_JobManager` / `_skel` / `execute`）→ **nbjm 暴露运行期热刷新接口**
- 缓存变量: `NBJMSvc::m_globalDteInfo`（nbjm 全局成员）→ 全局 DTE 模式缓存在 nbjm 进程内

**nbemm（MDS 服务器）** — 刷新 EMM 层缓存:

- 方法: `MdsServer::refreshGlobalDteCache`
- 成功日志: `Successfully refreshed the MDS cache for Global DTE Mode to value [ %d ]`
- 缓存实现位于 **libVemmMT.so**: `GetQueryMediaDTESettingCache` / `PutQueryMediaDTESettingCache`
- 缓存结构: `CacheTemplate<string, string, DefaultTime>`（**带默认 TTL 的缓存模板** → 缓存有过期兜底，即使无主动刷新也会按 TTL 自然失效重查）

### F4: 强制守卫执行点（nbjm 子作业调度期 — ***DTE*** 日志流）

nbjm 在**子作业调度决策时**检查（非连接建立期）:

```
***DTE*** Determining global DTE mode for Child Job with job_id = [
***DTE*** Determining DTE mode for Child job with job_id = [
***DTE*** Error - Failed to get DTE global mode, retval =
***DTE*** Error - DTE mode is enforced, but media server is not DTE capable, media server version =
    → "The global data-in-transit encryption is enforced in the NetBackup domain,
       but it cannot be enabled as the media server version is earlier than 9.1."
***DTE*** Error - DTE global mode is enforced, but MEDIA_DTE_MODE is set OFF on media server
    → "The global data-in-transit encryption (DTE) is enforced in the NetBackup domain,
       but the DTE setting is disabled on the media server."
***DTE*** Media server version is unknown, setting m_dteMode :
```

**两种 Enforced 失败场景**（作业在调度期被拒，根本走不到连接建立）:
1. 媒体服务器版本 < 9.1（不支持 DTE）
2. 媒体服务器 MEDIA_DTE_MODE=OFF（被显式禁用）

相关符号: nbjm `getGlobalDteMode`、`map_global_dte_mode_to_dte_mode`、`emmlib_QueryMediaDTESetting`（U，来自 libVemmMT.so 的 EMM 查询）; nbemm `getGlobalDteMode`、`get_dte_ignore_image_mode`、`convert_media_server_dte_mode`、`DTE_MEDIA_MODE`、`verify_media_srvr_dte`。

### F5: 客户端侧行为（文档）

- `DTE_CLIENT_MODE = AUTOMATIC | ON | OFF`，9.1 默认 OFF，10.0+ 默认 AUTOMATIC
- AUTOMATIC → 遵循全局模式（Enforced/Preferred On/Preferred Off）
- **Enforced + 客户端 OFF（或 < 9.1）→ 作业失败**（文档明确）; Preferred On 时 OFF 可排除个别客户端（不失败）

## 结论与建议

### 结论

**AC-1 ✅ 配置链路（存储 → 下发 → 执行）**

```
nbseccmd -setsecurityconfig -dteglobalmode 2
   │  ① 写入安全配置（EMM/安全配置库）
   │  ② 发起 bpcr_refresh_dte_global_config_rqst
   ▼
bprd: "Refresh DTE Cache"（权限校验 → 集群广播 refresh_dte_for_cluster）
   │  ③ 经 CORBA/bpcr 通道下发
   ├──▶ nbjm:  refreshDteCache (CORBA) → 更新进程内 m_globalDteInfo
   └──▶ nbemm: MdsServer::refreshGlobalDteCache → 更新 EMM 缓存
              (libVemmMT.so Get/PutQueryMediaDTESettingCache, CacheTemplate+DefaultTime TTL)
   │
   ▼
执行点: nbjm 子作业调度期（***DTE*** 判定）→ 失败拒绝 或 携带 dte_mode=6 下发 bpbrm/bptm
   → 连接建立期: VNET 协商（T0162 实证: badfeed JSON dte_mode=6 → TLS 1.2 升级）
```

**AC-2 ✅ 缓存机制**: 进程内缓存（nbjm `m_globalDteInfo`）+ EMM 缓存（libVemmMT.so `Get/PutQueryMediaDTESettingCache`），CacheTemplate 带 DefaultTime TTL（自然过期兜底）; 刷新时机 = 配置变更即时主动刷新（nbseccmd → bprd → nbjm/nbemm 热刷新接口），延迟窗口 ≈ 主动刷新耗时 + 缓存 TTL 兜底（无实际业务影响）。

**AC-3 ✅ 强制守卫执行点**: **作业调度期**（nbjm 子作业判定，错误串见 F4），明文连接在调度期即被拒（作业失败，不进入连接建立）; 连接建立期仅做协商（VNET/TLS 升级），不做强制判定。

**AC-4 ✅ 修改 Enforced 无需重启**:
- 配置变更经 bprd → nbjm/nbemm 运行期热刷新（CORBA refreshDteCache），进程无需重启
- EMM 缓存有 TTL 兜底，即使刷新失败也会自然失效重查
- 实证: nbusvr103 uptime 84 天（T0162）期间 DTEMode=On 作业全程正常，证明运行期配置生效路径存在
- **差异**: Enforced 下媒体服务器 <9.1 或 MEDIA_DTE_MODE=OFF 的作业**直接失败**（调度期）; Preferred On 下仅尽力加密，失败只是降级或排除
- 唯一需要"重启"的场景: 立即断开**存量已建立**的不安全连接（与 insecurecommunication off 同理，属连接生命周期问题，非配置生效问题）

**AC-5 ✅ Enforced vs insecurecommunication off**: 两者独立维度。insecurecommunication off 管控 legacy 明文通信端口/VNET 层的允许列表; DTE Enforced 管控数据路径加密强度（应用层）。NBU 10.3 实测全走 1556 (PBX)（T0162），legacy 端口已不参与; Enforced 不隐含 insecurecommunication off，需分别配置。

### 对自研实现的建议

1. **配置生效设计**: 采用"写配置 + 主动刷新通知"模式（模拟 bpcr_refresh_dte_global_config_rqst），进程内缓存 + 内存刷新接口，**无需重启**
2. **缓存兜底**: 缓存必须带 TTL（NBU 用 CacheTemplate+DefaultTime），防刷新通知丢失导致配置永久不生效
3. **强制判定位置**: 调度期（作业派发前）做强制校验，失败信息带明确原因（版本不支持 / 显式禁用），优于连接期才拒绝
4. **权限控制**: 刷新接口需校验请求方（bprd: "Not a valid server to request DTE cache refresh"），防止任意节点触发刷新

## 参考资料

- T0148 调研记录（DTE 决策状态机、vnet 层符号）
- T0162 抓包实证（单端口协商机制、dte_mode=6、uptime 84 天、动态生效）
- NetBackup 10.5 SecEncryp Guide（DTE_CLIENT_MODE、nbseccmd 语法、Enforced 失败语义）
- nbseccmd man 页（/usr/openv/netbackup/bin/goodies/man/nbseccmd.1）
- 静态分析目标: /usr/openv/netbackup/bin/{nbjm,nbemm,bprd,nbseccmd}, /usr/openv/lib/libVemmMT.so
