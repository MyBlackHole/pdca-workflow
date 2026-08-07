# T0226 Evidence

## E1: 改动文件
- `rpc/rpc-io.h`：enum 增 `IO_EOF = 0xfffffffd`（-3）。
- `rpc/rpc-io.cpp` `rpc_recv`：
  - 长度头循环：`nread==0` → `eof=1; break`（不再命中 EINTR/EAGAIN/ErrorLog 分支）。
  - body 循环：`nread==0` → `eof=1; break`（同）。
  - `bytes != sizeof(msg_net_length)` 分支：`eof ? (静默) return IO_EOF : ErrorLog+return -100`。
  - `bytes != msg_length` 分支：`eof ? (静默) return IO_EOF : ErrorLog + return IO_TRUNCATE`。
  - 库函数 EOF 路径不打日志（供调用方语义化），减少重复输出。
- `rpc/rpc-server.cpp` 服务端 worker 主循环（StartRPCServiceWoker 请求接收点）：
  - `bytes == (int)IO_EOF` → `InfoLog`（connection closed by peer） + `goto return__`，
    消除"recv request failure for bad network"误报 Error（rpc-io.cpp:44-51 原噪音源）。
- 既有网络错误路径（EINTR/EAGAIN → WarningLog+continue；RST/错误 → ErrorLog+break）未改。

## E2. 验证
- `xmake build rpc`：build ok，librpc.a 归档成功（rpc-io.cpp + rpc-server.cpp 均通过；IO_EOF 比较用 `(int)IO_EOF` 强转规避 -Werror sign-compare）。
- 实跑（用户提供）：
  ```
  [2026-08-07 11:49:44]|Info|rpc-server.cpp:222| connection closed by peer (EOF). addr:[127.0.0.1:40662].
  [2026-08-07 11:49:44]|Info|rpc-server.cpp:421| close client connection, type [1102], addr:[127.0.0.1:40662].
  ```
  原 "recv request failure for bad network" 误报消失；EOF 走 Info 干净关闭。
- 冗余收敛：rpc_recv 库函数内部不再打 EOF Info，仅 server 主循环统一打一次（用户反馈前两步冗余）。

## E3. 语义对齐
| 返回 | 含义 | 日志 |
|------|------|------|
| bytes>0 | 完整收到 | 无 |
| -100/-200/IO_TRUNCATE | 网络错误/长度不符 | ErrorLog（保持） |
| IO_EOF(-3) | 对端正常关闭(EOF) | server 主循环 Info |
- 调用点 `rpc_recv(...)<0` / `<1` 判定行为不变（IO_EOF<0）。原被误打的 3 条 Error 噪音消除，改为 1 条 Info（close by peer）。