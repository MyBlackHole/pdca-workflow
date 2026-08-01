# Recovery fault matrix and public derived validation

在 journal replay → derived rebuild → publication 的 recovery 顺序中，派生状态校验必须保持
只读，并可通过公开 API 独立调用。fault 注入应绑定三个边界：replay 后、rebuild 阶段、publication
前；任一 fault 都不得返回成功恢复对象。结构化 mismatch 至少区分 invalid pointer、generation、
duplicate backpointer、alloc set 和 backpointer set，便于测试和上层诊断。
