# GMSSL 替代 OpenSSL 可行性 PoC 结论

## 环境

| 项 | 值 |
|---|-----|
| GMSSL 版本 | v3.1.1（xmake-repo） |
| 构建方式 | xmake package gmssl（CMake 默认选项 `-DBUILD_TESTING=OFF`） |
| OpenSSL 版本 | 3.6.3 |
| 测试主机 | Linux x86_64 |

## 测试分组

| # | 测试项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | SM2 密钥生成 + PEM 导出 | ✅ | |
| 2 | X.509 CA 自签名 + PEM + 自验 | ✅ | |
| 3 | CA → 服务端证书 + 验签 + 提取 Subject | ✅ | |
| 4 | SM4-GCM 加解密 + 篡改检测 | ✅ | |
| 5 | TLS/TLCP 协议常量 | ✅ | |
| 6 | TLS13/TLCP 上下文创建 | ✅ | |
| 7 | tls-keygen Ed25519 证书 → GMSSL 加载 | ✅ 加载；❌ 解析 | GMSSL 不支持 Ed25519 OID（预期） |
| 8 | GMSSL SM2 证书 → OpenSSL 验签 | ✅ | **双向兼容** |
| 9 | OpenSSL SM2 证书 → GMSSL 验签 | ❌ | 公钥解析正常（`x509_cert_get_subject_public_key=1`），但 `sm2_do_verify` 签名验证失败 |
| 10 | tls-keygen Ed25519 链 OpenSSL 自验 | ✅ | 工具修复：`sign` 需显式传 `--ca-cert`/`--ca-key` |

## 关键发现

### GMSSL 功能完整性
- ✅ SM2 密钥生成、签名、验签
- ✅ X.509 证书链（CA → Server）签名与验证
- ✅ PEM/DER 格式导出
- ✅ SM4-GCM 加解密
- ✅ TLS13/TLCP 上下文

### 已知限制
1. **Ed25519 完全不支持**（GMSSL 为 GM 标准库，不含 Ed25519 实现）
2. **OpenSSL SM2 证书互操作问题**：GMSSL 可解析 OpenSSL SM2 证书的 TBS 和公钥，但 `sm2_do_verify` 签名验证失败（SM2 签名/哈希计算差异）
3. **GMSSL SM2 证书可被 OpenSSL 验证**：双向兼容单向可用

### 使用注意事项
- `x509_cert_sign_to_der` 不自动分配输出内存，需两段式调用：`NULL` 算长度 → `malloc` → 写入
- `x509_name_set` 参数顺序：`country, state, locality, org, org_unit, common_name`
- `x509_cert_check` 需要 `basicConstraints` 扩展（CA 证书）

## 替换结论

**不能直接 find/replace 替换 OpenSSL。** 存量证书兼容问题：

| 存量证书类型 | 来源 | GMSSL 兼容性 |
|-------------|------|-------------|
| Ed25519（tls-keygen） | 现有生产工具签发 | ❌ 无法解析/验签 |
| SM2（OpenSSL 签发） | 外部/历史证书 | ❌ 无法验签 |
| SM2（GMSSL 签发） | 新签发 | ✅ |

**建议方案：双后端设计**
- 旧证书（Ed25519 / OpenSSL SM2）继续用 OpenSSL 维护
- 新证书统一用 GMSSL 签发 SM2
- 运行时根据证书签名算法 OID 自动选择后端验签
