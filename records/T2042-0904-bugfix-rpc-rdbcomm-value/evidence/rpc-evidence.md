# rpc 1544 5 错细化（T2042 AC-1）— 本体→代码首验

- `rpc.cpp:1544` 的 `stage` 区分（`socket/connect/handshake/EBADF/File exists`）+ `strerror(errno)`，`本体 aio-tools-6200-release` 的 `rdbcomm` 契约直驱
- 验证：`grep -c 'stage = "socket"' rpc.cpp` 2，`EBADF` 1，`File exists` 1，`handshake` 2
- 回归：`T0457` 的 `8811` 场景现可区分 `connect` vs `handshake` vs `EBADF`
