# 内容采用与修复审查

逐问题验收位于[audit-regression](audit-regression/K-01.md)，密码向量见[crypto-regression](crypto-regression.md)。每次实际采用前按ONTOLOGY-01记录具体claim、版本、scope、source/semantic/behavior等级与证据，不能仅因status=active或链接可打开就通过。

## 固定OpenZFS 2.3.0源审查矩阵

| 场景 | 必须核对 | 错误样本 |
|---|---|---|
| 普通去重命中 | zio_ddt_write路径中的校验/引用与读回语义，不凭文字把数据变hole | dedup命中强制brt_add(hole) |
| 非dedup显式块克隆 | brt_pending_apply处理pending计数与实际BRT引用 | 把BRT描述成空洞表 |
| dedup块克隆，DDT成功吸收全部pending refs | 逐项ddt_addref成功并消费余数；没有remaining才跳过BRT | 无条件对每个dedup克隆新增BRT |
| dedup块克隆，DDT无法吸收全部pending refs | 代码中break后的remaining走后续BRT路径 | “dedup块克隆永远不会进入BRT”的过强断言 |
| ddt_enter | 函数签名和mutex_enter(&ddt->ddt_lock)调用 | 将其当新增条目API |

源代码核对只能支持对应源码主张，不证明真实数据池功能。真实测试必须绑定测试池、特性、构建、相同输入、前后计数和读回，避免破坏生产池；没有此环境时保持NOT_RUN。计数更新可能发生在同步阶段，不能随意用一次瞬时快照声称不变量失效。

## 隔离节点解除条件

bcachefs-btree-bset、sm4-zfs-encryption和NBU资料保持稳定ID但禁止采用。阅读它们进行补证/修正文档是允许的；将未核验主张作为必需实现约束或oracle是不允许的。解除需独立材料、匹配版本、正反例、审查记录、发布修订；本次不根据“已改成谨慎语气”自动解除。

## 分类负控制

已知正确：KnowledgeArtifact individual通过instance_of引用knowledge-artifact类；与task为relates_to。
已知错误：领域加密主题以specializes继承pdca-task。类型方向形式合法不能替代语义审查。

## 证据层级负控制

给错误GCM公式保留GHASH/CTR等关键词：结构检查仍可通过，固定向量必须失败。unverified或unclassified不能自动采用；source_checked_scoped仅覆盖checked_claims列出的主张且需与当前任务版本相符。字段填写不是实际验证结果。
