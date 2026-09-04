# Fix Diff Evidence — T0540 mount_verify 容错

## 变更文件
- `fs-backup/fsclient/transfer_file.cpp` — 新增 `is_ephemeral_dir()` + 容错分支
- `rpc/rpc.cpp` — 修复 stale errno 打印，显式区分 IO_EOF

## 核心变更

### 1. transfer_file.cpp:372-384 新增 helper
```cpp
static bool is_ephemeral_dir(const char *path)
{
    if (path == NULL || *path == '\0') return false;
    const char *base = strrchr(path, '/');
    base = base ? base + 1 : path;
    return strncmp(base, "mount_verify", 12) == 0 ||
           strncmp(base, "DISK_CHECK", 10) == 0;
}
```

### 2. transfer_file.cpp:464-483 backup_new_directory 容错
```cpp
ret = rpc_conn_cli_readdir_tree(...);
if (ret != 0) {
    int saved_errno = errno;
    if (is_ephemeral_dir(path) &&
        (saved_errno == ENOENT || saved_errno == ENOTDIR || ret == -3)) {
        WarningLog("skip ephemeral dir %s ret=%d errno=%d", ...);
        return 0;
    }
    ErrorLog(...);
    return -1;
}
```

### 3. rpc/rpc.cpp:1986-1991, 2024-2029 修复 stale errno
```cpp
if (ret == -3) ErrorLog("IO_EOF(ret=-3)"); else ErrorLog("errno...");
```

## 验证
- `xmake build` — 100% ok (9.5s)
- `xmake test` — 32/32 passed
- `ephemeral_dir_test` — 9/9 场景通过
