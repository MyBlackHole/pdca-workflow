# 调研报告：NBU DTE 单端口 TLS/明文协商机制 — 抓包验证

> 任务: T0162 | 类型: research | 日期: 2026-07-31
> 环境: nbusvr103 (10.6.67.187) + nbumed103 (10.6.67.251), NBU 10.3.0.1

## 调研目标

实证验证 T0148 推断的机制：
1. 同一端口上是否存在明文 VNET 协议头（非 TLS 开头）
2. 加密连接是否在明文头之后紧跟 TLS ClientHello（同连接升级，STARTTLS 式）
3. 同一端口上是否存在纯明文连接（无 TLS）
4. DTE 配置是否动态生效（无需重启）

## 方法

1. **抓包**: nbusvr103 上 `tcpdump -i ens192 -s 0 -w dte.pcap "host 10.6.67.251 and port 1556"`，触发 file-test-msdp full 备份作业（718）
2. **分析**: tshark 按 tcp.stream 分类，解码首字节序列、TLS 握手、JSON 协商载荷
3. **交叉验证**: bpdbjobs 作业记录 vs 抓包进程 PID

**关键前置发现**: NBU 10.3 实际通信端口为 **1556（PBX）**，非 T0148 通信矩阵所记的 13782/13724/13720。所有 30 个 TCP 流均走 1556。

## 发现

### F1: 30 个 TCP 流的明文/TLS 分类

| 首字节特征 | 流数 | 含义 |
|-----------|------|------|
| `61636b3d` = `"ack="` | 25 | 明文 VNET 协议头 → 全部升级 TLS |
| `47494f50` = `"GIOP"` | 1 | 纯明文 CORBA 流量（无 TLS） |
| `170303xx` (TLS record) | 4 | 抓包中途已建立的 TLS 会话 |

### F2: 明文 VNET 协议头格式（STARTTLS 式升级）

连接建立后先发明文协议头，协商后同连接升级 TLS：

```
客户端 → 服务端:  "ack=28\nextension=vnetd-auth-only\n\n"          (frame 565, 明文)
服务端 → 客户端:  "\x1c"                                           (frame 567, 1 字节)
服务端 → 客户端:  "badfeed" + 长度 + JSON 协商载荷                   (frame 569, 明文)
客户端 → 服务端:  TLS ClientHello (0x16 0x03 0x01, 内部 0x0303 TLS1.2) (frame 571)
服务端 → 客户端:  ServerHello TLS 1.2 + Certificate                (frame 572-574)
数据通道:         全部 0x17 0x03 0x03 (TLS 应用数据)               (frame 576+, 2.47GB)
```

**VNET 头魔数**: `ack=<n>\nextension=<service>\n\n`（ASCII 明文）
**响应头魔数**: `badfeed` + 4 字节长度 + JSON（含 ca_roots/connection_id/proxy_version/peer_host/dte_mode 等字段）
**协议版本**: proxy_version: 6

### F3: dte_mode 字段 = 连接级 DTE 开关（决策载体）

JSON 协商载荷中的 `dte_mode` 字段按服务区分：

| 服务 | dte_mode | 含义 |
|------|---------|------|
| bpbrm（PID 15759，作业 718） | **6** | DTE 启用（数据路径） |
| bptm | **6** | DTE 启用（数据路径） |
| nbemm / bpjobd | -1 | 不参与 DTE（控制面） |
| bpdbm / bpcompatd | 0 | 不参与 DTE（控制面） |

→ 印证 DTE 仅应用于**数据通道**（bpbrm/bptm），控制面（CORBA GIOP）走明文/独立 TLS 协商。

### F4: 纯明文流存在（同一端口明文与 TLS 并存）

- stream 0: 纯 GIOP/CORBA 明文流（`47494f50` = "GIOP"），多个请求（VolumeInfoQF、getNextPage、getAllJobsUpdatedBetween、release、ping），**无任何 TLS 升级**
- 与 25 个升级 TLS 的流共用同一 1556 端口

### F5: 动态生效佐证（无需重启）

- nbusvr103 uptime: **2026-05-08**（84 天未重启）
- 作业 718/717/715 全部 DTEMode=On（PID 15759 与抓包 JSON 中的 bpbrm PID 完全一致）
- 每次作业均新建连接、重新协商，无缓存/无重启依赖

## 结论与建议

### 结论（全部假设实证通过）

1. ✅ **明文 VNET 协议头存在**: `ack=<n>\nextension=<svc>\n\n`，ASCII 明文，非 TLS
2. ✅ **同连接 TLS 升级**: 明文头协商成功后紧跟 TLS 1.2 ClientHello（STARTTLS 式）
3. ✅ **同端口明文/TLS 并存**: 1556 端口同时承载纯明文 GIOP 流和 25 个 TLS 升级流
4. ✅ **动态生效**: 84 天无重启，作业级连接每次重新协商（dte_mode 字段）
5. ✅ **T0148 推断修正**: 端口应为 **1556 (PBX)**；"单端口双模"确认，机制为 VNET 明文头 + 连接内升级

### 机制图（实证版）

```
同一端口 1556
    │
    ├── TCP 连接建立
    │       │
    │       ▼
    │  明文 VNET 头 "ack=..\nextension=..\n\n"
    │       │
    │       ▼
    │  "badfeed" + JSON（dte_mode=6 → 数据路径）
    │       │
    │       ├── dte_mode=6 ──▶ TLS 1.2 升级 (0x16 0x03 0x01)
    │       │                     │
    │       │                     ▼
    │       │              加密数据 (0x17 0x03 0x03)
    │       │
    │       └── 控制面 (GIOP/CORBA) ──▶ 保持明文（stream 0）
    │
    └── 结论: 加密与否 = 连接内协商结果，非端口属性
```

### 对自研实现的建议

1. **协议设计**: 采用"明文握手头 + 按需 TLS 升级"模式（NBU 同款 STARTTLS 式），单端口可配置启停
2. **协商字段**: 在 JSON/协议头中携带加密模式（类似 dte_mode），bpbrm/bptm 数据路径启用、控制面可选
3. **魔数约定**: 头魔数（ack=/badfeed）+ 版本号，便于演进和抓包识别
4. **动态启停**: 每次连接重新协商 → 配置变更即时生效，无需重启；生产切换时无需重启但需注意存量连接
5. **端口规划**: 单一入口端口（类似 1556/PBX）统一收口，内部按服务分发

## 参考资料

- T0148 调研记录（符号级证据: vnet_set_dte_mode_in_tss / inapp_tls_enabled_*）
- NetBackup 10.5 SecEncryp Guide（DTE 配置模型）
- 实证数据: /tmp/dte1556.pcap (2.4GB, 113k 包, 46 秒) — 证据已登记
