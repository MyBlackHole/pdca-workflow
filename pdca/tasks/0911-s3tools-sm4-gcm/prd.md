# PRD：s3tools 支持 SM4-GCM，CBC 兼容旧数据

> 任务 T2157｜分支 `6.2.0.0/F/143`｜依据《存储国密加密技术方案》3.2/3.4/四/五（Y2/Y3/Y7）

## 1. 背景与目标

现状 `s3tools` 仅支持 SM4-CBC（`gmssl=1`，固定 key/iv），快照 bundle 上传走
`PutObject`（无对象元数据），加解密完全由本地配置决定。目标：

1. 新增 SM4-GCM 写能力（`gmssl=2`），GCM 与 CBC 统一用项目内 `openssl4 EVP`
   实现（已验证两者与 gmssl 输出逐字节一致，见已提交的兼容测试）。
2. SM4-CBC 读写兼容旧版本：新选 CBC 时默认沿用旧 key/iv，存量 CBC 对象
   无需改写即可解密。
3. 读端（s3file 合并读、s3mount 挂载读）按对象元数据 `gmssl` 自适应分支，
   解密失败一律 fail-closed。

## 2. GCM 落盘格式（纯元数据方案）

对象内容 = 纯密文，不拼接；全部加密表达放对象元数据：

| 元数据键 | 值 | 适用对象 |
| --- | --- | --- |
| `gmssl` | `0`=明文 / `1`=CBC / `2`=GCM（复用现有键，扩展值域） | 全部（新写） |
| `file-size` | 原文长度（语义不变） | 全部（新写） |
| `sm4-nonce` | 每对象随机 12B nonce 的 hex（24 字符） | 仅 GCM |
| `sm4-tag` | 16B GCM Tag 的 hex（32 字符） | 仅 GCM |

为何优于“Tag 缀对象尾”：

1. 审计只需 `HeadObject` 即可核对全部加密表达，无需下载对象，符合方案
   3.8“清单 → 介质表达 → 密钥登记”与“`HeadObject` 即可审计”；
2. 长度语义干净：GCM 密文长度恒等于原文长度，可用 `content-length`
   交叉校验 `file-size`，对不上直接 fail-closed 检出截断；空明文 GCM
   内容 0B 无歧义；
3. CBC/明文对象只写原来 2 个元数据，旧行为零扰动；
4. Tag 缺失/损坏在取 head 阶段即可 fail-closed，不浪费下载流量；
5. 编解码集中在一处 helper，Upload/Download 两侧对称。

密钥与随机数：GCM 复用同一 16B 固定 key（与 CBC 同 key，轮换按卷/桶粒度
另立项，见方案四）；nonce 每对象 `RAND_bytes` 随机，失败则 fail-closed
拒绝上传。

## 3. 功能需求

1. CBC 切 `openssl4 EVP`：替换 `s3file/main.cpp`（加密 1 处、解密 1 处）与
   `s3mount/fuse-file.cpp`（解密 1 处）的 gmssl 调用，key/iv/缓冲策略不变。
2. 元数据层扩展：新增 `GetKeyNonce()/GetKeyTag()`；`matadata` 数组 2→4；
   `UploadObsObject`/`S3Service::PutObject` 新增可携带 nonce/tag 的重载
   （保留旧签名向后兼容）；快照 bundle 上传按 `gmssl` 写入对应元数据。
3. s3file 写 GCM：`--gmssl=2` 时每对象随机 nonce → `EVP SM4-GCM` 加密 →
   上传密文 + 4 元数据；父块合并读先取父对象元数据再选分支解密。
4. 读端自适应：按对象元数据 `gmssl` 值选分支（2/1/0）；存量快照对象无
   元数据时回落本地配置（CBC/明文）；Tag 校验失败、nonce 缺失、模式越权
   一律报错，不跨模式降级重试。
5. s3mount 三态：`enableGmssl` 0=明文卷（读到加密对象报错，不再静默透出）、
   1=CBC 卷（允许 0/1，读到 2 报错）、2=GCM 卷（0/1/2 全自适应）。
