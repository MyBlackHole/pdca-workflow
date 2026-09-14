---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.1
authority: reference
status: active
---

# 项目绑定契约 v4

规则根PDCA_ROOT与项目根TARGET_ROOT分离；项目数据根默认TARGET_ROOT/.pdca。非空环境变量只定位，不自动启用。项目已绑定时沿用固定根／协议快照，不依据后来cwd改绑。

项目context固定project/workspace身份、真实路径、规则ref/digest与数据位置；Git共享元数据不当任务私有区。业务写域、记录写域与引用基准明确；任务之间、项目之间不串用。

新工作先明确初始化权限；保留已有文件和用户修改，不覆盖旧context或默迁records。已有3.x任务按原路径与协议继续，迁移需用户操作及新的身份／引用。

持久入口只提醒恢复原记录；实际加载能力由宿主验证。详见USE-PDCA与RECOVERY。
