# 修复tls_integration集成测试偶发失败(资源竞争)

## 验收标准

- [ ] AC-1: 循环运行 tls_integration ≥15 次可复现截断失败（复现率 >0）
- [ ] AC-2: 失败特征确认为 wc 计数随机短少（非固定偏移、非挂起）
- [ ] AC-3: 排除清单成立——agent 队列零丢弃、证书路径唯一、端口锁正常、plain 对照稳定
- [ ] AC-4: 双端计数定位至 client Reactor 发送侧提前 EOF（附 DIAGRX 证据）
- [ ] AC-5: 跟进任务 T0347 已创建（parent=T0345）承接根因修复
- [ ] AC-6: tests/tls_exec_stress.sh 资产化，≤5 轮内稳定复现并保留现场日志

## 执行中范围演化与结论收窄（Do 阶段如实记录）

原始假设"端口/证书资源竞争"被证伪。实际定位：**TLS exec 数据面偶发 stdin 截断**——client Reactor 端（client_exec_reactor.cpp）在 credit 流控状态下提前发送 FT_EOF（实证：DIAGRX client eof sent=61440，应发 32MiB；agent 端 received 同步短少且队列零丢弃）。plain 模式 15/15 稳定排除共通层。

根因修复（credit 流控状态机竞态）超出本周期合理范围，经用户决策分拆立项。本任务结论收窄为：**复现方法固化 + 排除清单 + 定位至发送侧**。新增 AC-6（复现脚本资产化）。
