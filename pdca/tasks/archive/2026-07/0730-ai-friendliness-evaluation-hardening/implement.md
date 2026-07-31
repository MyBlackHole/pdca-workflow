# T0160 实施切片

## 切片 1：路由合约与 resolver

- 先写 schema、合法/非法 contract 和 resolver CLI 的失败测试。
- 实现稳定映射、错误码与文档锚点一致性检查。
- 用保持 Markdown 标题但交换 contract 映射的反例替换旧标题搜索夹具。

## 切片 2：真实故障与生命周期 fixture

- 建立最小临时严格仓库和公共转换调用封装。
- 先实现完整成功路径，再逐个注入 Plan→Do、Do→Check、Check→Act、Act→archive 的关键缺失项。
- 删除所有直接返回预期错误码的 fixture 分支；断链必须由实际引用检查产生。

## 切片 3：内容 baseline 与预算检查

- 为当前审计范围生成初始 baseline，添加严格 schema 和 budget 检查模式。
- 先覆盖未知/遗漏/超预算/无理由更新，再覆盖等于/降低和有理由更新。
- 将相关 deterministic fixture、引用完整性作为预算更新的验证条件。

## 切片 4：集成评测与审查

- 统一 fixture 输出为稳定 JSON，保留 context bytes 但明确其仅为代理。
- 执行完整 unittest、AI 友好夹具、内容审计、workflow/doctor、双轴代码审查。
- 登记 schema、测试、结果和审查证据，生成 convergence map 后进入 Check。
