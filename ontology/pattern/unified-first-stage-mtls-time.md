---
schema: pdca.asset/v1
id: ontology:pattern/unified-first-stage-mtls-time
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/unified-first-stage-mtls-time/1.0.0
summary: RPC/rdbcomm 统一第一阶段握手经验
source_task: T0302
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/mtls-handshake]
attributes:
  - name: applicability
    desc: rpc 与 rdbcomm 共用独立明文第一阶段协议的流式 TCP 协议
    constraint: ""
    testable_signal: TIME 返回时间后关闭、NEGOTIATE 升级 mTLS、协商失败不降级为明文
---

# RPC/rdbcomm 统一第一阶段握手经验
# RPC/rdbcomm 统一第一阶段握手经验

RPC 与 rdbcomm 可共用独立的明文第一阶段协议：TIME 返回时间后关闭；NEGOTIATE 返回明文继续或服务端选择的 `ca_cn` 后升级 mTLS；未知 operation 返回明确错误并关闭。

mTLS 升级完成后必须保留 `SSL *`，将会话的读写指针切换到 TLS 实现，APP 原始数据帧不得再次使用裸 fd。多证书客户端按服务端返回的 `ca_cn` 从 `cert_dir/<ca_cn>/` 选择证书。

客户端继续使用既有 TLS 配置参数，不额外引入新的配置参数；服务端启用 TLS 时协商失败不得降级为明文。

来源：T0302 Check 结论及真实 RPC/rdbcomm 进程测试。
