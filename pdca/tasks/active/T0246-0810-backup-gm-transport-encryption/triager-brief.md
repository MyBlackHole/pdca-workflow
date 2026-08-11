# T0246 Triage Brief

| 项 | 值 |
|----|----|
| 任务 | T0246-0810-backup-gm-transport-encryption |
| 分类 | enhancement → documentation |
| 输入 | `/home/black/Public/aio/aio-tools/6200/release`（项目源码）+ `/home/black/Documents/database_国密/`（8 份国密调研文档） |
| 产出位置 | `/home/black/Documents/备份传输存储加密/`（假定，待确认） |

## 分类与查重

- 输入："编写 PG系列、MySQL系列、文件系统、Oracle、DM、OB、gaussDB 数据库是如何实现备份传输加密支持国密的，画出架构图、数据流图"
- 类别：enhancement（文档编写），scenario_type=documentation
- 查重：
  - T0228（gs_roach 国密验证）——单对象（GaussDB 备份工具），本任务为全量七类对象实现梳理，不重复
  - T0229（OB 备份国密验证）——单对象（OceanBase），本任务含 OB 但为链路接线层面实现梳理，角度不同
  - pdca/knowledge 下无同主题全量实现文档

## Claim 验证（已通过源码/文档核实）

- 项目已含 `third_party/gmssl`（lib_x86_64/lib_aarch64）——GMSSL 双后端有材料基础
- `huanweicloun-sdk-s3-data-backup/my-fuse/cli.cpp` 与 `s3tools/s3file/main.cpp` 已实现 SM4-CBC（gmssl, `--gmssl` 开关，硬编码 key/iv）
- `libs/tls_cert.c` 纯 OpenSSL（Ed25519/AES 套件），`sec_tls_enabled()`/`RPC_TLS_ENABLE` 控制 RPC 链路 TLS（`rpc-net.c:154`、`rpc-server.cpp:199`）
- `aio-speed`/`rdbcomm` 的 `--encrypt` 为 XOR 混淆（`data_encrypt`，非真加密）
- Oracle→libobk.so↔FileTransferAgent(:12000) 裸 TCP；DM→libdmsbtex.so↔dm-ftp(:1255) 裸 TCP
- GaussDB→XBSA（xbsa/rch-tools）；文件系统→fs-backup(内核hook)+aio-speed/aio-speedd；ZFS→S3(华为云 SDK)；PG/MySQL→文件/流式备份(aio-speed --nc xbstream)

## 信息缺口 → P1/P2 Grill

- 产出物格式：单份大文档 vs 按对象分文件 vs 每对象一份
- 图风格：Mermaid vs ASCII vs 两者
- 是否需要"现状-目标-改造路径"三段式 vs 仅现状实现
- 文件系统类别（fs-backup vs ZFS→S3 vs 两者皆含）
- NFS 介质层是否纳入
- 术语表 / 参考文档清单是否附带

## 建议下一步

P1 澄清需求 → P2 grill 确认 → P3 PRD → P6 终审 → 进入 Do