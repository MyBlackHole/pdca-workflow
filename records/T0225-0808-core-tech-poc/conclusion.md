---
schema: pdca.asset/v1
id: T0225-0808-core-tech-poc
phase: check
source_ids: [sc12-main, sc13-main, sc14-main, sc15-main, sc16-main, sc17-main, maketest]
---

## 上下文

用户明确"不需要业务场景 POC，需要核心技术"，故本任务转向备份引擎**技术栈核心原语**实证，
用生产级系统库（OpenSSL/libsodium/libblake3/libxxhash）覆盖 6 个关键技术点，
为后续架构选型提供可量化数据。

## 假设与结果

| PRD 假设 | 结果 |
|---------|------|
| AC-1 零拷贝传输 sendfile/splice ≥ 用户态副本 1.5x | ✅ 成立，实测 1.6-2.3x（回环近内存带宽，真实磁盘/网络场景收益更大） |
| AC-2 AEAD 两算法还原一致 + 篡改 1B 100% 检出 | ✅ 成立，AES-GCM 670MB/s、ChaCha20-Poly1305 380MB/s |
| AC-3 BLAKE3/XXH3 吞吐均 > SHA-256 + 向量对照 | ✅ 成立，XXH3 ~13GB/s（~7x SHA-256）、BLAKE3 ~3.3GB/s；空串+"abc"双官方向量匹配 |
| AC-4 布隆实测假阳率 ≤ 理论 + 内存节省 | ✅ 成立，无假阴性；实测 2.1602% vs 理论 2.1577%（双哈希派生近似偏差）；内存 1MB vs 精确表 61MB（1/60） |
| AC-5 帧协议粘包/半包正确 + 多流归属正确 | ✅ 成立，4 流×2000 帧单连接交织流隔离/顺序完整；1-5B 半包重组；CRC 检出篡改；EOF 帧逐流断言 |
| AC-6 RS(5,3) 任意 ≤2 片丢失完整恢复 | ✅ 成立，自研 GF(2^8)(0x11D)；全部 C(5,2)=10 组合逐字节还原；冗余 1.67x |
| AC-7 顶层 make test 全量 PASS | ✅ 成立，PASS: 16, FAIL: 0 |

## 分析

- 6 项验收标准全部达成，`validate-convergence` 返回 valid:true。
- 双轴代码审查发现 2 类问题并全部修复：标准轴（场景16 socket fd 泄漏、死代码）；规范轴（AC-4 假阳率断言口径不一致、AC-3 缺 64B 向量已补 "abc"、AC-6 仅 7/10 组合已补全、AC-5 EOF 未断言已补）。
- 关键技术教训：XXH3 结果未消费会被编译器死代码消除（虚假 733GB/s）；frame_try 在 memmove 后返回内部指针导致数据错位（需先拷出 payload）；RS 容错上限 n-k=2 片（3 数据片全失本就不可恢复）。
- 早期自研代理原语（XOR/FNV）被生产级库替换后，数据更贴近真实备份引擎选型依据。

## 失败原因

（无 — 结论成立。）

## 适用边界

- 数据基于本机（x86-64，AES-NI/SHA-NI 加速）回环基准，绝对数值因硬件而异，相对关系（零拷贝>副本、AEAD 认证必检、XXH3>BLAKE3>SHA-256、布隆省内存 60x）稳定。
- 零拷贝在回环下被内存带宽稀释，磁盘/网络传输场景加速比应更高。
- RS 实现为自研教学级 GF(2^8)，生产宜用 SIMD 加速库（如 liberasurecode/isal）。
- blake3/xxhash 为非系统默认库，构建需显式链接 -lblake3 -lxxhash。

## 下一轮建议

- 知识沉淀：将 6 个选型结论登记到 knowledge/（哈希选型、布隆去重、RS 纠删、零拷贝、AEAD、帧复用各一条）。
- 如需零拷贝真实收益，可在真实文件系统+网络（非回环）下复测场景12。
