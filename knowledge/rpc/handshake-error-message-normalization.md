# 协议错误码报错信息归一模式（T3956）

## 模式

多模块共享同一套协议错误码时，"码→可读文案"必须单一来源，禁止客户端各自打印裸十六进制：

1. **libs/common.h 唯一定义 + 模块兼容别名宏**（复刻 T0359 算法名归一模式）：
   - 真实定义唯一（如 `HS_ERR_MTLS_REQUIRED 0x8004`），四套前缀别名（`RDB_HS_ERR_*`/`OBK_HS_ERR_*`/`DM_HS_ERR_*`）指向它
   - 运行时值严格不变；各模块头文件删除重复 enum/define 改为引用
   - 注意 enum→宏迁移时的编译冲突：先在 common.h 落定义再删各头文件 enum，否则宏展开进 enum 报 `expected identifier before numeric constant`
2. **文案函数与码表同置**：`hs_err_str()` 与算法名映射同放 libs 单一实现文件；已知码返回静态字面量，未知码走 `_Thread_local` 缓冲并携带原始码（诊断不丢失）
3. **接入点全覆盖检查**：客户端有两类消费路径——主动握手失败路径 + 业务响应循环中的握手帧防御分支（0822 类任务产物），两处都要接文案函数；用 `grep "result=0x\|%x"` 扫残留

## 关联陷阱

- **shell 退出码仅低 8 位**：`-(int)0x8004=-32772` 截断为 252（随机语义）。语义化退出码必须选稳定小值（本例 -2→254）并在头文件注释文档化；原始错误码保留在日志而非退出码。
- **静默失败扫描**：rdbcomm/dmsbtex 客户端拒绝时 `fail=1; goto error;` 无任何日志——报错类 bug 排查时应 grep `fail = 1` / `goto error` 分支确认有 ErrorLog。
- **FAILURE 帧不带原因码**的协议下，客户端只能做情境化提示（"server may require mTLS..."），措辞须保留不确定性。

## 验证锚

e2e 场景矩阵断言三要素：退出码精确值 + stderr 关键短语 + 反向断言（不含裸 `result=0x`、业务输出未执行）。参考 `test/e2e_tool_scenarios.sh` S4/S17。
