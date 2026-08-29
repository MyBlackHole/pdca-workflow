---
schema: pdca.asset/v1
id: ontology:pattern/sbt-config-mtls-override
type: pattern
layer: Knowledge
status: active
summary: init_sbt_config 配置文件键解析模式（dmsbtex）
source_task: T0366
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/tls-configuration]
attributes:
  - name: applicability
    desc: dmsbtex/sbt.c 增加 --key=value 解析写入 tls_cfg
    constraint: ""
    testable_signal: 解析块置于 --backup-dirs 之前；基线+仅覆盖存在键；非法 fail-closed
---

# init_sbt_config 配置文件键解析模式（dmsbtex）
# init_sbt_config 配置文件键解析模式（dmsbtex）

## 适用场景
在 `dmsbtex/sbt.c` 的 `init_sbt_config(const char *cfg, dmsbtex_t *sbt)` 中为 `sbt-config.conf` 增加新的 `--key=value` 解析，并写入 `sbt->tls_cfg`（或类似结构体）时。

## 关键陷阱：解析块位置
`init_sbt_config` 在解析完 `--checksum-enabled`/`--compress-enabled` 后，会处理 `--backup-dirs`；**当配置不含 `--backup-dirs` 时走 `goto next__` 直接跳到尾部初始化**，会跳过其后所有代码。

- **错误**：把新键的解析块放在 `--backup-dirs` 处理之后 → 配置文件不含 `--backup-dirs` 时新键永远不被解析。
- **正确**：新键解析块放在 `--backup-dirs` 处理**之前**（在 `sbt->backup_dirs_num = 0;` 之前插入），确保所有配置路径都经过解析。

## 优先级模式：基线 + 仅覆盖存在的键
mTLS 状态/算法来源存在 env/ini 与配置文件两个渠道：

- 先以 `sbt_tls_config_init(&sbt->tls_cfg)` 完成全集（含 `cert_dir`，来自 env/ini）基线初始化；
- 随后**仅当配置文件存在对应键**时才覆盖（用 `file_xxx_present` 标志驱动），键缺失则跳过、沿用 env/ini 基线，不要强制置默认；
- 值非法时 fail-closed 返回 `-1`，与 `sec_resolve_bool` 范式一致，不静默降级。

## 测试接缝（无头文件改动）
`dmsbtex_t` 为 `sbt.c` 私有结构体，未暴露到公共头。要单测 `init_sbt_config`，在 `dmsbtex/test/session_test.c` 中 `#include "../sbt.c"`，使测试 TU 直接获得 `dmsbtex_t` 定义与函数符号；再把临时 `sbt-config.conf` 路径传入 `init_sbt_config` 后断言 `sbt->tls_cfg` 字段。注意 `#include` 方式下 xmake 增量构建可能不感知被包含文件的变更，改 sbt.c 后需 `-r` 强制重建测试目标。

## 关联
- T0366（TLS 证书 P2）：`sbt_tls_config_init` 的 env/ini 解析与 `tls_cert` 层 reload/CRL。
- T0328（0819-dmsbtex-libobk-mtls）：mTLS 握手接入，本模式仅解决“配置来源”而非“握手能力”。
