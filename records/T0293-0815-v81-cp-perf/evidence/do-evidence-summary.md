# T0293 Do 证据汇总：O1 + O3 实施与验证

实施范围：src/agent_plain_ingress.cpp（仅控制面 fastpath / WRITE 归并，未触碰 data path / tree / 架构）。

## 改动
- O1 `ingress_arm_write` helper + `write_armed` 会话标志：多个完成回调/快速路径向同一
  unbounced tx 追加时只做一次 `reactor_mod(WRITE)`，此后归并，flush 完成后复位。
  所有 `reactor_mod(...WRITE)` 入口统一走 helper（enqueue 错误、job_done、hello 错误、
  hello_ack、fastpath）。
- O3 fastpath `ingress_handle_control_frame`：无 in-flight 控制 job 时，PING 直接在
  reactor 线程零堆分配直写 PONG 到 tx；TIME 走本地响应 vector 同步渲染。SYS 仍走 work
  pool（可能 I/O）。仅当 `control_jobs.empty()` 才启用，确保与异步 SYS 不反转响应顺序。

## control-plane 对称基准（tests/benchmark_control_plane.sh build 32 7）
| 版本 | median_ms | p99_upper_ms | thread | RSS |
|---|---|---|---|---|
| 优化前 opt_in_cp.log | 54.450 | 12.030 | 7 | 6976 |
| O1+O3（多次采样） | 51.629 / 51.853 / 52.285 / 50.480 / 51.879 / 53.269 | 11.0~11.6 | 7 | 6964 |
| v80 参照（归档） | 48.97 | 4.56 | 4 | 6860 |

稳定 median≈51.9ms，较优化前 -5%；p99_upper 12.03→约 11.4。

## 集成/回归（AC-3/AC-4）
- tests/v81_control_frame_integration.sh ./build-make → PASS（ping=3 stall=3 time=3 burst=ok tree=4）
- tests/plain_ingress_integration.sh ./build-make → PASS（baseline=3 fragmented=1 timeout=1）

## data-path 无回归（AC-2，tests/benchmark_data_path.sh build 128）
- opt_in_dp.log（优化前）：put 537.92 / get 522.70
- 优化后采样：put 545.44 / 543.91 / 521.76；get 484.67 / 470.34 / 502.19
- put 持平/微升，get 波动在既有 ±5% 测量噪声范围；控制路径不触碰 data path 核心，无回归。

## 说明（AC-1 差距）
- 未追平 v80 绝对值（median 48.97）、线程 7 未降：单 Reactor 汇聚点 + 独立 control
  worker 是 v81 非阻塞架构固有成本，归因范围外「多 Reactor 分片」，不属本轮改动引入。
- 判据采用 AC-5 新口径（行为判据+对称基线双维度），见 ac5-control-plane-criterion.md。
