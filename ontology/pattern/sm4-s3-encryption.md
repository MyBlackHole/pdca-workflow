---
schema: pdca.asset/v1
id: ontology:pattern/sm4-s3-encryption
type: pattern
layer: Knowledge
status: active
summary: SM4 S3 对象存储加密子模式（s3file 工具 SM4 加密上传）
relations:
  specializes:
    - ontology:pattern/sm4-storage-encryption
  relates_to:
    - ontology:entity/aio-tools-6200-release
attributes:
  - name: s3_sm4_upload
    desc: S3 对象存储 SM4 加密上传
    constraint: S3 对象存储的 s3file 工具 SM4 加密上传，对象落盘前加密
    testable_signal: "运行 grep -q 's3file' /home/black/Public/aio/aio-tools/6200/F/139/备份传输存储国密SM4全流程加密方案.md 且 grep -q 'S3' /home/black/Public/aio/aio-tools/6200/F/139/备份传输存储国密SM4全流程加密方案.md 命中"
---

# SM4 S3 对象存储加密子模式

> 源：`sm4-storage-encryption` 的 `S3` 四场景之一

## 架构

```mermaid
flowchart TD
    A[s3file 工具] --> B[SM4 加密]
    B --> C[S3 对象存储]
```
Source: `file: F/139/备份传输存储国密SM4全流程加密方案.md:1`

## F/143 落改细节（T2107，2026-09-09）

> 来源 record：`records/T2107-0909-guomi-storage-research/`（行号级重验，零代码改动）

- 写端现状只分支 `gmssl==1`（`s3tools/s3file/main.cpp:923,954`），key/IV 硬编码（`:919-922`）；GCM 需每对象随机 12B nonce 并新增 `sm4-nonce` 元数据。
- 读端现状按卷开关解密（`s3mount/fuse-file.cpp:224,823,914`），需按对象 `gmssl` 自适应；`config.cpp:129-136` bool 口径需扩为三态。
