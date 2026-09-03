# PRD — 调研ZFS直连PCIe国密SM4加密卡可行性及PCIe加密卡选型与对接方式（T0539）

> 任务：T0539 / 0903-research-zfs-pcie-sm4 / scenario: research / phase: plan

## 背景与问题

`ontology:domain/zfs-crypto` 已覆盖 ZFS 原生加密（含 `SM4-GCM` 补丁 `0001-icp-add-SM4-GCM-encryption-suite.patch`），但当前 `SM4-GCM` 仅走 `generic GCM` 软实现（`gcm_impl.c:632` 强制分支，禁用 AVX/QAT），`qat_crypt.c` 对 `SM4_GCM` 直接返回 `EOPNOTSUPP` 软回退。用户提出：**ZFS 能否直连 PCIe 国密 SM4 加密卡？有哪些卡可选？分别支持什么对接方式？** 需以源码链路+网络选型双轨回答可行性、选型与对接改造路径。

## 目标

1. 判定 ZFS 直连 PCIe SM4 加密卡的可行性，给出 QAT/KCF/SDF 三路径对比与边界。
2. 产出主流 PCIe 国密 SM4 加密卡选型清单（≥3 厂商 ≥5 型号，含性能/接口/合规/形态）。
3. 明确 ZFS 对接 PCIe SM4 卡的三种对接方式及各自内核/用户态边界与 ZFS 改造量。
4. 给出推荐选型、推荐对接方式及 PoC 验证路径与风险清单。

## 非目标

- 不做实际硬件采购与驱动编译验证（本任务为调研，PoC 仅给路径）。
- 不改 ZFS 源码（仅给出改造点与 patch 思路）。
- 不做全量国密合规审计（仅标注二级/三级等合规等级）。

## 术语

- **SDF**：`GM/T 0018` 密码设备应用接口规范，国密 PCIe 卡通用用户态/内核态接口（`SDF_OpenDevice/SDF_Encrypt` 等）。
- **KCF/ICP**：ZFS 内核密码框架（Illumos KCF 移植至 `module/icp`），`zio_crypt` 经 `crypto_encrypt` 调 KCF，QAT 为 KCF 硬件 provider 之一。
- **QAT**：Intel QuickAssist，仅加速 `AES-GCM`，不支持 `SM4_GCM`（`qat_crypt.c: EOPNOTSUPP`）。
- **AF_ALG**：Linux 内核 `AF_ALG` 套接字，用户态经 `sendmsg/recvmsg` 调内核 crypto API。

## 方案方向（待Grill确认）

拟采用“源码链路+网络选型”双轨：

1. **ZFS 链路剖析**：追 `zio_crypt.c:198` `zio_crypt_table`→`zio_do_crypt_uio:394`→`qat_crypt`→`KCF`，确认 SM4 软回退点与 QAT 边界。
2. **PCIe 卡选型**：搜国密 PCIe 卡（派科/渔翁/江南天安/信安世纪等），提炼性能/接口/合规/形态四维对比。
3. **对接方式设计**：三路径——A) KCF 新增 SM4 provider（`module/icp` 注册 `SUN_CKM_SM4_GCM` 硬件 provider）B) ZFS 侧 SDF 直调（`dsl_crypt.c:2826` 分支新增 `sdf_encrypt`）C) `AF_ALG` 桥接（用户态 `zfs` 命令经 `AF_ALG` 调卡，内核态需 `kapi`）。
4. **可行性判定**：按“是否需改 ZFS 核心/是否内核态/是否合规闭环”给出推荐与 PoC 步骤。

备选：仅做网络选型不碰 ZFS 源码；或仅做 ZFS 链路不做选型。

## 验收标准

- [ ] AC-1 ZFS 链路与可行性：报告含 `zio_crypt_table → qat_crypt → KCF` 调用链图（mermaid≥1）及 QAT 不支持 SM4 的源码锚点（`file:line`），并给出三路径可行性判定（可行/有条件/不可行）
- [ ] AC-2 选型清单：报告含 ≥3 厂商 ≥5 型号的 PCIe SM4 加密卡对比表（厂商/型号/接口/算法/性能/合规/形态/价格区间/信源），每项有 Source 行号或官网链接
- [ ] AC-3 对接方式：报告含三种对接方式的时序/架构图（mermaid≥1）及每种方式的内核/用户态边界、ZFS 改造点（`file:line`）、优缺点与成本（人日）
- [ ] AC-4 收敛可验证：报告已落 `records/T0539-0903-research-zfs-pcie-sm4/` 且 `ontology-validate` 0 issues，`convergence map` 逐条回链 AC-1..3

## 约束

- 网络调研须结构化产出（问题拆解→搜索策略→信息整理→结论），非简单堆链接。
- 源码锚点须为本仓库可复现的 `file:line`（如 `module/os/linux/zfs/qat_crypt.c:xx` 或 `ontology/domain/zfs-crypto.md:xx`）。
- 选型须标注信源可信度（官网/白皮书/第三方测评）。

## 风险

- 国密 PCIe 卡驱动多为闭源，内核对接需厂商配合 → 通过 SDF 用户态路径缓冲。
- ZFS KCF 新增 provider 需改 `module/icp`，合规与上游合并成本高 → 给出最小侵入的 AF_ALG/SDF 备选。
- 性能数据多为厂商标称，需标注“未实测”并给出压测方法。

## 开放问题（进Grill）

见 clarifications.jsonl 首轮 frontier 5问。
