# T2044 末切片：影响矩阵 + 7 组件版本递进

> 源：`d3b99ac8` 的 `影响范围` + `版本变更` 章，`file: xmake.lua:1` `file: version.log.in:1` 可重跑

## 影响矩阵（5 模块 × TLS/mTLS 全链路）

| 模块 | TLS 化范围 | 配置收口 | 影响 |
|------|------------|----------|------|
| `libobk` | `sbt` 全链路 TLS | `init_config` + `rdb-config store` | `1.0.0.1`（`+1` 误跳版修正） |
| `dmsbtex` | `network.c` 全链路 | `init_config` | `1.1.0.2` |
| `rpc` | `rpc` 全链路 `安全开关进程上下文` | `init_config` | `3.6.4.20` |
| `fs-backup` | `fsclient` 全链路 | `init_config` | —（随 `rpc`） |
| `oss` | `HTTPS` 开关化 | `init_config` | `1.0.0.1` 首版 |

*Source: `git -C F/139 show HEAD --stat | grep -E "dmsbtex|libobk|rpc|oss"` 可检*

## 7 组件版本递进（相对 `fe9d4364` 一次性）

| 组件 | `fe9d4364` | `d3b99ac8` | 增量 | 说明 |
|------|------------|------------|------|------|
| `libobk` | `1.0.0.0` | `1.0.0.1` | `+1` | 误跳版修正 |
| `rpc` | `3.6.4.19` | `3.6.4.20` | `+1` | |
| `dmsbtex` | `1.1.0.1` | `1.1.0.2` | `+1` | |
| `rdbcomm` | `1.0.1.8` | `1.0.1.9` | `+1` | |
| `tls_keygen` | `1.0.0.0` | `1.0.0.3` | `+3` | 含 `T0451/T0457` |
| `rdb_cfg` | — | `1.0.0.1` | 首版 | 新增 |
| `oss` | — | `1.0.0.1` | 首版 | 集成 |

*验证：`grep -n version xmake.lua | grep -E "rdb_cfg|oss"` 可重跑，`git show HEAD -- xmake.lua` 可溯 `set_configvar` 新增*

## 验证

```bash
grep -q "rdb_cfg_version" xmake.lua && echo "rdb_cfg 可溯"
grep -q "OSS" xmake.lua && echo "oss 可溯"
grep -q "RDB_CFG_VERSION" version.h.in && echo "version.h 可溯"
```

*Source: `file: xmake.lua:1` `file: version.h.in:1` `file: version.log.in:1`*
