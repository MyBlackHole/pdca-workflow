---
schema: pdca.asset/v1
id: T0524-0903-research-zfs-encrypt-transform
phase: check
source_ids: [research-encrypt-transform, ontology-zfs-crypto, convergence-map]
---

## 上下文

任务 T0524 隶属 Transform 三栈全覆盖研究，聚焦 `ontology:domain/zfs-crypto` 的 `encrypt` 分支深化（`AES-GCM/SM4-GCM` 加密与 `ZIO transform` 栈 `encrypt` 分支）。Plan 阶段经 4 轮 Grill 明确范围为 `encrypt` 全栈深化（`AES-128/256-GCM/CCM + SM4-GCM` 套件与 `ZIO_STAGE_ENCRYPT/DECRYPT` 压栈-弹栈及 `abd` 替换与 `IV/salt` 双分支），PRD 定义 3 项 AC 覆盖研究报告、本体细化与证据链。Do 阶段已产出 `research-encrypt-transform.md`（41075B）与 `ontology:domain/zfs-crypto` 细化（27008B，280 行），经 `register-evidence` 登记 3 条并生成 `evidence/convergence.json`，`validate-convergence` 验证 `valid:true`，`ontology-validate` OK 且 `islands:0`，现进入 Check 对照 PRD/证据/收敛条件逐项验收。

## 假设与结果

- 假设：ZIO transform 栈中 encrypt 可经 `zio_crypt_table[ZIO_CRYPT_FUNCTIONS]` 的 `zio_crypt_info_t（ci_mechname/ci_crypt_type/ci_keylen/ci_name）` 表驱动建模，`AES-128/256-GCM/CCM + SM4-GCM` 七套件与 `ZIO_STAGE_ENCRYPT(1<<6)` 压 `zio_push_transform(NULL)` / `zio_read_bp_init` 压 `zio_decrypt` 及 `abd` 替换与 `IV/salt` 双分支（`!dedup→get_salt+generate_iv 随机 / dedup→HMAC 确定性 / ZIL 已生成`）及 `DVA[2]+blk_fill/cksum[2..3]` 编码可经 C4 L3 + 时序 + 状态机三图一图穷尽，且本体 `transform_encrypt_branch` 可深化至 `encrypt_func/zio_crypt_table/IV/salt + ZIO pipeline` 协同并经 `grep -q 'zio_crypt'` 回归，证据链可经 `manifest.jsonl + convergence.json` 闭环。
- 结果：假设全部成立。研究报告 3 图全覆盖且每图可溯 `openzfs/zfs file:line`（`grep -c '```mermaid'` =6 ≥3，`grep -c 'Source:'` =15 ≥3），覆盖 `AES-128/256-GCM/CCM` 与 `SM4-GCM` 及 `ZIO_STAGE_ENCRYPT/DECRYPT` 压栈-弹栈及 `abd` 替换与 `IV/salt` 双分支；本体 `transform_encrypt_branch` 已细化至表驱动与 `ZIO_STAGE_ENCRYPT` 七分支及 `abd` 替换与 `IV/salt` 双分支及 `DVA/cksum` 编码，`attributes` 4 项（`algorithm_suite_coverage/key_hierarchy_depth/datapath_traceability/transform_encrypt_branch`）、决策树/正反例/门禁齐全，`testable_signal` 含 `grep -q 'zio_crypt'` 命中；证据链 `manifest.jsonl` 3 条、`convergence.json` 3 项逐条回链 `meta.convergence`，`validate-convergence` `valid:true` 无 issues，`ontology-validate` OK 且 `islands:0`。

## 分析

