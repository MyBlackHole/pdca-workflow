# T0226 跟进：rpc_recv EOF 判定修复（消除正常关闭误报）

## 背景

T0227（research）已选方案并 POC 实证（ADR-0016）。原计划落地"客户端空闲回收 + EOF 判定"完整方案。
经 grilling（3 轮）确定**范围收缩**：只修 `rpc_recv` 的 EOF 判定，不新增空闲回收、不新增配置项。
理由：
- 服务端已能靠 EOF/read_timeout 回收；客户端业务结束自然 close 即可。
- "空闲主动回收"依赖 idle_timeout 配置项，成本>当前收益，留待后续按需。
- 当前真实问题（T0227 调研发现的 3 条 Error 噪音）仅由 `rpc_recv` 把 EOF 当错误引发。

## 目标

- `rpc_recv`（rpc-io.cpp:25）区分 `nread==0`（EOF/对端正常关闭）与 `nread<0`（网络错误）。
- EOF 返回**负值语义（-101）**区分于网络错误（-100），既有 `< 0`/`< 1` 调用点行为不变。
- EOF 路径**不打 ErrorLog**（或降为 Note/Warning 级），消除"正常关闭误报 bad network"3 条 Error 噪音。
- 半包中断（字节数不符）仍按原错误路径处理，不误归为 EOF。

## 范围

- 仅改 `rpc/rpc-io.cpp`（`rpc_recv`），必要时补充文档注释。
- 不改协议、不新增配置、不改 rpc-conn/rpc-config/rpc-server 逻辑、不改调用点。

## 验收标准

- [ ] AC-1: 对端正常 close（FIN）时，`rpc_recv` 返回 EOF 语义负值（-101），不再打 ErrorLog
- [ ] AC-2: 网络错误（RST/超时等）仍返回原错误值（-100/-200），ErrorLog 行为不变
- [ ] AC-3: 既有所有 `rpc_recv` 调用点（`<0`/`<1` 判定）行为不变，无回归
- [ ] AC-4: 编译通过 + 全量回归通过；POC 场景 02（EOF 判定）作为回归参考

## 备注

- 复用 T0227 的 POC 仓库（POC/scenarios 02）验证 EOF 判定。
- 相关 ADR：ADR-0016；仅采纳其中 EOF 判定部分，空闲回收留待后续任务。
- 半包中断需区分 EOF 与长度不符：EOF 仅在 `bytes==0` 且首个 recv 即 `nread==0` 时判定。
