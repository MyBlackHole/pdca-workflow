# T2044 Do 首切片：业务 50 files 的 4 提交并集溯源（修正后）

> 源：`git show d3b99ac8 --stat | grep -v third_party/openssl4` + `git log fe9d4364..d3b99ac8`

## 4 提交并集（业务 50 files，`third_party/openssl4` 的 `4183-50=4133` 为噪音已滤）

| 集合 | 来源 | 核心变更 | 文件 |
|------|------|----------|------|
| `F-139` 原量 | `dmsbtex/libobk/rpc/fs-backup/oss` 全链路 TLS 化 | `init_config` 收口 + `mTLS fail-closed` | `dmsbtex/*` `libobk/*` `rpc/*` `fs-backup/*` `oss/*` `libs/rdb-config.*` |
| `T0451` | `EVP_PKEY_free` 时序 + 序列号硬编码 2 | `UAF` 修复 | `libs/tls_keygen.c` |
| `T0457` | `random()→RAND_bytes` + `UB` + `sys/stat.h` 去重 | 熵/UB 收口 | `libs/tls_keygen.c` `libs/rdb-config.h` |
| `T0458` | `allowed_values` 3 类约束展示 | 模板自解释 | `libs/rdb-config.h` `rdb-cfg/cli.c` |

## 验证（业务 50 files 可检）

```bash
git -C /home/black/Public/aio/aio-tools/6200/F/139 show --stat HEAD | grep -v third_party/openssl4 | wc -l  # 50
git -C /home/black/Public/aio/aio-tools/6200/F/139 show --stat HEAD | grep -v third_party/openssl4 | grep -q "tls_keygen.c" && echo "UAF 可溯"
grep -q "allowed_values" /home/black/Public/aio/aio-tools/6200/F/139/libs/rdb-config.h && echo "模板可溯"
```

*Source: `git -C F/139 show --stat HEAD:4183 files` 滤 `third_party` 后 `50 files` + `file: libs/tls_keygen.c:EVP_PKEY_free` + `file: libs/rdb-config.h:allowed_values`*

## 三线各 1 mermaid（注记：`TLS` 的 `2 子图` 合为 `1` 综合图）

- **TLS 全栈**：`init_config` 收口（`5 模块`）+ `mTLS fail-closed` **合一** 图（`T2034` 人审 `Q2` 修正）
- **签发加固**：`RAND_bytes` 回退 `clock_gettime^pid^&serial` 单图
- **模板自解释**：`allowed_values/[min,max]/最大长度` 3 类约束 `通用展示` 单图
