---
schema: pdca.asset/v1
id: ontology:domain/data-formats-backup-tools-serialization-practice
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/data-formats-backup-tools-serialization-practice/1.0.0
summary: 备份类程序序列化/存储格式工业实践
domain:
- ontology:domain/data-formats
relations:
  specializes:
  - ontology:domain/data-formats
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 备份类程序序列化/存储格式工业实践

来源：T0217 rpc 序列化补强调研（2026-08-05），面向本项目（备份工具）协议层决策。
依据：PBS 官方文档、restic 官方 design 文档。

## 1. 核心结论

两个主流备份程序（Proxmox Backup Server、restic）**均不使用通用序列化框架**
（无 protobuf/flatbuffers/cap'n proto），采用**自定义紧凑二进制 + 哈希寻址**。
且 **restic 文档明确采用小端（little-endian）**，印证"协议固定小端"是备份领域
标准做法。校验层都做得很重（每 chunk CRC/哈希/MAC）。

## 2. Proxmox Backup Server（PBS）

- **chunk**：`type marker(1B) || data || CRC-32(4B)`，SHA-256 内容寻址
  （chunk 文件名即内容哈希，哈希不匹配=损坏，可离线校验）
- **分块**：固定 4MB（VM 镜像，`.fidx`）/ 动态（文件级，buzhash 滚动哈希内容定义
  分块，`.didx` 存 `(offset, chunk_hash)` 对）
- **索引**：有序 chunk 哈希数组 + 偏移，低 MB 级
- **协议**：HTTP/2 + 自定义 Data Blob；客户端逐 chunk 问"你已有这个哈希吗"，
  仅上传缺失 chunk —— 去重在网络层完成
- **snapshot manifest**：`index.json.blob` 用 JSON 存索引文件列表/哈希/加密元数据

## 3. restic

- **Pack**：`EncryptedBlob1 || ... || EncryptedBlobN || EncryptedHeader || Header_Length`
- **长度字段全部 4 字节小端**（文档明确 little-endian）
- **Blob 头**：`Type(1B) || Length(encrypted_blob,4B LE) || Hash(plaintext)`；
  type=0b00/0b01 数据/树，0b10/0b11 压缩数据/树（format v2, zstd）
- **头放文件尾部**：备份流式写入时不需重写文件；头可独立认证校验
- **索引/锁/snapshot**：JSON（确定性编码），format v2 用 zstd 压缩

## 4. 与本项目对照

| 维度 | PBS | restic | 本项目现状 |
|------|-----|--------|-----------|
| 序列化框架 | 自定义二进制 | 二进制+JSON | 手写 struct+大端 |
| 字节序 | 自定义 | 小端 | 大端（htonl/ntohll） |
| 块大小 | 4MB / 动态 | 变长 | 4MB（RPC_STREAM_BLOCK_SIZE） |
| 校验 | CRC-32 + 哈希寻址 | MAC + 哈希寻址 | 帧级 flags（is_checksum） |
| 元数据 | JSON manifest | JSON | file_stream_meta 手写 |

## 5. 对本项目协议层决策的启示

1. **不引入通用序列化框架**：方向正确，维持手写紧凑布局。
2. **字节序固定小端 + 条件宏**（le32toh/le64toh，小端主机编译为空操作）：
   备份领域标准做法，跨字节序安全且小端零成本。可替代现有 htonl/ntohll。
3. **校验是备份协议的重心**：本项目最大缺口是变长字段长度无上限（可越界读写），
   与字节序选择正交，必须补。
4. 备份软件用哈希寻址做去重/校验，本项目为传输型协议（非内容寻址存储），
   哈希寻址不适用；但"每块带校验"原则可借鉴。
