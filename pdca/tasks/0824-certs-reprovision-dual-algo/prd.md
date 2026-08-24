# 【F】现网证书体系统一重签与目录规范化 — 规格文档

## 问题陈述

- **现状**: /opt/aio/cfg/certs 数据混乱：ed25519_ca.crt 内容实为 MySM2RootCA（SM2 CA）拷贝；host.crt 由无关 UUID CA 签发；存在 My_SM2_Root_CA/、MySM2RootCA/ 两个重复 CA 目录及 t0388tmp 等测试残留；服务端 ED25519 profile 因数据无效被 T0390 降级跳过，AES mTLS 不可用。
- **目标**: 以 keygen 统一重签一套自洽的双算法 CA 体系并按新布局规范部署，双算法（SM4 国密 + AES/ED25519）mTLS 实机全部可用。
- **差距**: 证书内容与命名错位、目录冗余、ED25519 链无效。

## 解决方案

1. 备份现有 certs → certs_bak_20260824_pre_t0391；
2. keygen 重签：
   - SM2 CA「My_SM2_Root_CA」（沿用现有有效 CA，不重签其根）：根 sm2_ca.* + 新签 sm2_host.*；
   - ED25519 CA「My_ED25519_Root_CA」新生成：根 ed25519_ca.* + 签发 ed25519_host.*；
   - 客户端子目录：My_SM2_Root_CA/{sm2_ca.crt,sm2_host.*} 与 My_ED25519_Root_CA/{ed25519_ca.crt,ed25519_host.*}（sign -n 自包含输出）；
3. 清理：t0388tmp、MySM2RootCA（重复）、无主 UUID 目录与散文件移入备份目录（不删除）;
4. 重启 aio-speedd 验证双算法握手。

## Seam 分析

### 测试接缝
research/运维操作场景，无代码测试产物。验证手段为 openssl 检视 + 实机握手。

### 声明的测试接缝
- 无（环境操作任务，验证以命令复核留痕）

### 验收可测性
- 每个 AC 用命令输出独立判定。

## 用户故事

1. 作为 `运维人员`，我想要一套命名规范、链路自洽的证书目录，以便排查问题时不再被错位内容误导。

## 实现决策

- 仅操作环境与记录，不改产品代码。
- SM2 根 CA 复用现有（T0387 签发的 My_SM2_Root_CA），避免客户端已部署信任的变更。

## 测试决策

- openssl x509 校验 subject/issuer 链关系；实机双算法 aio-speed 握手作为最终验收。

## 验收标准

- [ ] AC-1: 根目录四件套齐全且链正确——sm2_host 由 My_SM2_Root_CA 签发、ed25519_host 由 My_ED25519_Root_CA 签发（openssl issuer 断言）
- [ ] AC-2: 两个客户端子目录各自自包含三件套且与其根 CA 同源
- [ ] AC-3: 服务端启动日志无 serving plain only、无 profile 跳过警告
- [ ] AC-4: 双算法实机握手成功——默认 SM4 与 --tls-algorithm=TLS_AES_256_GCM_SHA384 均执行命令返回
- [ ] AC-5: 目录规范化完成——测试残留移入备份，certs 根仅保留规范文件

## 范围外

- 产品代码变更
- 其他主机/环境的证书分发

## 备注

- 遗留②调查结论：协商逻辑无缺陷（按协商算法取对应 profile CA CN），MySM2RootCA 错发系 ed25519_ca.crt 内容污染所致，本任务重签后自然消解。