- **AC-1** ✅ 研究报告 `research-encrypt-transform.md` 含 3 类 mermaid（C4 L3 `graph TD`、时序 `sequenceDiagram`、状态机 `stateDiagram-v2`，实测 `grep -c '```mermaid'` =6 ≥3）且每图附 `Source: openzfs/zfs file:line`（`grep -c 'Source:'` =15 ≥3，每图 `%% Source:` inline + 紧跟 `*Source:` 外联，双重可溯），覆盖 `AES-128-GCM`（`ZIO_CRYPT_AES_128_GCM, SUN_CKM_AES_GCM, ZC_TYPE_GCM, 16B`）、`AES-256-GCM`（`ZIO_CRYPT_AES_256_GCM, 32B, ON_VALUE`）、`AES-128/256-CCM`（`SUN_CKM_AES_CCM, ZC_TYPE_CCM, CCM_PARAMS`）、`SM4-GCM`（`ZIO_CRYPT_SM4_GCM=9, SUN_CKM_SM4_GCM, ZC_TYPE_GCM, 16B`）七套件与 `zio_crypt_table[ZIO_CRYPT_FUNCTIONS]`（`zio_crypt.c:198`）及 `ZIO_STAGE_ENCRYPT=1<<6（zio_impl.h:137）` / `ZIO_WRITE_PIPELINE 含 ENCRYPT（zio_impl.h:224）` / `zio_encrypt 七分支（zio.c:4953）` / `zio_decrypt 回调（zio.c:571）` / `zio_push_transform/zio_pop_transforms（zio.c:502）` / `zio_read_bp_init 压 zio_decrypt（zio.c:1806）` / `spa_do_crypt_abd 双分支（dsl_crypt.c:2826）` / `zio_do_crypt_uio CCM/GCM 分支（zio_crypt.c:394）` / `encode_params_bp（zio_crypt.c:751）+ encode_mac_bp（zio_crypt.c:810）` 的压栈-弹栈及 `abd` 替换（`grep -q 'zio_crypt_table' && grep -q 'ZIO_CRYPT_AES_128_GCM' && grep -q 'ZIO_CRYPT_SM4_GCM' && grep -q 'ZIO_STAGE_ENCRYPT' && grep -q 'zio_decrypt' && grep -q 'zio_push_transform' && grep -q 'zio_pop_transforms' && grep -q 'abd.*替换'` 全部命中），`IV/salt` 双分支 `zio_crypt_generate_iv（662, random_get_pseudo_bytes 12B）` 与 `zio_crypt_key_get_salt（361, atomic_inc_64≥400M→hkdf）` 与 `zio_crypt_generate_iv_salt_dedup（724, HMAC）` 均命中，满足 PRD 对 `≥3 mermaid + Source + AES/SM4-GCM全覆盖含 abd替换` 的要求。（research-encrypt-transform）
- **AC-2** ✅ `ontology:domain/zfs-crypto` 本体 `transform` 视角已深化 `transform_encrypt_branch`：`constraint` 覆盖 `ZIO_STAGE_ENCRYPT(1<<6)` 在 `ZIO_WRITE_PIPELINE（WRITE_COMPRESS后、CHECKSUM_GENERATE前）` 的位置与 `zio_pipeline[6]=zio_encrypt`、`zio_encrypt(zio.c:4953)` 七分支（`GANG/非allocating/非encrypted/RAW/L>0/OBJSET/!ENCRYPTED/主加密`）与 `zio_decrypt(zio.c:571)` 三段回调、`zio_push_transform/zio_pop_transforms(502)` 的 `zt_orig_abd/zt_bufsize/zt_transform` 链与 `abd` 替换（`eabd psize/NULL`）、`zio_read_bp_init(1806)` 的 `PROTECTED→push(zio_decrypt)` 读侧压栈、`spa_do_crypt_abd(2826)` 的 `salt/IV` 双分支（`!dedup→get_salt+generate_iv 随机 / dedup→generate_iv_salt_dedup HMAC确定性 / ZIL已生成`）、`zio_crypt_key_get_salt(361)` 的 `atomic_inc_64 + 400M→hkdf` 轮换、`zio_crypt_table[ZIO_CRYPT_FUNCTIONS](198)` 的 7 套件（`aes-128/192/256-ccm/gcm + sm4-gcm`）与 `ZC_TYPE_CCM/GCM`、`zio_do_crypt_uio(394)` 的 `CCM/GCM` 参数分支与 `crypto_encrypt/decrypt(ECKSUM)`、`ZIL(init_uios_zil:1403)` 的 `zil_chain_t.zc_eck` 与 `DNODE(init_uios_dnode:1615)` 的 `bonus` 特化及 `no_crypt` 短路，经 C4 L3 与时序/状态机可一图建模，`attributes` 数量 4（`algorithm_suite_coverage/key_hierarchy_depth/datapath_traceability/transform_encrypt_branch`）≥3 且每条 `testable_signal` 含 `grep -q 'zio_crypt'`（`grep -c "testable_signal.*grep -q"` =5），新增 `transform_encrypt_branch` 的 `testable_signal` 含 `grep -q 'zio_crypt' && grep -q 'ZIO_STAGE_ENCRYPT' && grep -q 'zio_encrypt' && grep -q 'zio_decrypt' && grep -q 'zio_push_transform'` 全命中，正文 `wc -l` =280 ≥80 且含 `## 5. Encrypt-Transform 分支`、`## 6. 决策树`（`flowchart TD` mermaid，覆盖 `zio_encrypt 七分支→salt/IV双分支→ABD替换→VDEV→read侧pop→ECKSUM` 全链）、`## 7. 正例`（6 例：`SM4-GCM选型`/`pipeline位图配对`/`随机IV/salt编码`/`dedup确定性`/`读侧压栈逆序弹栈`/`ZIL/DNODE特化`）、`## 8. 反例`（10 例：`pipeline漏ENCRYPT明文落盘`/`错把ENCRYPT当非栈手写MAC`/`漏pop悬挂密文`/`dedup随机IV去重失效`/`非dedup用HMAC泄露相等性`/`ZIL手造salt/IV失配`/`DNODE无bonus仍push`/`CCM/GCM参数混淆`/`400M轮换漏atomic_inc`/`byteswap遗漏`）、`## 9. 门禁`（12 条：`多图/溯源/套件覆盖/transform栈/IV/salt/编码/正文/属性/本体校验/脚手架/收敛/T0500回归`）、`## 10. 证据与追溯` 均齐全，`grep -q '决策树' && grep -q '正例' && grep -q '反例' && grep -q '门禁' && grep -q 'Encrypt-Transform'` 全部命中，`ontology-validate --ontology-dir ontology` 返回 `OK` 且 `ontology_graph --format summary` `islands:0`，`ontology_test_scaffold --node ontology:domain/zfs-crypto` 可产且 `pytest --collect-only` 7 项，满足 AC-2 对 `transform视角深化、attributes≥3、决策树/正反例/门禁、testable_signal含 grep -q 'zio_crypt'` 的要求。（ontology-zfs-crypto）
- **AC-3** ✅ 证据链完整：`evidence/` 含 `research-encrypt-transform.md`（41075B, `sha256:561da82287ae40853750d3cf084d0259b407966fce019a350aba3470d8530b92`）与 `zfs-crypto.md`（27008B, `sha256:0495bd2886181b3374af7b89aeda420ee3b4942f96795bae7a30ed33bc4915a2`）及 `convergence.json`（581B, `sha256:2d88fd6b0d62f5e24f682f9f6fa1b3d1f62a6848aa1f345b7297ae0729e158e0`），`manifest.jsonl` 3 条登记（`research-encrypt-transform` → AC-1/AC-3、`ontology-zfs-crypto` → AC-2/AC-3、`convergence-map` → AC-1/2/3 且 `evidence_type_ref: ontology:entity/evidence-convergence-map`），`convergence.json` 3 项逐条回链 `meta.convergence`（1: research报告含3 mermaid+Source覆盖加密/解密 → AC-1；2: ontology:domain/zfs-crypto transform视角深化 → AC-2；3: grep zio_crypt命中 → AC-3），`validate-convergence --task-dir pdca/tasks/0903-research-zfs-encrypt-transform` 返回 `valid:true` 无 issues，`evidence_issues` 0，`manifest` 中 `size/digest` 与实文件一致且 `convergence.json` 文件物理存在，`grep -q 'zio_crypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_crypt' ontology/domain/zfs-crypto.md` 双命中，满足证据链完整性。（convergence-map, research-encrypt-transform, ontology-zfs-crypto）

