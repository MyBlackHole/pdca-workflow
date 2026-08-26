# host/server 证书必须携带 SAN（T3973）

## 结论

现代 TLS 客户端（Go crypto/x509、curl、OpenSSL 1.1+、浏览器）按 RFC 6125 **仅以 subjectAltName 匹配 hostname/IP**，CN fallback 已废弃。证书工具签发 host/server 证书若不写 SAN，客户端校验必然失败——与 CA 是否受信无关，先报 SAN 错误。

实测报错形态（ossutil/Go）：`x509: cannot validate certificate for 127.0.0.1 because it doesn't contain any IP SANs`；用域名访问则为 hostname mismatch。IP 访问要求证书含 **IP SAN**（DNS 名不能替代），IPv6 用 `IP:::1` 形式。

## tls-keygen 的修复模式（T3973）

1. **默认回环集**：sign 未传参时写入 `DNS:localhost,IP:127.0.0.1,IP:::1`——保证开箱产物可被校验；回环名仅本机可解析，无攻击面扩大。
2. **--san 显式覆盖**：逗号分隔 OpenSSL nconf 格式（`DNS:x,IP:y`），完全覆盖默认；生产域名/IP 必须显式声明。
3. **fail-fast**：非法条目（缺前缀/空段）在生成前拒绝，不产半成品证书。
4. **inspect 同步展示**：新增证书扩展时，inspect 类自检命令必须同步输出（含 `(none)` + 告警），否则用户无法在部署前发现缺陷——T3973 曾遗漏后被用户反馈补上。

## 校验函数参考

`san_ext_valid`（libs/common.c）：逗号分段，每条须 `DNS:`/`IP:` 前缀（大小写不敏感）且值非空；空串/NULL/空段/裸主机名均拒。注意 `IP:::1` 值本身以冒号开头属合法。

## 关联事实

- 第二层问题：SAN 修复后客户端仍可能报 `unknown authority`——CA 入系统信任库（update-ca-certificates）或按客户端机制指定 CA（Go 支持 `SSL_CERT_FILE` 环境变量）是部署侧操作。
- 已签发的旧证书无法追溯修补，只能重签。

## 适用范围

验证环境 linux x86_64 + OpenSSL4 + Go 1.26（ossutil）；通用结论适用于所有 RFC 6125 客户端。
