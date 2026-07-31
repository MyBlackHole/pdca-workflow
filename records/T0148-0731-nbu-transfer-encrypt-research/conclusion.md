---
schema: pdca.asset/v1
id: T0148-0731-nbu-transfer-encrypt-research
phase: check
source_ids: [evt-001, convergence-map]
---

## 上下文

目标：调研 10.6.67.187 上 NBU 10.3.0.1 的备份传输加密逻辑（DTE），为本文方案（SM2/SM3/SM4 国密方案）提供参考。

范围：NBU 工具架构、DTE 配置模型、加密库栈、证书体系、网络连接模型、数据流、启动顺序、日志审计、实验验证、安全风险、镜像格式。

## 假设与结果

| 假设 | 验证结果 | 证据 |
|------|---------|------|
| DTE 使用 IN-APP-TLS 加密数据通道 | ✅ 确认 | bpdbjobs DTEMode=On, bptm nbtls_handshake/nbtls_io |
| TLS 版本为 TLS 1.2 | ✅ 确认 | CONNECT_OPTIONS auth=0 enc=2, VMWARE_TLS_MINIMUM_V1_2=YES |
| 加密库为 libnbtls + libnbssl | ✅ 确认 | bptm 符号 nbtls_config/ctx/handshake/io |
| 证书体系 RCA 2048 + NBCA | ✅ 确认 | nbcertcmd -getSecConfig → NBCA:ON ECA:OFF |
| 私钥未加密存储 | ✅ 确认 | PEM 文件检查，仅 600 权限保护 |
| 证书验证关闭 | ✅ 确认 | CONNECT_OPTIONS auth=0 |
| PSK 密钥管理支持 | ✅ 确认 | nbdte_psk_get/put 符号 |
| SCSI 磁带加密支持 | ✅ 确认 | scsi_establish_encryption 符号 |
| 旧版加密已禁用 | ✅ 确认 | ALLOW_ENCRYPTION=NO |

## 分析

### 调研方法充分性

- 远程 SSH 7 轮收集运行时信息
- strings/nm/ldd 对 3 个目标二进制 + 4 个加密库进行静态分析
- 日志分析（nbjm VxUL / bperror / nbauditreport）
- nbdeployutil 配置转储
- 与实际运行环境交叉验证

### 关键发现

1. **DTE 已启用**：file-test-msdp 备份作业 DTEMode=On，使用 IN-APP-TLS 路径
2. **vnetd-proxy 降级备用**：DEFAULT_CONNECT_OPTIONS=0 1 0 允许降级
3. **证书链不完整**：仅 NBCA，无 ECA，证书验证关闭
4. **私钥未加密**：完全依赖文件系统权限，无密码保护
5. **审计覆盖不足**：DTE 配置变更、私钥访问均无审计
6. **镜像格式**：多层容器（Media Header + Backup Header + FRAG + TIR + xfer_block），加密在 xfer_block 级别

## 适用边界

本调研结论适用于：
- NBU 10.3.0.1 build 0042
- CentOS 7.9 + PostgreSQL + MSDP + BasicDisk + VTL 磁带
- 单主服务器 nbusvr103 + 单介质服务器 nbumed103

不适用于：
- NBU 8.x 及之前版本（DTE 机制不同）
- Windows 平台（库栈和目录结构不同）
- 云环境部署

## 下一轮建议

1. 将调研发现的偏差（私钥未加密、证书不验证、AES-CFB 替代 SM4-GCM 等）更新到知识库 nbu-dte-architecture.md
2. 可在测试环境运行一次抓包验证 DTE TLS 1.2 握手证书详情
3. 将 DTE 决策状态机、通信矩阵、安全风险分析纳入本文方案设计文档