## 失败原因

无（verdict 为 confirmed，3 项 AC 全部达成）。

## 适用边界

- 研究范围限定为 `openzfs/zfs#master` 的 `include/sys/fs/zfs.h:1954-1969` / `include/sys/zio_crypt.h:38-121` / `include/sys/crypto/common.h:84` / `module/os/linux/zfs/zio_crypt.c:32-487,662-854,1403-2075` / `module/zfs/zio.c:502-538,571-702,1806-1827,4953-5096,5800-5828` / `module/zfs/dsl_crypt.c:2826-2919` / `include/sys/zio.h:127,362` / `include/sys/zio_impl.h:137,224` 的 `enum zio_encrypt→zio_crypt_table→HKDF/salt/IV双分支→ABD替换→压栈-弹栈` 分支，未深至 `metaslab` 的 `DVA_ALLOCATE` 数值调参、`vdev_queue` deadline 数值、`QAT` 硬件阈值调参、`sm4_impl.c` 的 S-box/L 线性变换细节、`objset/indirect MAC` 的 `HMAC-SHA512` 细节（见 `T0500` 六层模型）与性能压测。
- 本体 `ontology/domain/zfs-crypto.md` 当前为 280 行合并版（含 `T0500` 六层模型与 `T0524` transform 视角深化），与 `evidence/zfs-crypto.md` 快照（27008B）为同一内容落盘，无实质差异；行号以 `grep -n zio_crypt/zio_encrypt/zio_crypt_table/zio_crypt_generate_iv` 重锚可抵御上游漂移。
- 结论可复核性依赖 `file:line` 行号与 `grep` 门禁，ZFS 上游行号漂移需以 `grep -n ZIO_ENCRYPT_/zio_crypt_table/zio_crypt_key_get_salt` 重锚，`grep -c '```mermaid'` 与 `grep -c 'Source:'` 双门禁已在报告附录自检脚本中显式给出；`SM4` 轮函数仅点到复用 `gcm` 框架。

