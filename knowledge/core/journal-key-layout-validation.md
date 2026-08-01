# Journal btree key 布局校验边界

在独立存储引擎的 journal 恢复中，应在构建 overlay 和 replay 前，对每个
btree key 执行不依赖文件系统 btree-id 的布局校验。对照 bcachefs
`fs/journal/validate.c`：零长度 key 或 key 超出所属 entry 时截断 entry；
非当前 key format 时删除该 key、紧缩后续 key，并以空 entry 填充原尾部。

不要把 bcachefs fs 层的 type/size/snapshot validator 直接施加到拥有独立
btree-id 或 key 合约的引擎。应先证明两侧树类型语义一致；否则该 validator
会把当前引擎的合法记录误判为损坏。Rust 使用精确长度 buffer 时，读取 bkey
header 前还必须验证至少存在 `BKEY_U64S` 个 u64，避免 C 的固定 journal
buffer 隐含提供的访问余量变成越界读取。

来源：T0178，`records/T0178-0801-journal-bkey-validation/conclusion.md`。
