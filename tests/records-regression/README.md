# 从原始运行材料核验，不用facts自报通过

本目录把v3.4审查中的错误模式构造成固定原文/文件样本，case的expected与subject分开。subjects含实际request、response、suite、run、artifact、manifest、issue等文件及真实字节摘要；合成身份与事件不是生产事实。

## 使用与证据边界

读取[suite](suite.md)定位案例，按[CASE-01](../../ontology/concept/task-test-case.md)完成当前node/scene的本地适用绑定。检查方法只读取该例subject与显式引用；外层比较expected。原文、字节、引用和有限中文句式检查可以复跑，但不能证明通用自然语言判断、真实用户批准或新Agent隔离。

外部维护附件的verify.py提供这组确定性参考检查；不是工作流执行器，不写records、不生成批准、不访问网络。真实宿主/Agent结果保持NOT_RUN。旧结构facts套件保留原样，作用域不升级。

## 覆盖

确认与控制、基线及复合快照、终态/全场景图、已知阻断issue、CP_SHARE/CP_RECURSE语义覆盖、变体注入命中、答案边界、原始证据和失败历史、异常接续、回归增补、父组合版本、累计预算、额外实际依赖、否定/引用误报、活动版本冲突、结果分类、来源case绑定及原目标覆盖。

所有正反例都保留；负例被准确拒绝是检查器案例pass，不自动称mutation killed。外部报告单列故意错误检查器的实际表现、异常与限制，不把解析失败算成功击杀。

## 案例索引

