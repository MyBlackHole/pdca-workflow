# T0185 AC-3 覆盖差距

AC-3 的正常 insert/overwrite/delete 与 rebuild 路径已有既有 pointer trigger 测试覆盖，且全量
workspace 通过；但本轮尚未增加对持久化 alloc/backpointer 记录进行故意删除、复制或字段修改后
调用 validator 的独立回归测试。因此 AC-3 当前判定为 partial，不宣称任务完成。
