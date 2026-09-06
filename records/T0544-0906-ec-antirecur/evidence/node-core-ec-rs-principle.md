---
schema: pdca.asset/v1
id: ontology:domain/core-ec-rs-principle
type: domain
layer: Knowledge
status: active
summary: RS纠删数学原理：有限域/生成矩阵/编解码全流程
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-rs-math
  - ontology:domain/core-ec-rs-algorithm
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: RS 纠删数学原理理解、PQ 语义溯源场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文数学断言与 io.c 调用语义一致"
- name: constraints
  desc: 原理边界前提
  constraint: 见正文
  testable_signal: "通读正文三节，确认只讲 bcachefs 用到的 P/Q 子集数学，不展开通用编码理论"
---

# RS 纠删数学原理（bcachefs 子集）

沉淀自 T0543 补充（用户要求讲算法原理本身）。对照 bcachefs
`fs/data/ec/io.c:56-110` 调用语义；数学以 bcachefs 用到的 P/Q
子集为界，不展开通用编码理论。

## 算法原理

1. **有限域 GF(2^8)**：字节即域元素，加法即异或（无进位），乘法
   查对数表。选它只因字节对齐、运算可表驱动加速。
2. **P 即异或方程**：P = D1⊕D2⊕…⊕Dn。丢任一块，余块异或即得。
   n 元一次方程，解唯一。对应 `raid5_recov`。
3. **Q 即第二方程**：Q = g^0·D1 ⊕ g^1·D2 ⊕ …（g 为域生成元）。
   P、Q 联立解任意 2 块。对应 `raid6_gen_syndrome`。
4. **生成矩阵视角**：单位矩阵加 P 行（全 1）加 Q 行（幂系数）。
   编码即矩阵乘，解码即解方程组。
5. **解码即验算**：重算 syndrome，全零即好，非零定位求解。对应
   `raid_rec` 先验后算。

## 解决了什么问题

- **空间换安全可计算**：n 块数据加 1-2 块 parity，坏 1-2 块可恢复，
  空间放大从多副本的 2-3 倍降到 1.2 倍以内，且可精确算出。
- **恢复有数学保证**：线性方程组解唯一，不是启发式猜测，恢复结果
  可证明正确。
- **上限明确**：方程数决定可恢复数，超限必炸，不给虚假安全感。

## 引入了什么问题

- **计算开销**：每次写算 P/Q，每次重建解方程组，CPU 与内存带宽
  双重税。bcachefs 用后台整桶编码把税移到离峰，但税仍在。
- **小写放大**：改 1 块需读全条重算 parity（RMW），前台小写场景
  不可用——这正是 bcachefs 选后台路线的原因，代价是窗口期空间
  放大。
- **数学黑盒风险**：委托内核库意味着信任其域表实现；自研则无人
  审计。两害取其轻，bcachefs 选信任内核。

## 实际问题与修复

1. **删指针误删兄弟块**：现网疏散时同条双块 extent 被误删一指针（`90a55e64a`）。修复：按块号双键精确匹配。教训：身份必须双键，单键假设同槽唯一是错的。
2. **缓冲释放竞态 UAF**：修复中途退出时在途 IO 写已释放内存（`bc66229c9`）。修复：先同步后释放。教训： teardown 顺序与 setup 逆序是铁律。
3. **创建与移除竞态漏防**：复用旧条长期累积，移除守卫只看已发布群体（`d6e40165c`）。修复：fencing 覆盖累积中群体。教训：生命周期各阶段都要进守卫视野，无例外群体。
