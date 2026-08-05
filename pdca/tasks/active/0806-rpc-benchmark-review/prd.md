# T0220 rpc 基准复核：就地化+小端后的吞吐/并发净收益量化

## 问题陈述

T0217 消除 data memcpy + 小端替换 bswap，bench_download/bench_concurrent 需重新测量量化净收益

## 验收标准（草案）
- [ ] AC-1: bench_download 吞吐对比 T0215 基线
- [ ] AC-2: bench_concurrent 并发扩展性复核
- [ ] AC-3: RPS 基准复核
