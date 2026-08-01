# T0186 本地 bcachefs 源码对照审计

- `fs/init/recovery.c:68-118`：explicit recovery pass 在主树恢复后运行 allocation、alloc info、
  backpointer 与 extent-to-backpointer 检查；Rust fault phases 绑定 replay、rebuild、publication
  的相同顺序。
- `fs/alloc/backpointers.c:1228-1404`：extent↔backpointer 双向扫描及 mismatch 返回路径；公开
  API 复用 T0185 的只读集合比较，不在失败时隐式修复。
- 现有 Rust `StorageEngine::recover()`：journal replay 后 rebuild，再校验；T0186 仅增加可控
  fault 入口与结构化错误，不改变无 fault 控制流。