6. 配置三态化：`--gmssl` 与 `[s3file]gmssl` 统一为 0/1/2（默认 0）；
   `PARAM_S3FILE_GMSSL` 由 bool 改 int 枚举；CLI 加 0–2 校验与 help；
   更新 `config_test` 第 5 用例（`gmssl=2` 由拒绝改合法）。
7. 升级门禁：先升级全部读端（s3mount/s3file）到双模式版本，再允许配置 GCM；
   清理关闭解密的旧挂载点。

非目标：密钥轮换、传输链路国密、`my-fuse`（`huanweicloun-sdk-s3-data-backup`）
改造、容量规划。

## 4. 任务拆解

1. CBC 切 openssl4 EVP + 已提交兼容测试保持绿色回归。
2. 元数据层扩展（nonce/tag 键 + Upload/PutObject 重载）。
3. s3file 写 GCM（含父块 GCM 合并读）。
4. 读端自适应（s3file 合并读 + s3mount 挂载读 + 缺 meta 回落 + 三态门禁）。
5. 配置三态化（rdb-config + CLI + config 单测更新）。
6. GCM 单测（往返/篡改拒绝/nonce 唯一性/meta 编解码）+ minio 手工 e2e + 版本递进。

## 5. 设计调整（用户评审，Check 前增补）

- 流式接口：`sm4-crypto` 新增 `S3Sm4StreamCtx`（init/update/finish，
  GCM 加密专用 `finish_get_tag`、解密专用 `set_tag`），分段结果与一次性
  逐字节一致（单测锁定 1/7/16/17/100 切分、空 update 交错）；一次性接口
  基于流式实现。生产调用点保持一次性调用（bundle/块缓冲本就有界），流式
  接口面向后续大文件与流式场景。
- 严格解析加固：元数据整数一律严格解析（`s3_parse_int_strict`），`gmssl`
  非法值记 `-2` 直接 fail-closed；`INT_MAX` 长度上限守卫；解析溢出先判后乘。
- 多线程：全部接口无共享可变状态（上下文按调用分配）；key/iv 经互斥锁读写
  （配置重载亦安全）；GCM provider cipher 进程单例（pthread_once，不释放）。
  证据：8 线程 ×200 轮混合压力单测 + ThreadSanitizer 零竞争（E12）。
- key/iv 友好存放：`[s3file]/[s3mount]` 新增 `sm4_key/sm4_iv`（32 hex，
  默认旧值保兼容，非法 fail-closed 拒绝启动）；启动时一次性加载（提交点
  前先生效，失败不污染）；读写端须持同一 key（s3mount 默认与写端一致，
  不一致则解密失败 fail-closed）。

## 6. 风险与回滚

风险：快照 `PutObject` 补元数据后，老版本读新对象（`gmssl=2` 无 meta 读取
能力）误处理——由升级门禁拦截（读端先行），残留旧挂载清理后方可配置 GCM。
回滚：去掉 GCM 配置恢复原 `--gmssl` 值，读端保持双模式；代码 revert 本次
提交。

## 验收标准

- [ ] AC-1: `xmake run s3tools_sm4_compat_test` 仍全绿（CBC 字节一致无退化）
- [ ] AC-2: 新增 GCM 单测全绿：往返一致、翻转 1bit 拒绝、nonce 唯一直到 1 万对象无碰撞、缺 nonce/tag 的 fail-closed
- [ ] AC-3: `gmssl=0/1/2` × 新老读端互通矩阵：读端自适应正确，解密失败 fail-closed 且不跨模式重试
- [ ] AC-4: minio 手工 e2e：`--gmssl 2` 上传后 `HeadObject` 可见 4 元数据且 `file-size`=原文长度；s3mount（`enableGmssl=2`）挂载读一致；切回 `1`/`0` 仍可读旧对象
- [ ] AC-5: `s3file_config_test/s3mount_config_test` 全绿（含三态用例）
- [ ] AC-6: `s3tools_version` 已递进，提交信息含十要素
