---
name: pdca
description: 显式选择 PDCA 或恢复已有任务时，定位集中资源根和原任务。仅分流，不自动创建任务或执行四阶段。
metadata:
  version: 4.0.0-rc.2
---

# 兼容总入口

实际八个可安装入口位于 [skills](skills/README.md)。安装器只注册 `skills/pdca/SKILL.md` 等八个入口，不重复注册本文件；不把整个资源树放进技能发现目录。

直接读取本文件时，先读 [pdca 总入口](skills/pdca/SKILL.md)，按其根定位和任务绑定执行。这里没有自动新建、阶段授权或业务写权。集中根参见 [USE-PDCA](USE-PDCA.md)。
