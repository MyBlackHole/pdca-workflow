# Triage Brief — 0826-oss-https-opt-in

- **category**: enhancement
- **scenario_type**: development
- **summary**: oss 服务端支持通过参数配置开启 HTTPS，默认使用 HTTP
- **current behavior**: 服务启动时无条件构建 TLS 配置并强制 HTTPS 监听；证书缺失/非法/算法不支持时 fail-closed 整体启动失败，没有任何回退 HTTP 的手段
- **desired behavior**: 默认以纯 HTTP 启动；仅当用户显式开启（参数配置）时才启用 HTTPS，且开启后证书校验仍 fail-closed
- **key interfaces**: server 子命令 flag 定义、TLS 配置构建入口、服务监听入口（HTTP vs TLS 监听二选一）、4 层配置模型（CLI > 环境变量 > rdb.conf > 默认值）
- **acceptance criteria**:
  - 运行 `server` 不带任何 TLS 参数，得到明文 HTTP 监听，明文请求返回 200
  - 运行 `server` 带开启 HTTPS 的参数且证书齐备，得到 HTTPS 监听，TLS 握手成功、明文请求被拒
  - 显式开启 HTTPS 但证书缺失/非法时，进程启动失败（保持 fail-closed）
  - 开关解析遵循既有 4 层优先级：显式参数 > 环境变量 > 配置文件 > 默认关闭
  - 既有单元测试与构建脚本全部回归通过
- **out of scope**: 客户端侧 TLS 行为变更、国密/sm2 支持、双端口同时监听（http+https 并存）、mTLS 双向认证
- **information gaps**: 开关的载体形态（新增 CLI bool flag / 复用 rdb.conf tls_enable / 环境变量的取舍）需用户裁决；默认值语义确认
- **dedup results**: out-of-scope 未命中；历史任务 T0368（已归档）实现的是"强制 HTTPS"，与本需求"开关化+默认 HTTP"概念不同，不构成重复；T0259 为其父级遗留 Pending 状态，功能已被 T0368 覆盖
- **recommended next steps**: P1/P2 澄清开关载体与默认值语义 → 合成 PRD（含测试接缝）→ 终审后进入 Do
