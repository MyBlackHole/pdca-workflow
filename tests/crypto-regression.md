# 密码本体修复回归：K-01—K-04

固定输入见[向量](fixtures/crypto-vectors.md)，外部来源见[sources](sources.md)。这些是测试设计；实际结果另存验证报告。算法说明使用固定标准版本，不冒充最新合规建议；示例密钥绝不能用于生产。

## 公共执行合同

被测对象为采用当前本体构造的候选实现，以及独立密码库控制。记录实现/本体/fixture摘要、库与运行时版本。先跑正确控制验证夹具；逐字节比较ciphertext与tag，再解密对比原plaintext。仅roundtrip不足，因为同错加解密可以相互抵消。坏变体在隔离副本中运行；失败断言=killed，构建/环境错误=invalid。不能让Agent从actual重写预期。

## GCM

正例：GCM-EMPTY、GCM-BLOCK、GCM-AAD-PARTIAL、GCM-IV8全部匹配；覆盖空输入、整块、AAD和非整块、非96位IV。

负控制GCM-WRONG-MASK：只把E_K(J0)换成E_K(0)，EMPTY必须输出与固定tag不符，即使文本仍含GHASH/CTR/不可重用。此例证明关键词pass不代表公式通过。

篡改反例：分别修改一字节tag、AAD、密文和IV，保持其余输入不变。正确解密必须拒绝认证，不释放未经验证的结果；异常类型按真实绑定固定，捕获InvalidTag是本测试通过，其他环境异常不是。空明文用非空向量测密文修改。

返工：先保存错误mask结果，修H/J0的定义与依赖节点，升本体及套件版本；全向量回归和四类篡改测试，不能只验证EMPTY。未测试的标签长度/算法实例仍需任务自己的套件。

## CCM

正例：CCM-RFC1的8字节tag完全匹配；另以固定key/nonce和公开格式分别执行0/1/15/16/17字节消息、空与非空AAD、4/8/16字节tag的库/独立模型对照。这些边界对照不是另一个RFC已知答案向量，结果分类分开。

负控制CCM-PKCS7：同RFC1中只把必要补零换成PKCS7，应与原tag不符；M/L非法组合拒绝而不是自动改值。CCM-MISSING-S0省略S0掩码也必须失败。AAD/密文/tag任一改动的解密拒绝认证。

返工：对齐B0、AAD长度、零补齐和S0，不把CBC应用层填充混进CCM。保留旧tag失败，重跑RFC1及边界/无效参数。涉及长AAD长度编码的实现须另外增加长度边界，不能由小样本声明全覆盖。

## XTS

正例：XTS-TWO-BLOCKS与XTS-TAIL34完全匹配且可解密；相同key/tweak/plaintext重复执行必须相同。公开向量同时覆盖块推进和尾部stealing，roundtrip/确定性不能单独证明兼容。

负控制XTS-PER-BLOCK-ENCRYPT：把每块tweak错误写成E_K2(i+j)，两个整块向量第二块断言必须失败。不要把“固定输入重复得到同密文”本身当作缺陷。XTS无tag，因此不得构造“XTS篡改自动认证失败”这一错误预期。

返工：重建初始tweak与GF推进、完整分组和尾块处理，升案例版本；正确控制和错误tweak变体分别验证。不得外推到未经验证的SM4-XTS私有格式。

## fscrypt/CFB 身份审查

对Linux v6.12文档明确列出的文件名CBC-CTS模式作source-level核对，错误样本把CFB写成CBC-CTS同义词必须拒绝。该源文档核对不等于实际文件系统互通测试；具体部署需绑定内核/策略/工具并在授权测试目录完成正反例。
