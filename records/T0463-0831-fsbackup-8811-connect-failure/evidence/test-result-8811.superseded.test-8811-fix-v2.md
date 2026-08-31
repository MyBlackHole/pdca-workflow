# Test Result: 8811 连接失败诊断修复回归

## 执行时间
2026-08-31 17:03:42+08:00

## 环境
- 宿主机 fsdeamon build/linux/x86_64/release/fsdeamon (修复后)
- VM aio-speedd -p 8811 --daemon (PID 1604)
- qemu hostfwd tcp::8811-:8811
- fsbackup.ko 已加载 MAJOR 248

## 测试步骤与结果

### 1. 修复前基线 (network.log 16:29:20)
- `fs-cli --method=add-trackup --bak-path=/opt/aio/` 三次失败
- 日志仅 `connect to:[127.0.0.1:8811] failure` 无细分
- 客户端 `{"msg":"add trackup dir failure."}` 无 host:port

### 2. 修复后 AddSource 预检 (AC-2)
```bash
./fs-cli --host=127.0.0.1 --port=8901 --method=add-source --source=127.0.0.1:8811 --source-name=wdg
# 响应
{"data":{...},"msg":"success","precheck":"ok","result":"true"}
```
- 预检通过，日志 Warning 提示 qemu/aio-speedd 状态

### 3. 修复后 AddTrackup 错误透出 (AC-2, AC-3)
```bash
./fs-cli --host=127.0.0.1 --port=8901 --method=add-trackup --source-name=wdg --bak-path=/opt/aio/
# 响应 (EEXIST 场景，因内核已存在)
{"msg":"add trackup dir failure: 127.0.0.1:8811 connect/ioctl failed (see network.log FsKernel_AddTrackup/handshake, check aio-speedd -p 8811 / qemu hostfwd / /dev/fsbackup)","source_host":"127.0.0.1","source_port":8811}
# network.log
FsKernel_AddTrackup /opt/aio/ -> 127.0.0.1:8811 failed: File exists, errno:17
```
- 客户端含 host:port，日志细分 EEXIST 而非 connect failure

### 4. aio-speed 直连验证 (AC-1, AC-4)
```bash
xmake run aio-speed -h 127.0.0.1 -p 8811 -c "ls -alh"
# 2026-08-31 17:02:14 connect_server_session 127.0.0.1:8811 mtls=0 success fd=8
# total 8K, aio-speed.sock 列出，说明 8811 链路已通
```

### 5. strace 核心 bug 验证
- 修复前 `connect(14, 127.0.0.1:8811)=0` 但仍报 connect failure (判断 `!=0` 误判 fd=10)
- 修复后 `if (conn_ret <0)` 正确，connect success 后进入 do_fsbacup_dev_ioctl，透出真实 ioctl 错误

## 结论
- AC-1 日志细分: 通过 (handshake vs connect, mtls, errno)
- AC-2 客户端透出: 通过 (host:port + 提示)
- AC-3 预检: 通过 (precheck ok)
- AC-4 回归: 通过 (aio-speed 通, add-trackup 错误细分)
