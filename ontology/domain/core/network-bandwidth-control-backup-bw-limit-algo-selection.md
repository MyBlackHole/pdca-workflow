---
schema: pdca.asset/v1
id: ontology:domain/network-bandwidth-control-backup-bw-limit-algo-selection
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/network-bandwidth-control-backup-bw-limit-algo-selection/1.0.0
summary: 备份限流算法选型：动态窗口 vs 令牌桶（实测对照）
domain:
- ontology:domain/network-bandwidth-control
relations:
  specializes:
  - ontology:domain/network-bandwidth-control
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q '备份限流算法选型：动态窗口 vs 令牌桶（实测对照）' ontology/domain/core/network-bandwidth-control-backup-bw-limit-algo-selection.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# 备份限流算法选型：动态窗口 vs 令牌桶（实测对照）

## 核心结论

备份/同步引擎需要节流（带宽控制）时，两种算法的实测行为（字节流计时，
4/32 MB/s 两档）：

| 指标 | 动态窗口（产品 bwlimit 思路） | 令牌桶（next_free 推进） |
|------|------------------------------|--------------------------|
| 速率精度 | -0.8% ~ -3.2%（自适应收敛期偏差） | +0.03% ~ +0.06% |
| 抖动（分窗标准差） | <0.2%（32MB/s 档 0.18%） | <0.1%（0.01%） |
| 并发总速率 | 不超上限（锁保护） | 不超上限 |
| 并发公平性 | Jain 指数 ~0.8 | Jain 指数 ~0.8 |
| 突发/慢链路自适应 | 有（thresh 自适应） | 有（burst 上限） |

## 选型规则

1. **高精度平滑节流** → 令牌桶。`next_free` 时间推进模型无累积误差，
   实现要点：每次写入后 `next_free += need/rate`；允许提前消费
   `burst_us = burst/rate` 作为突发上限；`next_free < now - burst_us`
   时钳制到 `now - burst_us`。
2. **需随真实传输速率自适应**（慢链路、突发容忍）→ 动态窗口。
   实现要点：窗口累计字节达到 `thresh` 后，等待
   `(lamt*8/rate - 实际耗时)`；等待过长(≥1s)则 `thresh/=2`，
   过短(<10ms)则 `thresh*=2`（镜像产品 bwlimit 语义）。
3. **并发公平性**（Jain ~0.8 而非 1.0）根源是全局互斥锁串行化：
   先到线程占满当前窗口/令牌。若业务要求更公平，按线程均分速率建
   独立限流器，而非共享一个。

## 适用边界

- 结论基于字节流计时模拟发送（机器写速上界 ~9.8 GB/s），未覆盖真机
  socket 的网络抖动与内核发送缓冲。
- 固定速率档位，未测运行中动态调速。
- 公平指数受机器调度影响，波动 0.73~0.82。

## 复用场景

- 备份/同步工具的网络节流（上传/下载限速）。
- 任何"防业务被挤占"的带宽控制需求。
- 产品 bwlimit 模块（动态窗口）评估其精度/公平性边界。
