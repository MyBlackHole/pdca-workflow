# 跨树复用与共享修订教学

所有对象fixture_only，无生产Agent、授权或发布结果。定义/manifest中的SHA-256由本次生成时实际计算，可复查；符号引用明确标FIX，不当作真实来源。没有为所有节点补完3N套件，因此不是完整业务工作。

## 三个工作视图

[A](works/A.md)与[B](works/B.md)各自Root→{Range,Writer}，引用同一r1字节；[C](works/C.md)明确选择r2。A/B的node、任务与确认不能共用；即使知识库后来提供r2，A/B仍读r1。

[实例参数](works/A-local-delta.md)保存在A自己的目标记录，不改变B与共享定义。增加新的外部行为约束不是参数选择，必须改为local_extension/新契约并重建对应测试。

## 已有定义与候选

[r1](library/versions/range/r1/definition.md)及[manifest](library/versions/range/r1/manifest.md)保存原字节；[r2](library/versions/range/r2/definition.md)及[manifest](library/versions/range/r2/manifest.md)补充编辑性说明。实际语义还依赖[字节术语](library/terms/byte-r1.md)和[固定案例](library/cases/range-s1.md)，故顶层内容不变不代表闭包没有变化。

两个[候选A](candidates/candidate-A.md)、[候选B](candidates/candidate-B.md)同基于r1。A先发布以后B必须检测stale_base；不能因得到写锁就覆盖A。合并后有新payload/manifest/审查/授权，不复制旧许可。

## 演练顺序与返工

先复查所有实际摘要→读取A/B r1→候选A的本地模拟提交→确认A/B输入未变→拒绝候选B旧base→重新三方合并→新manifest与模拟批准→提交→模拟commit完整但head丢失并恢复视图→注入半记录与坏字节，必须拒绝。

局部模拟不是宿主CAS/分布式事务验证。真实执行必须按[EVOLVE-01](../../ontology/concept/ontology-evolution.md)独立审查和真实授权；不能把fixture批准布尔值搬到生产。

详细[U01—U20](../../tests/reuse-regression/README.md)分别说明正反例、错误控制、观测与返工。旧结果永远保留，实际迁移必须有新任务，局部完成不等待全库采用者迁移。
