---
schema: pdca.asset/v1
id: T0162-0731-nbu-dte-packet-capture
phase: check
source_ids: [evt-001]
---

## 上下文

任务 T0162：抓包验证 T0148 推断的"NBU 单端口同时支持 TLS 与明文"机制。T0148 通过符号分析推断为 STARTTLS 式（明文协议头 + 同连接 TLS 升级），但未抓包实证。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| 同一端口上存在明文 VNET 协议头 | ✅ 实证 | frame 565: `ack=28\nextension=vnetd-auth-only\n\n`（ASCII 明文） |
| 加密连接在明文头后同连接升级 TLS | ✅ 实证 | frame 565(明文) → 569(JSON) → 571(TLS ClientHello 1.2) → 572(ServerHello) |
| 同端口存在纯明文连接 | ✅ 实证 | stream 0 纯 GIOP/CORBA 明文流，无 TLS |
| DTE 配置动态生效无需重启 | ✅ 实证 | 84 天 uptime + 每次作业新连接协商（dte_mode 字段） |
| 通信端口为 1556 (PBX) | ✅ 修正 | 30 个 TCP 流全部走 1556，非 T0148 所记 13782/13724 |

## 分析

### 协议机制（实证）

```
同一端口 1556 (PBX)
  ├── 明文 VNET 头: ack=<n>\nextension=<service>\n\n
  ├── badfeed + JSON 协商载荷（含 dte_mode 字段）
  ├── dte_mode=6 (bpbrm/bptm 数据路径) → TLS 1.2 升级
  └── 控制面 (GIOP/CORBA) → 保持明文
```

### 关键发现

1. **VNET 协议头魔数**: `ack=<n>\nextension=<svc>\n\n`，响应 `badfeed` + 4 字节长度 + JSON
2. **dte_mode 字段**: 数据路径（bpbrm/bptm）= 6，控制面（nbemm/bpjobd/bpdbm）= -1/0
3. **加密与否 = 连接内协商结果，非端口属性** → 配置变更即时生效
4. **T0148 通信矩阵端口修正**: 实际为 1556 (PBX)

### 调研方法充分性

- tcpdump 抓包 113k 包/2.4GB/46 秒，覆盖完整作业（718）
- tshark 按流分类 + 首字节解码 + JSON 载荷解析
- 作业记录交叉验证（PID 15759 ↔ bpdbjobs）

## 适用边界

- 仅验证 nbusvr103 ↔ nbumed103（10.3.0.1）的 IN-APP-TLS 路径
- 未验证 vnetd-proxy 降级路径（当前环境全部 TLS 升级）
- 未验证低版本客户端（<9.1）交互
- 未验证 DTE=Off 时的纯明文数据流（当前环境 DTE=On）

## 下一轮建议

1. 将实证结论更新到 knowledge/nbu/nbu-dte-architecture.md（新增"单端口协商机制"章节 + 修正端口）
2. 自研 TLS 实现参考此模式：明文握手头 + 按需升级 + 每次连接重新协商
3. 如需完整覆盖：在 DTE=Off 环境下抓包验证纯明文数据通道
