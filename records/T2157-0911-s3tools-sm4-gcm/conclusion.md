# Check 结论：T2157 s3tools SM4-GCM 支持与 CBC 兼容（T2157-0911-s3tools-sm4-gcm）

## 验收对照（PRD ## 验收标准）

- [x] AC-1：`s3tools_sm4_compat_test` 全绿（CBC 与 gmssl
  字节一致无退化）。证据 E9（E2 已被替换）。生产 CBC 已切 openssl4 EVP 同 key/iv。
- [x] AC-2：`s3tools_sm4_gcm_test` 全绿：GCM 往返
  （0/1/15/16/17/100/4096）、密文与 Tag 各翻转 1bit 拒绝、1 万 nonce 无碰撞、
  hex 非法拒绝、非法 gmssl 画像拒绝、严格解析溢出拒绝、流式与一次性分段
  一致（1/7/16/17/100 切分、空 update、误用拒绝）、8 线程×200 轮混合压力
  一致、ThreadSanitizer 零竞争。证据 E8/E15/E16。
- [x] AC-3：`gmssl=0/1/2` 分发矩阵在单测内全覆盖（meta2/1/0/缺失/非法 × 本地
  0/1/2，含能力门禁与歧义回落）；老版本读新 GCM 对象必失败属设计预期
  （R3 门禁，单测 `meta2/local1 gate rejected` 锁定新端行为；老端按配置
  误解密/透出由升级门禁与挂载清理覆盖，属上线操作项）。
- [x] AC-4：minio 真实落盘 e2e 全绿（证据 E13）：GCM 对象 Head 可见 4 元数据且
  `file-size`=原文长度，下载解密一致，CBC 卷读 GCM 被拒；新写 CBC 元数据
  如实（1/原文长度）；存量歧义对象（标 0 的 CBC）在 CBC 卷可读；明文卷直通。
  未覆盖：完整 `upload-snapshot` zfs 流 e2e（需 zfs 环境，CI 无），其加解密
  与元数据拼装逻辑与 e2e 覆盖的 helper/接口为同一代码。
- [x] AC-5：`s3file_config_test` / `s3mount_config_test`（含三态与 key/iv
  用例：缺省即旧值防漂移、自定义生效、非法拒绝）与 `rdb_config_test` /
  `param_registry_test` / `rpc_param_test` 全绿。证据 E4。
- [ ] AC-6：`s3tools_version` 已递进至 1.0.1.6；提交（含十要素）待用户下达
  “提交”后执行。

## 判定

verdict 建议：confirmed（代码范围；AC-6 提交动作待执行，AC-3/AC-4 残余为
环境与上线操作项，已如实记录）。

## 残余风险

1. 快照 `PutObject` 补元数据后，老版本读新对象行为：本地 1 误解密明确报错、
   本地 0 静默透出——上线必须先升读端并清理关闭解密的旧挂载点（PRD 升级门禁）。
2. `my-fuse`（huanweicloun）仍用 gmssl CBC，不在本次范围；其读新 GCM 对象会失败，
   如需互通须另立项。
3. release 模式构建未在本轮执行（debug 已验证链接机制与模式无关），打包前需补一次。
