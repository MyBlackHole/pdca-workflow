# 正式模板记录示例与边界

这里不是新的工作流、adapter或executor。内部105份正式记录直接使用当前templates的schema与字段；没有再用status/value或last_sequence简化为另一套形状。单叶包括三个场景、每场景四条转换、两组请求/响应/消费记录、suite/run/delivery/archive。辅助来源全部写明fixture。

`single-leaf/` 是被检查对象；`expectations.md` 在其外，是维护者固定的合成验收依据。检查调用必须另传basis的SHA-256。候选删除required列表不会改变该依据；其节点集合又与SCENE-01三场景组合核对。生成器同时编写示例和教学规格，所以本例不能证明原目标的语义提取已经正确，更不认证用户批准。

当前建模验收用 `suites/entry.md`，14份本地案例及来源绑定固定ME原oracle/expected/required；Do输出的节点三场景套件另存 `suites/node-*.md`，不会反写当前基线。`real_tool_binding=NOT_RUN` 表示没有取得实际宿主能力，合成run中的pass是测试输入，不是本轮执行了ME语义检查。

`protocol:` 是本示例维护入口的显式只读别名，由调用方绑定到所选协议目录；候选不能重定向它。相对引用从所在文件解析，只允许在subject或明确固定的protocol根内，不跟随任意外部链接。不得把这个教学别名当成某个平台已有adapter。

检查范围：必需文件/字段、身份、摘要、来源案例保护、部分阶段关系、真实图重算、选定清单的显式固定引用闭包。**不覆盖任意正文语义、真实确认消费、权限、时钟、独立Agent、并发发布或完整业务契约。** 所以输出可为structural_relational_result=pass，但production_eligible始终false；真实readiness/freeze/release回执没有生成。

通过独立附件复跑：

```bash
python formal_verify.py --root /path/to/pdca-tree \
  --subject /path/to/pdca-tree/examples/formal-records/single-leaf \
  --basis /path/to/pdca-tree/examples/formal-records/expectations.md \
  --basis-sha256 "$(sha256sum /path/to/pdca-tree/examples/formal-records/expectations.md | cut -d' ' -f1)" \
  --out /path/to/results/formal.json
```

这里现场计算摘要只便于复跑教学材料；实际采用须先取得独立可信的basis摘要，不能相信候选旁边的一份自报校验值。

## v3.4.4 非成功记录与真实开发观察

`lifecycle/`新增10组使用正式模板的有限生命周期fixture；独立basis为`lifecycle-expectations.md`。覆盖派发前阻断、Plan阻断/等待/拒绝、停止在途、已结清终止、隔离保留及有/无冲突后继。它们不是生产执行。正常四边诚实失败由独立维护挑战构造，不复制另一套大规模成功示例。

[生命周期字段/关系](../../ontology/contracts/lifecycle-records.md)与正常完成profile分开；`formal_verify.py`按固定basis显式路由，不依赖候选自选状态。当前会话[语义开发结果](semantic-development/README.md)不是fixture，原始观测和限制分别保留；[真实试点](live-pilot-344-status.md)未冒充完成。
