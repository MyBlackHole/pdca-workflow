# 解压 openssh-9.6p1-16.oe2403sp4 源码包 — PRD

## 问题陈述

- **现状**: `/home/black/Downloads/openssh-9.6p1-16.oe2403sp4.src.rpm` 已下载但未解压，源码树与补丁不可访问
- **目标**: 解压 src.rpm，得到完整源码树与补丁；产出 openssh 国密（SM2/SM3/SM4）支持清单
- **差距**: 无可用工作目录，无法阅读源码与审计补丁

## 解决方案

1. 用 `rpm2cpio | cpio` 解压 src.rpm 到目标目录 `/home/black/Downloads/openssh-9.6p1-src/`
2. 目标目录按 `src/`（源码树）与 `patches/`（全部补丁）组织，根目录放 `openssh.spec`
3. 尝试校验 `openssh-9.6p1.tar.gz.asc` GPG 签名，失败不阻塞
4. 展开 `openssh-9.6p1.tar.gz` 为源码树
5. 基于补丁内容产出国密支持清单（SM2 密钥/KEX、SM3 摘要/MAC、SM4 加密）

## Seam 分析

### 测试接缝

- 验证手段为命令执行 + 产物检查（文件存在、目录结构、关键文件），无需单测。

### 声明的测试接缝

本任务为源码解压+审计型操作，无测试产物，跳过 seam 声明。

### 验收可测性

- 每个 AC 可通过文件系统命令独立判定。

## 用户故事

1. 作为开发者，我想要解压 openssh src.rpm 并确认国密支持，以便进行国产化适配/安全审计。

## 实现决策

- 目标目录：`/home/black/Downloads/openssh-9.6p1-src/`
- 目录组织：`src/` + `patches/` + 根级 `openssh.spec`
- 签名校验：尝试 `.asc`，失败仅记录不阻塞
- 源码树：展开 tar.gz 到 `src/openssh-9.6p1/`
- 国密清单：依据 `feature-add-SMx-support.patch` 与 `adaption-for-feature-sm2-support.patch` 实际内容生成

## 测试决策

- 无测试代码；验收依赖命令执行与产物检查。

## 验收标准

- [ ] AC-1: `/home/black/Downloads/openssh-9.6p1-src/` 存在，包含 `openssh-9.6p1.tar.gz`、`openssh.spec` 及全部补丁（文件计数与 rpm 包内清单一致）
- [ ] AC-2: 补丁按 `patches/` 目录组织，国密相关补丁（SMx、SM2 适配）可定位
- [ ] AC-3: `src/openssh-9.6p1/` 源码树已展开（configure 脚本/README 存在）
- [ ] AC-4: `.asc` 签名校验已执行并记录结果（成功或失败原因）
- [ ] AC-5: 国密支持清单已输出，覆盖 SM2 密钥/KEX、SM3 摘要/MAC、SM4 加密各算法名

## 范围外

- 不构建 rpm/源码
- 不应用补丁、不做代码修改
- 不产出补丁内容逐行审计（仅国密算法支持点清单）

## 备注

- 国密证据来源（triage 已核查）：
  - `feature-add-SMx-support.patch`：SM2 密钥（ssh-sm2.c）、`sm2-sm3` KEX（kexsm2.c）、`sm4-ctr` cipher、`hmac-sm3`/`SSH_DIGEST_SM3`
  - `adaption-for-feature-sm2-support.patch`：OpenSSL 3.x EVP 下 `EVP_PKEY_is_a(res,"SM2")` + `sm2_pkey_to_ec_key()` 适配
  - spec `Patch61` 应用 SMx 补丁，默认构建启用
