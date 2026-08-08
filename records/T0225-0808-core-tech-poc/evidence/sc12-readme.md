# 场景12 零拷贝传输

**验证**：sendfile / splice vs 用户态 read+write 副本，经 127.0.0.1 回环 socket 传输 1GB 文件。

## 原理

备份大流量（全量备份上传、恢复写盘）的常规路径是 **read() → 用户缓冲 → write()**，
每字节经历 **2 次用户态拷贝 + 2 次内核态拷贝**。零拷贝把数据留在内核态：

```
V1 用户态副本                  V2 sendfile              V3 splice
─────────────                ─────────────            ─────────────
文件fd ──read──> 用户buf         文件fd                      文件fd
                    │             │ sendfile                    │ splice
                    write         │ (内核态直发 socket)         │ (fd→pipe)
                    │             ▼                            ▼
                  socket        socket                      pipe
                                                              │ splice
                                                              ▼
                                                            socket
CPU 拷贝: 用户2次+内核2次      CPU 拷贝: 0 次             CPU 拷贝: 0 次
                             (DMA 直接内核缓冲→网卡)     (pipe 缓冲, 仍免用户态)
```

| 路径 | 用户态拷贝 | 内核态拷贝 | CPU 开销 |
|------|-----------|-----------|---------|
| V1 用户态副本 | 2 次 | 2 次 | 最高 |
| V2 sendfile | 0 | 0（DMA） | 最低 |
| V3 splice | 0 | 1（pipe 中转） | 低 |

## 实测（本机回环）

| 路径 | 耗时 | 吞吐 | 加速比 |
|------|------|------|--------|
| V1 用户态副本 read+write | ~400 ms | ~2.4 GB/s | 1.0x |
| V2 sendfile | ~190–250 ms | ~4.1–5.4 GB/s | 1.6–2.3x |
| V3 splice | ~190–260 ms | ~4.0–5.4 GB/s | 1.6–2.1x |

## 结论

- **sendfile 最优**：单次 syscall、无用户态拷贝、无 pipe 中转，吞吐与 CPU 都最佳，是备份传输主路径首选。
- **splice 次之**：fd↔socket 间不便直接 sendfile 时（如加密管道、chunk 缓冲）用 splice，代价是 pipe 多一次内核缓冲拷贝。
- 回环链路已近内存带宽，用户态拷贝占比有限（加速比约 1.6–2.3x）；**真实网络（百兆/千兆）下用户态拷贝的 syscall 与缓存压力占比更大，零拷贝收益更高**。
- 通用 `sendfile` 不适合读端不落盘的场景（加密/压缩直通），需用 `splice` 或 io_uring。

## 断言

- `sendfile ≥ 1.5x 用户态副本`，`splice ≥ 1.5x 用户态副本`。
