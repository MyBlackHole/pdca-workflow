---
schema: pdca.asset/v1
id: T0163-0731-nbu-dte-enforced-mechanism
phase: check
source_ids: [evt-001, evt-002]
---

## 上下文

T0148 已确认 Enforced 决策层行为（错误码 8301/8308/8310/8311/8314），T0162 已实证单端口协商机制。本任务针对服务端实现机制：配置存储/下发链路、refreshDteCache 缓存、强制守卫执行点、重启需求、与 insecurecommunication off 的关系。

方法约束：纯静态分析（nbjm/nbemm/bprd/nbseccmd/libVemmMT.so 二进制符号与字符串）+ 官方文档 + 复用 T0162 实证，不修改生产配置。

## 假设与结果

| # | 假设 | 结果 |
|---|------|------|
| H1 | 修改 Enforced 需要重启服务端（类似 insecurecommunication off） | ❌ 推翻：改配置即推送刷新（bpcr_refresh_dte_global_config_rqst → bprd → nbjm/nbemm 热刷新），无需重启 |
| H2 | 强制守卫在连接建立期拒绝明文 | ❌ 修正：守卫在 nbjm 子作业**调度期**执行（***DTE*** 日志流），明文连接根本走不到建立阶段 |
| H3 | 存在 DTE 配置缓存窗口（生效延迟） | ⚠️ 部分：nbjm 进程内缓存 m_globalDteInfo + EMM 缓存（libVemmMT.so CacheTemplate+DefaultTime TTL），有主动刷新 + TTL 兜底，实际延迟≈0 |
| H4 | Enforced 隐含禁用不安全通信 | ❌ 推翻：两个独立维度（DTE=数据路径加密强度，insecurecommunication=legacy 明文端口管控），需分别配置 |

## 分析

### 证据链（符号级，全部来自 nbusvr103 二进制）

1. **配置入口**：nbseccmd `-setsecurityconfig -dteglobalmode 0|1|2` / `-dtemediamode off|on` / 隐藏 `-cleardtecache`；引用 `bpcr_refresh_dte_global_config_rqst`（U 符号 = 发起刷新请求）
2. **接收/分发**：bprd 实现该 rqst，操作名 "Refresh DTE Cache"，权限校验 "Not a valid server to request DTE cache refresh"，集群广播 `refresh_dte_for_cluster`
3. **热刷新执行**：
   - nbjm：CORBA 方法 `JobManager_i::refreshDteCache`（完整 TAO skeleton 链），缓存变量 `NBJMSvc::m_globalDteInfo`
   - nbemm：`MdsServer::refreshGlobalDteCache`，成功日志 "Successfully refreshed the MDS cache for Global DTE Mode to value [ %d ]"
   - libVemmMT.so：`GetQueryMediaDTESettingCache`/`PutQueryMediaDTESettingCache`，`CacheTemplate<string,string,DefaultTime>`（带 TTL）
4. **守卫执行点**：nbjm 调度期 `***DTE***` 错误串（media server < 9.1 / MEDIA_DTE_MODE OFF）→ 作业失败，两种场景均不进入连接建立
5. **文档对照**：DTE_CLIENT_MODE=AUTOMATIC 遵循全局；Enforced + 客户端 OFF/<9.1 → 作业失败（SecEncryp Guide）；nbseccmd man 页确认语法
6. **实证交叉**：nbusvr103 uptime 84 天（T0162）期间 DTEMode=On 作业全程正常 → 运行期配置生效路径存在

### 排他性检查（Grill）

- **替代解释 1**：是否可能 refresh 仅清缓存、仍需重启？→ 排除：nbjm 暴露 CORBA 热刷新接口（非重启时机），且 T0162 实证 84 天无重启且 DTE 配置已生效
- **替代解释 2**：mds.db 是否承载 DTE 配置？→ 排除：实测为媒体设备缓存（EMM_Media_* 表），无 DTE 表；DTE 存于 EMM 安全配置库（nbseccmd 读写路径）
- **证据局限**：未能实测"切换 Enforced 瞬时生效"（生产零变更约束）；nbjm 日志目录为空（日志未启用），未能获得调度期时间线日志佐证
- **静态分析局限**：CacheTemplate DefaultTime 具体秒数未提取（C++ 模板实例化，无字面量串）；延迟窗口结论依赖机制推理 + T0162 实证

## 失败原因（仅 rejected/partial）