## 本体沉淀

- 决策：`ontology:domain/zfs-crypto` 已沉淀（`ontology:domain/zfs-crypto` 的 `transform_encrypt_branch` 深化至 `encrypt_func/zio_crypt_table/IV/salt生成与 ZIO transform协同`，含决策树/正反例/门禁，且 `attributes` 4 项均含 `testable_signal grep -q` 可回归；`records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md` 与 `ontology/domain/zfs-crypto.md` 双轨可复核）。
- 依据：`research-encrypt-transform.md` 3 类 mermaid 每图附 `Source: openzfs/zfs file:line` 覆盖 `AES-128/256-GCM/CCM + SM4-GCM` 与 `ZIO_STAGE_ENCRYPT/DECRYPT` 压栈-弹栈及 `abd` 替换与 `IV/salt` 双分支，本体 `wc -l 280`、`ontology-validate OK`、`islands:0`、`validate-convergence valid:true`，`manifest.jsonl` 3 条登记对齐。
- 处置：本体已在本任务 Do 阶段落盘并经 evidence 登记，无需另建 `ontology:pattern/research-diagram-methodology` 或 `ontology:concept/pdca-task` 新节点；`records-only` 不适用。
- 可复核：`grep -q 'zio_crypt' ontology/domain/zfs-crypto.md && grep -q 'ZIO_STAGE_ENCRYPT' ontology/domain/zfs-crypto.md && grep -q 'zio_encrypt' ontology/domain/zfs-crypto.md` 命中；`grep -c '```mermaid' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md` =6 且 `grep -c 'Source:'` =15。

## 下一轮建议

- 将本研究报告 C4 L3（套件选型 `enum→table→ZC_TYPE→CK_PARAMS`）与时序（`WRITE_COMPRESS→ENCRYPT压栈abd替换→VDEV→read侧pop DECRYPT`）与状态机（七分支+IV/salt双分支+ABD替换）三图作为 `skill-research` 后续 ZFS 加密相关调研的模板样例，并在 `ontology:domain/zfs-crypto` 的 `transform视角` 回链；后续 `zfs-dmu/zfs-spa` 可直接复用决策树扩展加密分支，无需回滚。
- 以 `grep -q 'zio_crypt_table' module/os/linux/zfs/zio_crypt.c && grep -q 'ZIO_CRYPT_SM4_GCM' include/sys/fs/zfs.h` 定基线、`grep -q 'zio_crypt' records/T0524-.../research-encrypt-transform.md && grep -q 'ZIO_STAGE_ENCRYPT' include/sys/zio_impl.h` 与 `validate-convergence` 门禁脚本化纳入 CI；高吞吐池（>1.6PB/400M×4K）评估收紧 `zfs_key_max_salt_uses` 模块参数，以 `kstat` 与 `zio_crypt_key_get_salt` 的 `atomic_inc` 监控。
- `T0500` 回归门禁（`grep -q 'Wrapping.*AES-256-CCM' ontology/domain/zfs-crypto.md`）与 `T0523` 压缩分支门禁（`grep -q 'zio_compress' ontology/entity/zfs-zio.md`）均已在本体 `## 门禁` 中显式保留，后续归档无需额外回归；`QAT SM4_GCM` 的 `EOPNOTSUPP` 软回退与 `dedup HMAC` 的相等性泄露权衡已在反例中显式约束。

## 判定

- verdict.outcome: **confirmed**
- reason: 3 项 AC 全部达成，研究 3 mermaid+15 Source 覆盖 AES-128/256-GCM/CCM+SM4-GCM 与 ZIO_STAGE_ENCRYPT/DECRYPT压栈-弹栈及abd替换与IV/salt双分支，本体 transform_encrypt_branch深化至encrypt_func/zio_crypt_table/IV/salt与pipeline协同且4 attrs+决策树正反例门禁280行，证据链manifest 3条+convergence 3项valid:true且ontology-validate OK islands:0
- verdict_id: T0524-confirmed-20260902
- at: 2026-09-02T10:10:24+08:00

**verdict**: confirmed
