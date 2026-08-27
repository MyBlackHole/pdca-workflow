# 服务端 mTLS 算法锁 fail-closed（指定算法证书异常即失败）

> 来源：T3988（关联 T3987 证书整体缺失 fail-closed、T3961 算法锁、T0390 双算法尽力收集）

## 适用场景
服务端 mTLS 启用**且显式指定算法**（如 `tls_algorithm=TLS_SM4_GCM_SM3`）时，
该指定算法对应证书缺失/损坏/不支持 → **启动期必须以非 0 退出**，且**不得 fallback 到
另一算法的证书兜底成功**。

## 反模式（根因）
`libs/tls_cert.c:tls_cert_init_server` 原本不感知上层算法配置，恒按 `cert_dir` 自动构建
SM4+AES 双算法链；单算法 `tls_cert_slot_create` 失败仅 `continue` 跳过（T0390"尽力收集、
不连坐其他算法"）。于是"指定 SM4 但 SM4 缺、AES 在"仍整体成功——安全开关被另一算法
静默兜底，等于 **fail-open**。

## 正确范式
服务端证书校验函数须接收**算法选择**参数，并在该参数非空时**仅加载该算法 profile**：
- 指定算法 profile 的 `slot_create` 失败 → 整体失败（`tls_cert_cleanup` + `return`），
  **不跳过、不 fallback**；
- 非法算法名 → 显式 `TLS_CERT_ERR_INVALID_PARAM`（安全开关不变 fail-open）；
- 空算法（未指定）→ 保持双算法链兼容（向后兼容旧行为）。

传递链：`tls_cert_server_options_t.algorithm` ← 各服务端算法配置字段
（rdbcommd `server_boot.opts.algorithm_name`、aio-speedd `g_rpc_config->tls_algorithm`、
dm-ftp `dmsbtex_tls_config_t.algorithm_name`、sbt `libobk_tls_config_t.algorithm_name`）。

## 复用要点
1. 任何"算法锁 + 证书加载"的安全开关，都必须让算法选择**穿透到证书加载层**，
   不能让上层白名单与底层双算法兜底脱节。
2. fail-closed 的判定必须在**底层 slot 创建失败**处，而非上层配置校验处
   （配置合法 ≠ 证书可用）。
3. 引入"指定算法单路径"时，须保留"未指定算法"的双算法兼容分支，避免回归旧部署。

## 测试收敛模式
- `libs/tls_cert_test`：`tls_cert_init_server_alg_failclosed` 构造"仅 SM4"/"仅 AES"临时
  证书目录，验证指定算法缺失→失败、不 fallback、非法名→失败、指定且正常→成功。
- 四服务端：`*_server_boot_tls_test` / `session_test` 加"指定算法 + 该算法证书缺失
  （另一存在）→ prepare 返回非 0"用例（用 `mkdtemp` + 复制单算法证书）。
- 真实证书目录由 `CERT_DIR` env 指定（默认 exe 同目录 `certs`）。
