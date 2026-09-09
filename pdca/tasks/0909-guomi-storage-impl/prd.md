# 存储国密方案在本项目落改点调研（T2099·纯调研）

## 背景

《存储国密加密技术方案.md》（`/home/black/Public/aio/F/143/存储国密加密技术方案.md`，547行，已评审通过）要求存储落盘三类全覆盖：ZFS内核透明加密（ICP第9套件SM4-GCM）、S3按`--gmssl`三态（0明文/1 CBC/2 GCM+`sm4-nonce`）、NFS客户端`--enc-algo`预加密。本任务是**纯调研**：把“若在本项目（`/home/black/Public/aio/aio-tools/6200/F/143`）落地”所需的差距定位、落改点清单、风险与外部依赖写成报告，**不修改本仓任何代码**。

纠正说明：建票时误判为`development`并提示代码修改，经用户纠正按边界规则（纯报告→`research`）转回；`T2100–T2102`三个实现子票已废止（`active=false`，无产物）；`phase`保持`do`未动门禁。

Grill对齐结论（clarifications.jsonl round1-7，均captured:true）：范围=全量承接（S3+NFS+ZFS）；S3=按方案三态；密钥=白话“同钥不换钥”；验收=报告可验；另补aio-speed缺失项、自我审查、技术文档Y1-Y7对齐三轮。

## 目标

- S3：`--gmssl`三态差距、读端自适应缺口、元数据与卷校验冲突逐点定位到文件行号；
- NFS（aio-speed）：传输已具备与存储缺失拆分，`--encrypt` XOR非合规声明；
- ZFS：本仓无内核源码，承接参数与外部依赖清单化；
- 密钥白话：同钥不换钥、存量CBC只读，写进报告；
- Y1-Y7对齐矩阵：哪些本仓可改、哪些记外部依赖。

## 范围

输入：方案文档 + 本仓 `s3tools/s3file/main.cpp`、`s3tools/s3mount/fuse-file.cpp`、`s3tools/libs/obs-service.cpp`、`s3tools/libs/s3_service_frame.h`、`s3tools/s3file/config.cpp`、`rpc/rpc-client.cpp`、`rpc/rpc-common.cpp`。
输出：`research-report.md`（差距定位+落改点清单+Y对齐矩阵，≥3 mermaid图+可复核来源）。
不做：不改本仓代码、不跑fio实测、不做容量规划、不做密钥轮换、不改NBU/ZFS内核、不改传输TLS。

### 已定位差距（代码实测，报告详写）

- `s3tools/s3file/main.cpp:919-922` 与 `s3tools/s3mount/fuse-file.cpp:819-822`：SM4密钥与IV硬编码固定复用，不符合GCM每对象随机nonce要求；
- CLI `--gmssl`（`main.cpp:139,165,1246`，`atoi`无值域校验）与配置文件`gmssl`（`config.cpp:129-136` bool型仅0/1，`config_test.cpp:72-76`拒`2`）口径不一致；写/合并读只分支`gmssl==1`（`main.cpp:923,954,1155`），无GCM分支；
- `s3tools/s3mount/fuse-file.cpp:224,823,914`：读端按卷配置解密，未按对象元数据自适应；
- `s3_service_frame.h:50-58` + `obs-service.cpp:319-329,380-390`：元数据仅`gmssl`+`file-size`，无`sm4-nonce`（需`meta_data_count` 2→3）；
- `main.cpp:1488-1493`卷级强一致校验阻断三态过渡；
- `rpc/rpc-common.cpp:446-464`：`--encrypt`为静态XOR非真加密；传输`--tls-algorithm TLS_SM4_GCM_SM3`（`rpc-client.cpp:489,693-704`）已具备。

## 需求（报告目录）

1. S3写端落改点：CLI+config三态统一、`sm4-nonce`元数据、GCM随机nonce、收发同钥不换钥；
2. S3读端落改点：按对象`gmssl`分支、fail-closed不重试、升级门禁（读端先行+旧挂载点清理）、卷校验过渡策略；
3. NFS落改点：新增`--enc-algo`语义、清单字段、管理侧半写收敛、`--encrypt` XOR非合规声明；
4. ZFS承接清单：`encryption=sm4-gcm`、`load/unload-key`、`send/recv`继承、灰度只测内环（外部依赖）；
5. Y1-Y7对齐矩阵：Y2/Y3/Y6/Y7本仓可改，Y1/Y4/Y5外部依赖；3.8清单表达与3.9日志落点要求。

## 验收标准

- [ ] AC-1 差距逐条定位到文件行号，复核可重走（`grep`+`Read`可验）
- [ ] AC-2 落改点清单含接口变化（参数值域、元数据键、`meta_data_count`、分支语义）无遗漏
- [ ] AC-3 aio-speed传输/存储拆分与XOR非合规声明已写入
- [ ] AC-4 Y1-Y7对齐矩阵完整，外部依赖与非目标与方案一致
- [ ] AC-5 `research-report.md`通过先调研门禁（mermaid≥3、Source≥3、http Source≥1、URLs≥2）
- [ ] AC-6 全程零代码改动（`git status`干净可验）

## 关联本体节点

```
ontology:concept/pdca-task
ontology:concept/pdca-evidence
ontology:concept/pdca-verdict
```

## 拆分映射

- 差距定位与落改点清单 -> ontology:concept/pdca-task
- Y对齐矩阵与外部依赖 -> ontology:concept/pdca-evidence
- 报告门禁与零改动验证 -> ontology:concept/pdca-verdict
