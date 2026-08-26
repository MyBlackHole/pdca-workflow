# Triage Brief — 0826-tlskeygen-san

- **category**: bug
- **scenario_type**: bugfix
- **summary**: tls-keygen 签发的 host 证书无 Subject Alternative Name，任何严格校验的 TLS 客户端（ossutil/curl/Go 程序）访问对应服务必然证书校验失败
- **current behavior**: tls_keygen.c sign 流程只写 basicConstraints/keyUsage/SKI/AKI 四个扩展；生成的证书 CN 为 UUID 且无 SAN 条目。aio-oss --tls + ossutil 实测报 `x509: cannot validate certificate for 127.0.0.1 because it doesn't contain any IP SANs`
- **desired behavior**: 签发的 host 证书默认携带可用 SAN 集合（DNS localhost 族 + IP 回环），并支持用户自定义 SAN 覆盖；重新生成证书后 ossutil 经正常校验路径访问 aio-oss HTTPS 成功
- **key interfaces**: tls-keygen sign 子命令 CLI 参数、host 证书签发扩展写入逻辑、SAN 扩展格式（RFC 5280 subjectAltName）
- **acceptance criteria**:
  - 运行 tls-keygen sign（不带新参数）生成证书，openssl -text 可见含 DNS 与 IP 的 SAN 扩展
  - 用新证书启动 aio-oss --tls，ossutil 以 https://127.0.0.1 访问不再报 IP SAN 错误
  - 显式传入自定义 SAN 时证书 SAN 与传入一致；未传时用默认集合
  - 既有 mtls/CN 校验行为不回归（既有测试全绿）
- **out of scope**: CA 证书入系统信任库的分发机制（部署侧操作）；sm2 证书链的客户端兼容性验证；ossutil --skip-verify-cert 用法推广
- **information gaps**: SAN 默认集合与 --san 参数形态需用户裁决；CA 不受信为第二层问题需向用户明示（SAN 修复后仍需信任分发或 --ca 配置才能全绿）
- **dedup results**: 任务库与知识库均无 SAN 相关概念记录，不重复
- **recommended next steps**: P2 裁决 SAN 默认集与参数形态 → PRD → 终审后 Do（TDD：tls_keygen 已有测试基建可扩展）
