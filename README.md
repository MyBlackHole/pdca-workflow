# PDCA Tree · Markdown-native

<!-- pdca:current-release:start -->
当前维护快照 **3.4.10** · [协议清单](protocol-release.md) · [变更](migration/v3.4.10-CHANGES.md) · [迁移](migration/v3.4.10-MIGRATION.md) · [验证范围](migration/v3.4.10-VALIDATION.md)
<!-- pdca:current-release:end -->

主包保持纯 Markdown：三个场景、每节点完整 PDCA、真实新 Agent、Plan/Check 两处确认、平台中立、无 adapter。当前版本是维护快照，不表示宿主执行或发布资格已获证明。

## 开始使用

支持标准技能发现的宿主从 [SKILL.md](SKILL.md)进入；已安装全局规则的宿主从 [global-entry](bootstrap/global-entry.md)进入。二者交接到同一个 [USE-PDCA](USE-PDCA.md)和[入口检查](bootstrap/entry-check.md)，不重复启动任务。

先固定真实 TARGET_ROOT、PDCA_ROOT 与协议快照，再按[角色与事件](bootstrap/entry-check.md#role-actions)行动。新工作目标是入口 cwd；恢复不换根、不重建身份。协议资料留在获权 PDCA records，业务源码留在获权目标目录。

## 维护与验证

[模板](templates/README.md) · [验证入口](tests/README.md) · [按需规则](ontology/LOAD-MAP.md) · [知识索引](ontology/INDEX.md)。本轮验证程序随独立验证包交付，不成为日常运行依赖；完整分发包把源码、验证器、固定原输入与结果一起绑定。

静态检查、检查器自测、实际宿主行为与效果对照分别报告。原真实 records 不回写，不因格式或导出缺项被改称模拟；旧 PASS 不自动继承到新版本。

## 历史

[3.4.7 变更](migration/v3.4.7-CHANGES.md) · [3.4.6 变更](migration/v3.4.6-CHANGES.md) · [3.4.4 验证](migration/v3.4.4-VALIDATION.md) · [派发扩展](migration/agent-dispatch.1-CHANGES.md)。这些说明只适用于其固定版本，不能代替上方当前验证入口。旧任务按原快照接续。
