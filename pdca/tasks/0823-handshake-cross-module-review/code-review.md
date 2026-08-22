# 四模块握手字节序与白名单一致性审查（AC-1）

## 审查范围

`rdbcomm` / `libobk`(sbt) / `dmsbtex` / `rpc` 四模块握手收发代码（T0354–T0362 落地），维度：字节序、白名单/fail-closed、错误帧完整性、测试覆盖。

## 字节序一致性结论

四模块握手 body 均为**网络字节序**，已统一：

- **rdbcomm**：`buf_put_u16`/`buf_get_u16` 底层 `POKE_U16`/`PEEK_U16` 为大端写读（`libs/buf.h:301-303`、`325-330`）→ 网络序。
- **dmsbtex**：`network.c:139/213/228/246` 显式 `htons`；`164-165` `ntohs`。
- **libobk**：`libobk.c:138/165/167`、`oracleCmdTbl.c:99-132/882` 显式 `htons`/`ntohs`（M5 改造）。
- **rpc**：`rpc-protocol.cpp:175-176/194-195` 结构体 `htons`；`183-184/203-204` `ntohs`。

**结论**：M5 仅改 libobk 是对齐另三模块，四模块字节序一致，无跨模块回归。

## 白名单 / fail-closed 结论

- **rpc**：`hs_negotiate_algorithm` 白名单 + 所有拒绝分支均发帧（`rpc-server.cpp:250-298`，含 `HS_ERR_CA_CN`）。
- **rdbcomm**：T0357 修复静默回落 `slot[0]`；未知算法显式拒绝发帧；`ca_cn unavailable` 发 `RDB_HS_ERR_CA_CN`（`server.c:517-521`）。
- **libobk**：T0357 白名单 + M5 网络序。
- **dmsbtex**：`unknown-algorithm` 发 `DM_HS_ERR_ALGORITHM`；`no-TLS-context` 发 `DM_HS_ERR_MTLS_UNAVAILABLE`；`ca_cn unavailable` 原**缺帧**（本任务修复，见 `code-diff.md`）。
