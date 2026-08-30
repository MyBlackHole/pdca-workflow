---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc-aead-auth-encryption
type: domain
layer: Knowledge
status: active
summary: 备份传输加密：AEAD 认证加密（AES-GCM vs ChaCha20-Poly1305）
domain:
- ontology:domain/core-tech-poc
relations:
  specializes:
  - ontology:domain/core-tech-poc
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# 备份传输加密：AEAD 认证加密（AES-GCM vs ChaCha20-Poly1305）

## 核心结论

备份数据传输/落盘加密需**认证加密（AEAD）**——同时保证机密性 + 完整性，
防止篡改。本机实测：

| 算法 | 吞吐 | 硬件加速 | 认证 |
|------|------|---------|------|
| AES-128-GCM | ~670 MB/s | AES-NI | 篡改 1B → 100% 检出 |
| ChaCha20-Poly1305 | ~380 MB/s | 无（软件） | 篡改 1B → 100% 检出 |

## 选型规则

1. **x86-64（有 AES-NI）** → AES-128-GCM（快 ~1.76x）。
2. **ARM/无 AES-NI 或需恒定时间软件实现** → ChaCha20-Poly1305。
3. **必须验证 tag**：解密后不校验认证 tag 等于没有完整性。篡改任意
   1 字节密文/tag，认证必须失败——这是 AEAD 与非 AEAD（如裸 AES-CBC）
   的本质区别。
4. 备份链路"先压缩后加密"（场景07 已证体积更优），加密层用 AEAD 同时
   覆盖传输与静态完整性。

## 适用边界

- GCM 需注意 96-bit nonce 复用风险（每次加密必须唯一 nonce）。
- 本测为单线程回环；多线程/多流可并行 AEAD 获得更高聚合吞吐。

## 复用场景

- 备份数据加密管道（传输 + 落盘）。
- 加密层的选型依据（AES-NI 有无决定算法选择）。
