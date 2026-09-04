---
schema: pdca.asset/v1
id: ontology:pattern/mtls-handshake-netorder-libobk
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/mtls-handshake-netorder-libobk/1.0.0
summary: libobk 握手 body 网络序改造经验
source_task: T0362
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/mtls-handshake]
attributes:
  - name: applicability
    desc: libobk 握手帧 body 由主机序统一为网络序
    constraint: ""
    testable_signal: 收发均 htons/ntohs，测试断言契约字节序而非仅行为
---

# libobk 握手 body 网络序改造经验（M5 / T0362）
# libobk 握手 body 网络序改造经验（M5 / T0362）

## 背景
libobk 握手帧 body `{result u16, algorithm u16}` 原主机序收发，与 rdbcomm/dmsbtex/rpc
网络序约定不一致（T0348 审查遗留项）。本任务改为网络序，统一四模块握手协议。

## 改动落点
- 客户端 `libobk/lib/sbt/libobk.c`：发送 `htons(algorithm)`（L138），接收
  `ntohs(result/halg)`（L165/L167）。
- 服务端 `libobk/lib/logic/oracleCmdTbl.c`：接收 `ntohs(halg)`（L880）；三条发送路径均
  `htons(result/halg)`（L99-102 不可用、L116-119 未知算法拒绝、L129-132 OK）；需补
  `#include <arpa/inet.h>`。

## 关键教训（双轴审查捕获）
1. Shotgun Surgery 坏味：裸 `memcpy` 收发 uint16 字段时，`htons/ntohs` 易漏某分支
   （尤其 fail-closed 拒绝帧）。改一处须全路径同步。
2. 测试两侧需同步：模拟对端（`session_test.c`）直接 `_recv` 拒绝帧并比较 `result` 时，
   漏 `ntohs` 会掩盖 wire 字节序错误——测试须断言契约（字节序）而非仅行为。
3. 破坏性变更：外部 oracle 对端（不在仓库）须同步升级，否则握手错位；已列为另排 follow-up。

## 复用建议
- 后续字节序改造优先封装 `put_u16_be`/`get_u16_be` 读写助手，消除裸 `memcpy` +
  `htons/ntohs` 散落。
- 跨模块握手协议统一网络序为既定基线（rdbcomm/dmsbtex/rpc/libobk）。
