---
schema: pdca.asset/v1
id: ontology:principle/cli-tls-mtls-configuration
type: principle
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/cli-tls-mtls-configuration/1.0.0
summary: 工具 CLI TLS/mTLS 配置约定
source_task: T0323
relations:
  specializes: [ontology:principle]
  guides: [ontology:entity/tls-configuration]
attributes:
  - name: applicability
    desc: 同时提供明文和 mTLS 的客户端/服务端工具配置入口
    constraint: ""
    testable_signal: 参数解析拒绝未知算法和非 0/1 的 mTLS 值，并输出工具名及参数名
---

# 工具 CLI TLS/mTLS 配置约定
# 工具 CLI TLS/mTLS 配置约定

## 适用场景

适用于同时提供明文和 mTLS 连接的客户端/服务端工具，需要在不改变握手协议与业务帧的前提下暴露启动时配置。

## 约定

- 统一使用 `--mtls-enable=0|1` 和 `--tls-algorithm=<受支持算法>`。
- 配置优先级固定为：CLI > 工具环境变量 > 工具专属配置段 > `[security]` > 默认值。
- 工具名、配置段名、环境变量名和算法名集中定义为共享宏。
- CLI 值在进程启动时注入共享配置解析层，TLS 初始化只读取解析后的有效配置。
- 参数解析必须拒绝未知算法和非 0/1 的 mTLS 值，并输出工具名及参数名。
- help 必须同步说明合法值、默认值、优先级和可直接复制的 CLI 示例。

## 边界

该约定只负责工具配置入口，不负责证书路径、`ca_cn` 选择、握手帧或第二阶段业务帧；这些仍由既有安全配置和协议实现负责。
