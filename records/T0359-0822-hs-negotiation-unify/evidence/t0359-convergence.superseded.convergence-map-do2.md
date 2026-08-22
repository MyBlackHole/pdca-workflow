# T0359 收敛映射（四模块 → libs/common.h 单一来源）

## 枚举收敛（真实定义唯一在 libs/common.h）
| 模块 | 原枚举（已删） | 统一枚举 | 兼容别名 |
|------|---------------|----------|----------|
| rdbcomm | `RDB_HS_ALG_TLS_SM4_GCM_SM3`(=1) / AES(=2) | `HS_ALG_TLS_SM4_GCM_SM3`(=1) / AES(=2) | `#define RDB_HS_ALG_*` |
| libobk | `OBK_HS_ALG_TLS_SM4_GCM_SM3`(=1) / AES(=2) | 同上 | `#define OBK_HS_ALG_*` |
| dmsbtex | `DM_HS_ALG_TLS_SM4_GCM_SM3`(=1) / AES(=2) | 同上 | `#define DM_HS_ALG_*` |
| rpc | `HS_ALG_SM4_GCM_SM3`(=1) / AES(=2) | 同上 | `#define HS_ALG_SM4_GCM_SM3` 等 |

数值契约不变：`HS_ALG_DEFAULT=0` / `HS_ALG_TLS_SM4_GCM_SM3=1` / `HS_ALG_TLS_AES_256_GCM_SHA384=2`。

## 映射函数收敛（实现唯一在 libs/hs_algorithm.c）
| 模块 | 原本地函数（已删） | 统一函数 | 调用方式 |
|------|-------------------|----------|----------|
| rdbcomm | `rdb_hs_algorithm_name` / `rdb_hs_algorithm_from_name` | `hs_algorithm_name` / `hs_algorithm_from_name` | 宏别名 `rdb_hs_algorithm_name` |
| libobk | `obk_hs_algorithm_name` / `obk_hs_algorithm_from_name` | 同上 | 宏别名 `obk_hs_algorithm_name` |
| dmsbtex | `dm_hs_algorithm_name` / `dm_hs_algorithm_from_name` | 同上 | 宏别名 `dm_hs_algorithm_name` |
| rpc | `hs_algorithm_name` / `hs_algorithm_from_name` | 同上 | 直接调用 |

## 死代码删除（零调用，已删定义+声明）
- dmsbtex/protocol.c: `dm_hs_encode` / `dm_hs_decode` / `dm_hs_decide`
- dmsbtex/protocol.h: 对应声明

## 协商语义（语义 B，四模块一致）
采纳客户端算法 + 白名单拒绝（fail-closed），服务端不再回落配置：
- rpc 经 T0357 去除回落，改用 `hs_negotiate_algorithm`（白名单拒绝）；
- rdbcomm / libobk / dmsbtex 本就无条件采纳合法算法，合法值由统一映射表界定（即白名单）。
四模块决策路径语义统一，无第二套协商逻辑。

## 链接收敛（消除独立链接隐患）
libobk(`sbt`/`FileTransferAgent`) 与 dmsbtex(`dmsbtex`/`dm-ftp`) 主目标均加 `add_deps("tls_cert")`，
统一实现 `hs_algorithm.c` 经 `tls_cert` 静态库传递可达。