无。结论以 confirmed 判定。

## 适用边界

- 适用于 NBU 9.1+（9.1 引入 DTE）；验证环境 10.3.0.1
- "无需重启"指配置生效路径；若需强制断开**存量已建立**的不安全连接，仍需重启（连接生命周期问题，非配置生效问题）
- Enforced 下媒体服务器 <9.1 或 MEDIA_DTE_MODE=OFF 的作业**调度期直接失败**——生产切换 Enforced 前必须逐台核验媒体服务器版本与 DTE 模式（nbusvr103/nbumed103 均 10.3 ✅）
- 静态分析结论基于二进制字符串/符号推断，未做运行期动态验证

## 下一轮建议

1. **可选跟进**：启用 nbjm 详细日志（vxlogcfg -o Nbjm -s 6），在非生产环境实测 Enforced 切换 → 首次作业调度时间线（验证 TTL 窗口实测值）
2. **生产切换 Checklist**（若未来执行）：逐台核验 media server 版本 ≥9.1 且 MEDIA_DTE_MODE≠OFF → 先 Preferred On 观察 → 再 Enforced
3. 本结论与 T0148 错误码、T0162 协商机制合并为完整 DTE 知识链（knowledge/nbu/nbu-dte-architecture.md 已回写）

## 安全机制分析（恶意关闭/降级 DTE 的攻击面）

### 纵深防御链路（四层防护 + 语义兜底 + 审计）

```
┌─────────────────────────────────────────────────────────────────────┐
│                        攻击者（目标：关闭/降级 DTE）                    │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │
    攻击路径 A：直接修改配置         攻击路径 B：伪造刷新请求
    (降级 dteglobalmode)           (骗 bprd 重载缓存)
               │                              │
               ▼                              ▼
┌──────────────────────────┐   ┌──────────────────────────────────────┐
│ ① 认证层（入口闸门）       │   │ ③ 通道认证层（每请求必检）              │
│ nbseccmd -setsecurityconfig│   │ bpcr_authenticate_connection        │
│    │                       │   │ vnet_vxss_authenticate             │
│    ▼                       │   │        │                           │
│ 必须 bpnbat WEB 登录        │   │        ▼  NBU 证书/主机身份          │
│ (实测无登录→5930 拒绝)      │   │ 伪造请求在通道层即被拒 ✗             │
│    │                       │   │        │                           │
│    ▼ 凭据无效 → 拒绝 ✗      │   │        ▼ 通过认证                  │
└──────────────────────────┘   └────────────┬─────────────────────────┘
                                            │
                                            ▼
                          ┌─────────────────────────────────────┐
                          │ ④ 服务器身份校验（bprd 接收端）        │
                          │ "Not a valid server to request      │
                          │   DTE cache refresh"                 │
                          │   ┌───────────┐  ┌──────────────┐    │
                          │   │ 有效服务器? │─→│ 集群广播?      │    │
                          │   │ (主机列表)  │  │ refresh_dte_ │    │
                          │   └─────┬─────┘  │ for_cluster   │    │
                          │         │        └──────┬───────┘    │
                          │    非列表内 ✗           │            │
                          │    拒绝                  ▼            │
                          └─────────────────────────────────────┘
                                            │
                                            ▼
                    ┌─────────────────────────────────────────┐
                    │ ⑤ 语义兜底：刷新≠降级（关键设计）          │
                    │ 刷新请求只能"重载已落盘配置"              │
                    │ ┌─────────┐    ┌──────────────┐        │
                    │ │ 配置存储  │←──│ 只有①认证通过的 │        │
                    │ │(EMM/nbdb)│   │ 写操作能修改   │        │
                    │ └─────────┘   └──────────────┘        │
                    │       │                                │
                    │       ▼ 恶意刷新最多                  │
                    │  缓存抖动（TTL 兜底恢复）               │
                    └─────────────────────────────────────────┘
                                            │
                                            ▼
                          ┌─────────────────────────────────────┐
                          │ ⑥ 审计留痕（无法隐身）                │
                          │ bpcr_update_host_config_audit_rqst  │
                          │ net_update_host_config_audit_rqst   │
                          │ Audit::tr_dte_global_mode           │
                          │ 谁/何时/何操作 → 全程可追溯          │
                          └─────────────────────────────────────┘
```

### "直接改配置文件"为何不可行（结构性防御）

**NBU 不存在可编辑的 DTE 配置文件**，配置存储于 nbdb (PostgreSQL)：

