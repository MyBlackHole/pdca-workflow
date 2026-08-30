---
schema: pdca.asset/v1
id: ontology:domain/benchmark-paired-comparison-noise
type: domain
layer: Knowledge
status: active
summary: 噪声环境下性能断言：配对对比测量
domain:
- ontology:domain/benchmark
relations:
  specializes:
  - ontology:domain/benchmark
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# 噪声环境下性能断言：配对对比测量

来源: records/T0215-0804-rpc-epoll-multireactor/conclusion.md

## 问题

多线程并发基准（本机跑 LLM 客户端/IDE 等）下，单次进程内多 round 的吞吐
方差可达 ±20%（实测 790~1130 MB/s），单次均值比率在 0.89~0.998 间波动。
5% 阈值的"均值 ≥ 0.95×"断言无法用单次测量稳定判定，可能误判通过/失败。

## 模式：配对对比

- **交替执行**：基准配置 A、B 交替各跑 N 个独立进程（N≥4），而不是先跑完
  A 再跑 B。抵消负载随时间漂移。
- **成对比率 + 总体均值**：逐对计算 A/B 比率，报告中位数/均值；同负载漂移
  在配对内被抵消。
- **判定以配对均值比率为准**：配对均值比率 0.984 稳定 ≥ 0.95 判通过，即使
  单次比率出现过 0.89。
- **报告置信**：写明单次 min/max 与配对均值，暴露噪声水平，避免结论掩盖
  测量不确定性。

## 适用边界

- 适用于可重复启动的进程级基准（server 可起停）；对常驻进程内部基准改用
  更长的采样窗口 + 取中位数。
- 系统负载本身波动 > 断言阈值时，配对对比只是可靠下限；更严格需空闲机器
  或 cgroup 隔离 CPU。
