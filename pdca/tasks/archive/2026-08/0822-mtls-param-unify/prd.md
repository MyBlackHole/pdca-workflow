# T0361 — mtls 参数三态精简与 sec_resolve_bool 统一配置解析

## 问题陈述

- **现状**（用户意见 + 代码核实）：
  1. 四个工具的 `cli_mtls_set`+`cli_mtls_enabled` 成对字段冗余（rdbcomm-main.c:125-126、rdbcommd-main.c:85-86、rpc-config.h:22-23、rpc.h:88-89），用两个变量区分"未设置/显式 0"；
  2. dmsbtex/libobk 的 mtls 开关只读环境变量（T0358 的 parse_bool_env），不支持 ini 配置文件，与其余工具的 sec_resolve 分层不一致。
- **目标**: 单一三态字段表达 CLI 意图；新增 `sec_resolve_bool` 统一布尔安全开关解析（env/ini 分层、严格 0/1、非法 fail-closed）；dmsbtex/libobk 接入配置文件。

## 解决方案

1. **新增 `sec_resolve_bool(tool_section, tool_key, global_section, global_key, env_name, default_val)`**（libs/rdb-config）：分层同 sec_resolve_int，但每层取原始串严格校验仅 "0"/"1"；任一层非法返回 **-1 错误哨兵**；调用方报错退出。通用 `sec_resolve_int` 不动（避免波及非布尔调用方）。
2. **六处字段合并**：删 `cli_mtls_set`，`cli_mtls_enabled` 语义改为三态 `-1=未设置 / 0 / 1`；消费点 `if (cli_mtls_enabled >= 0)` 覆盖。
   - rdbcomm-main.c、rdbcommd-main.c、rpc-config.h(g_rpc_config)、rpc.h(g_rpc_args)、rpc/main.cpp、rpc-client.cpp
3. **mtls_enabled 解析统一换 sec_resolve_bool**：
   - rdbcomm/rdbcommd/aio-speed/aio-speedd：sec_resolve_int → sec_resolve_bool，==-1 报错退出
   - dmsbtex/libobk：删除 T0358 的 dm_parse_bool_env/sbt_parse_bool_env，改 sec_resolve_bool(NULL,NULL,SEC_GLOBAL_SECTION,SEC_GLOBAL_TLS_KEY,SBT_*_MTLS_ENABLE,0)——获得 ini `[security] mtls_enable=1` 支持
4. CLI getopt 校验逻辑保留（strtol 全串 0/1）。

### 声明的测试接缝
- seam: libs/tests/*（新增 sec_resolve_bool 单测） -> libs/rdb-config.c
- seam: dmsbtex/test/session_test.c -> dmsbtex/network.c
- seam: libobk/test/session_test.c -> libobk/lib/sbt/libobk.c

## 验收标准

- [ ] AC-1: 六处工具结构体仅剩单一 `cli_mtls_enabled` 三态字段（grep 无 cli_mtls_set 残留）
- [ ] AC-2: sec_resolve_bool 单元覆盖——env 合法/非法/未设置、ini 层合法/非法、默认值；非法返回 -1
- [ ] AC-3: 四工具 + dmsbtex/libobk 端到端：ini 配置生效、CLI 覆盖 ini、env 覆盖 ini、非法值拒绝启动（exit≠0）
- [ ] AC-4: 六套既有测试回归 PASS

## 范围外

- 不修改通用 sec_resolve_int / config_get_int 行为
- 不涉及协商协议与白名单（T0357）

## 备注

用户意见原话：(1) cli_mtls_set/cli_mtls_enabled 应留一个；(2) 每个工具 mtls_enabled 都应 sec_resolve 支持配置文件获取、CLI 参数覆盖。
