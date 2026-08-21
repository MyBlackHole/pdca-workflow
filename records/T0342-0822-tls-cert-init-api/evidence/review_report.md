# 代码审查报告 — T0342 tls_cert 初始化 API 完善

## 审查范围
- libs/common.h: 统一证书路径常量（新增 ED25519 前缀）
- libs/tls_cert.{h,c}: 精简 options 强制 cert_dir，ED25519 双格式回退，ca_cn 校验，LOAD_CERT/LOAD_KEY 拆分
- libs/tls_keygen.c: 路径统一复用 common.h
- libs/tests/tls_cert_test.c: 新增 6 用例（AC-1/2/3/4/7）
- rpc/*, rdbcomm/*, dmsbtex/*, libobk/*: 调用点收敛为 cert_dir 唯一路径

## 标准轴
- 编码标准：无新增 getenv，无 rwlock，无硬编码 "%s_host.key"（已消除），头文件仅暴露必要常量
- 安全：ca_cn 校验仅 [A-Za-z0-9._-]，防路径遍历；双格式回退优先有前缀，无则回退，避免旧集群中断
- Fowler 坏味：消除重复分支（rpc-io 双分支收敛为单路径），消除栈局部拷贝（改直用 g_rpc_config），函数长度适中

## 规范轴（对照 prd.md 8 AC）
- AC-1 build_server_profiles: 新前缀优先，count==2，算法固定，非法返回 INVALID_PARAM — 通过
- AC-2 build_client_profile: algorithm 区分 ca，ca_cn 必填+非法字符校验 — 通过
- AC-3 init_server: cert_dir 必填，双 SSL_CTX 非空互异，缺失 LOAD_* 不降级 — 通过
- AC-4 init_client: cert_dir+algorithm+ca_cn 必填，非法 INVALID_PARAM，旧 profiles 已移除 — 通过
- AC-5 静态：grep profiles in tls_cert.h 仅内部辅助，grep hardcode 0，grep getenv 0 — 通过
- AC-6 回归：tls_cert_test 8 用例全绿，rpc_handshake_test 已同步为 cert_dir（1处历史行残留仅内部辅助）
- AC-7 双格式：old/new 临时目录双测均 TLS_CERT_OK — 通过
- AC-8 路径统一：grep CERT_FILE_ED25519 in common.h 非空，grep hardcode in tls_keygen 0 — 通过

## 风险评级：低
- Breaking 已量化（9 处调用点已收敛），回退路径明确（fallback to ca.crt/host.crt/server.crt）

## 建议
- 后续可抽 tls_paths.h 独立，但当前 common.h 已满足统一
