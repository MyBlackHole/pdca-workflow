# GMSSL TLCP 传输总结测试报告（2026-08-03）

## 测试条件

- 环境：本机回环（127.0.0.1），Linux，单线程流式收发，每项 3 轮取 median
- 三组：明文 TCP / OpenSSL 常规 TLS（mTLS，AES-GCM 套件）/ GMSSL TLCP（SM4-CBC + HMAC-SM3，修复版库）
- 证书：demo-bench/gmssl_bench（CA/SM2 双证书，口令 bench）

## 一、端到端传输对比（MB/s / 耗时 median）

| 档位 | 明文 TCP | OpenSSL TLS (AES) | GMSSL TLCP (SM) | GMSSL/明文 |
|------|---------|-------------------|-----------------|-----------|
| 128 MB | 54.1 ms · **2367 MB/s** | 131.9 ms · **970 MB/s** | 2284 ms · **56.0 MB/s** | 42× 慢 |
| 512 MB | 211.6 ms · **2419 MB/s** | 548.2 ms · **934 MB/s** | 9263 ms · **55.3 MB/s** | 44× 慢 |
| 1024 MB | 434.8 ms · **2355 MB/s** | 1040.6 ms · **984 MB/s** | 18742 ms · **54.6 MB/s** | 43× 慢 |

要点：
- 明文 ~2.4 GB/s（回环大包直传），OpenSSL TLS ~0.95 GB/s（AES-NI 硬件加速，记录层开销限制），GMSSL TLCP ~55 MB/s（纯软件 SM4/SM3）
- GMSSL TLCP 稳定在 55±1 MB/s，不随数据量波动；相对明文慢 42-44×，相对 OpenSSL TLS 慢 17-18×

## 二、加密层对比

### SM4-GCM 吞吐（512 MB，软件实现）

| 实现 | 吞吐 |
|------|------|
| OpenSSL | **112.0 MB/s** |
| GMSSL | **32.1 MB/s**（3.5× 慢） |

### SM2 操作耗时（us）

| 操作 | OpenSSL | GMSSL | 比值 |
|------|---------|-------|------|
| sign+verify | 1048 us | 2952 us | 2.8× 慢 |
| encrypt+decrypt | 1229 us | 2824 us | 2.3× 慢 |

## 三、差距归因分析

1. **算法硬件加速（主因）**：AES-GCM 用 AES-NI+PCLMULQDQ（单算法 7.7-8.6 GB/s）；SM4/SM3 在 x86 无指令加速（软件 ~120/160 MB/s 量级）。同为 SM4-CBC 时 GMSSL 与 OpenSSL 持平（1.03×），证明库实现质量非瓶颈
2. **TLCP 协议结构**：SM4-CBC + HMAC-SM3（MAC-then-Encrypt，每记录约 2-3 遍 SM3 数据量）比 GCM 多 ~1.8× 计算量
3. **GMSSL GCM 实现低效**（若用 GCM 反而更慢）：`gf128_mul` 逐比特软件乘法（128 轮/块），AVX 版被 `reverse_bits` 位反转拖垮，无查表优化 → 32 MB/s 仅 OpenSSL 同算法 1/3.5
4. **SM2 软件实现**：GMSSL 比 OpenSSL 慢 2.3-2.8×（无 SM2 硬件加速的基数上还有实现差距），握手一次性开销

## 四、结论

- GMSSL TLCP 端到端 ~55 MB/s：对千兆备份（线速 ~110 MB/s）国密加密成为瓶颈（~50% 线速）；万兆场景差距更大
- 若需提升：① 使用带 SM4/SM3 硬件扩展的 CPU（ARMv8.2/国产芯片）；② 修复 GMSSL GHASH 查表与 AVX 字节序转换；③ 换用国密 TLS 1.3 GCM 套件（需先优化 GCM 实现）
- 当前修复版（databuf 越界 fix）传输功能正确，性能与修复前一致（无额外开销）