| 案例 | 方法 | 输入 |
|---|---|---|
| [F001](cases/F001.md) | gate | [subject](subjects/S001/input.md) |
| [F002](cases/F002.md) | gate | [subject](subjects/S002/input.md) |
| [F003](cases/F003.md) | gate | [subject](subjects/S003/input.md) |
| [F004](cases/F004.md) | gate | [subject](subjects/S004/input.md) |
| [F005](cases/F005.md) | gate | [subject](subjects/S005/input.md) |
| [F006](cases/F006.md) | gate | [subject](subjects/S006/input.md) |
| [F007](cases/F007.md) | gate | [subject](subjects/S007/input.md) |
| [F008](cases/F008.md) | gate | [subject](subjects/S008/input.md) |
| [F009](cases/F009.md) | gate | [subject](subjects/S009/input.md) |
| [F010](cases/F010.md) | gate | [subject](subjects/S010/input.md) |
| [F011](cases/F011.md) | gate | [subject](subjects/S011/input.md) |
| [F012](cases/F012.md) | gate | [subject](subjects/S012/input.md) |
| [F013](cases/F013.md) | snapshot | [subject](subjects/S013/input.md) |
| [F014](cases/F014.md) | snapshot | [subject](subjects/S014/input.md) |
| [F015](cases/F015.md) | snapshot | [subject](subjects/S015/input.md) |
| [F016](cases/F016.md) | snapshot | [subject](subjects/S016/input.md) |
| [F017](cases/F017.md) | tree | [subject](subjects/S017/input.md) |
| [F018](cases/F018.md) | tree | [subject](subjects/S018/input.md) |
| [F019](cases/F019.md) | tree | [subject](subjects/S019/input.md) |
| [F020](cases/F020.md) | tree | [subject](subjects/S020/input.md) |
| [F021](cases/F021.md) | tree | [subject](subjects/S021/input.md) |
| [F022](cases/F022.md) | tree | [subject](subjects/S022/input.md) |
| [F023](cases/F023.md) | tree | [subject](subjects/S023/input.md) |
| [F024](cases/F024.md) | tree | [subject](subjects/S024/input.md) |
| [F025](cases/F025.md) | coverage | [subject](subjects/S025/input.md) |
| [F026](cases/F026.md) | coverage | [subject](subjects/S026/input.md) |
| [F027](cases/F027.md) | coverage | [subject](subjects/S027/input.md) |
| [F028](cases/F028.md) | injection | [subject](subjects/S028/input.md) |
| [F029](cases/F029.md) | injection | [subject](subjects/S029/input.md) |
| [F030](cases/F030.md) | injection | [subject](subjects/S030/input.md) |
| [F031](cases/F031.md) | injection | [subject](subjects/S031/input.md) |
| [F032](cases/F032.md) | injection | [subject](subjects/S032/input.md) |
| [F033](cases/F033.md) | visibility | [subject](subjects/S033/input.md) |
| [F034](cases/F034.md) | visibility | [subject](subjects/S034/input.md) |
| [F035](cases/F035.md) | visibility | [subject](subjects/S035/input.md) |
| [F036](cases/F036.md) | evidence | [subject](subjects/S036/input.md) |
| [F037](cases/F037.md) | evidence | [subject](subjects/S037/input.md) |
| [F038](cases/F038.md) | evidence | [subject](subjects/S038/input.md) |
| [F039](cases/F039.md) | evidence | [subject](subjects/S039/input.md) |
| [F040](cases/F040.md) | takeover | [subject](subjects/S040/input.md) |
| [F041](cases/F041.md) | takeover | [subject](subjects/S041/input.md) |
| [F042](cases/F042.md) | takeover | [subject](subjects/S042/input.md) |
| [F043](cases/F043.md) | takeover | [subject](subjects/S043/input.md) |
| [F044](cases/F044.md) | extension | [subject](subjects/S044/input.md) |
| [F045](cases/F045.md) | extension | [subject](subjects/S045/input.md) |
| [F046](cases/F046.md) | extension | [subject](subjects/S046/input.md) |
| [F047](cases/F047.md) | release | [subject](subjects/S047/input.md) |
| [F048](cases/F048.md) | release | [subject](subjects/S048/input.md) |
| [F049](cases/F049.md) | budget | [subject](subjects/S049/input.md) |
| [F050](cases/F050.md) | budget | [subject](subjects/S050/input.md) |
| [F051](cases/F051.md) | budget | [subject](subjects/S051/input.md) |
| [F052](cases/F052.md) | budget | [subject](subjects/S052/input.md) |
| [F053](cases/F053.md) | dependency | [subject](subjects/S053/input.md) |
| [F054](cases/F054.md) | dependency | [subject](subjects/S054/input.md) |
| [F055](cases/F055.md) | assertion | [subject](subjects/S055/input.md) |
| [F056](cases/F056.md) | assertion | [subject](subjects/S056/input.md) |
| [F057](cases/F057.md) | assertion | [subject](subjects/S057/input.md) |
| [F058](cases/F058.md) | rule-conflict | [subject](subjects/S058/input.md) |
| [F059](cases/F059.md) | rule-conflict | [subject](subjects/S059/input.md) |
| [F060](cases/F060.md) | rule-conflict | [subject](subjects/S060/input.md) |
| [F061](cases/F061.md) | classification | [subject](subjects/S061/input.md) |
| [F062](cases/F062.md) | classification | [subject](subjects/S062/input.md) |
| [F063](cases/F063.md) | classification | [subject](subjects/S063/input.md) |
| [F064](cases/F064.md) | binding | [subject](subjects/S064/input.md) |
| [F065](cases/F065.md) | binding | [subject](subjects/S065/input.md) |
| [F066](cases/F066.md) | binding | [subject](subjects/S066/input.md) |
| [F067](cases/F067.md) | scope | [subject](subjects/S067/input.md) |
| [F068](cases/F068.md) | scope | [subject](subjects/S068/input.md) |
| [F069](cases/F069.md) | chain | [subject](subjects/S069/input.md) |
| [F070](cases/F070.md) | chain | [subject](subjects/S070/input.md) |
| [F071](cases/F071.md) | chain | [subject](subjects/S071/input.md) |
| [F072](cases/F072.md) | chain | [subject](subjects/S072/input.md) |