| 候选位置 | 实测结论 | 证据 |
|---------|---------|------|
| bp.conf | 不含 DTE | 文本配置无 DTE 项 |
| /usr/openv/var/global/ | 无 DTE 配置文件 | 仅有 createsrt/nbcl/nbservice.conf |
| mds.db (SQLite) | 仅 EMM 媒体设备缓存 | 表结构无 DTE（EMM_Media_*） |
| **nbdb (PostgreSQL)** | **DTE 真正存储** | emmlib 读写路径 |

直接改 nbdb 的障碍链：
1. **密码加密存储**：vxdbms.conf `VXDBMS_NB_PASSWORD = AES-256-CTR:<密文>/TAG`，解密密钥在 NBU 内部密钥库（nbatd_passphrase + 主机证书），无明文
2. **psql 直连需认证**：实测 `fe_sendauth: no password supplied` 被拒
3. **缓存隔离**：即使物理改库，nbjm m_globalDteInfo + EMM CacheTemplate(TTL) 不触发刷新不生效
4. **审计**：nbemm `Audit::tr_dte_global_mode` 记录 DTE 模式变更

→ 合法唯一入口 = `nbseccmd -setsecurityconfig`（bpnbat 认证），职责分离设计（改配置=特权写操作需认证；刷新缓存=只读重载受身份+白名单限制）。

### 服务程序读取路径：双层架构（非全部直连数据库）

**只有 nbemm 直连 nbdb**，应用进程经 emmlib API + CORBA IPC + 双层缓存读取：

```
┌────────────────────────────────────────────────────────────────┐
│ 第一层：应用进程（nbjm 等）                                      │
│   调用 emmlib_QueryMediaDTESetting（emmlib API）               │
│   │                                                             │
│   ▼                                                             │
│ libVemmMT.so（EMM 客户端库，实测 ldd 无 nbdb 依赖）             │
│   带缓存: GetQueryMediaDTESettingCache/Put...（TTL 兜底）       │
│   │                                                             │
│   ▼  CORBA IPC（TAO，非 SQL）                                    │
├────────────────────────────────────────────────────────────────┤
│ 第二层：EMM 服务（nbemm）——唯一直连 nbdb 的组件                 │
│   实测 ldd: libnbdbMT.so + libVdbMT.so ✅                       │
│   MdsServer::refreshGlobalDteCache → 更新 EMM 缓存              │
│   │                                                             │
│   ▼  SQL 查询                                                   │
│ nbdb (PostgreSQL, 端口 13785)                                   │
└────────────────────────────────────────────────────────────────┘
```

**实测证据**（nbusvr103）：

| 组件 | 直连 nbdb? | 证据 |
|------|-----------|------|
| nbjm | ❌ | `ldd` 依赖 libVemmMT（无 nbdb），符号 `emmlib_QueryMediaDTESetting`（U=外部） |
| libVemmMT.so | ❌ | `ldd` 无 nbdb/pq 依赖；符号为 CORBA/TAO 类型（`Veritas::EMM::*_Record`） |
| **nbemm** | ✅ | `ldd`: `libnbdbMT.so` + `libVdbMT.so`；符号 `VxDBMS_Conf::GetEMMConnectString` |

**对"直改数据库"的影响**：改库后需穿透**两层缓存**（nbemm EMM 缓存 → nbjm 侧 GetQueryMediaDTESettingCache）才可能生效，叠加此前已述的密码加密/psql 认证/审计，共五层设卡：
1. nbdb 密码 AES-256-CTR 加密（vxdbms.conf，密钥在内部密钥库）
2. psql 认证（实测 fe_sendauth 拒绝）
3. nbemm EMM 缓存（TTL/刷新才重查）
4. nbjm 侧 EMM 客户端缓存（再次缓存）
5. Audit::tr_dte_global_mode 审计留痕

### 设计启示（对自研实现）

1. **配置不在文件里**：敏感配置入受管数据库/密钥库，物理改文件路径被结构性堵死
2. **配置密码加密存储**：AES-256-CTR + TAG，密钥入硬件/内部密钥库，防止静态提取
3. **写操作单一入口 + 认证**：所有配置变更必须走带认证的管理通道
4. **缓存隔离**：配置变更不直接改运行态，走刷新通知链路，防旁路
5. **审计独立**：配置变更审计（tr_dte_global_mode）与业务日志分离，攻击者无法清除
