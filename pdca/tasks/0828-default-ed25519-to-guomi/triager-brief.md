# Triage Brief — default-ed25519-to-guomi

- **category**: enhancement
- **scenario_type**: development
- **summary**: 将代码库多处默认密钥/证书算法由 ed25519 改为国密
- **current behavior**: 证书生成、证书路径选择、Go OSS HTTPS 配置等多处默认算法为 ed25519，证书默认文件名前缀为 ed25519_*
- **desired behavior**: 上述默认位置改为国密算法（证书/签名层默认 sm2，相应文件名前缀 sm2_*）；范围与 Go 侧处理方式依 Grill 决策
- **key interfaces**: 证书生成工具的算法参数默认值、证书路径解析的默认前缀常量、OSS HTTPS 的算法/前缀默认配置、握手套件默认选择
- **acceptance criteria**:
  - 运行证书生成工具不带算法参数时，默认生成国密（sm2）证书并以 sm2_ 前缀命名
  - 运行 OSS HTTPS（依范围决策）默认解析到国密证书前缀，且行为可预期（启动或明确 fail-closed）
  - 既有测试用例中关于默认算法/默认前缀的断言与新默认一致
  - 运行全量相关测试套件得到全部通过
- **out of scope**: 不改变握手默认枚举的运行时数值（保持二进制兼容）；不改变 SM2 算法实现本身；不改变 `HS_ALG_DEFAULT` 值
- **information gaps**: 改动范围、国密具体算法（sm2 / SM4-GCM-SM3）、Go 侧 SM2 证书加载不支持的处理、默认文件名前缀是否变更
- **dedup results**: 未在 tasks/records/out-of-scope 命中相似概念（out-of-scope 检查 default-algorithm-to-guomi / ed25519-sm2 均无匹配）
- **recommended next steps**: 进入 P2 Grill，向用户澄清改动范围与国密算法定义后合成完整 PRD
