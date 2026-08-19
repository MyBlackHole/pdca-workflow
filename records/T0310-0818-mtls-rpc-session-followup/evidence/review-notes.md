# T0310 implementation review notes

The fd-only RPC business call sites were migrated to explicit session I/O;
the server-side send/receive macros were removed. Public command helpers now
receive `rpc_io_t *`, and file-stat/ioctl/mkdir/unlink paths use the negotiated
session. The handshake client rejects a response with an operation other than
NEGOTIATE.

Remaining limitation: the newly added real rdbcomm tool test currently
exercises the plaintext command round trip. mTLS protocol behavior is covered
by the existing certificate-backed handshake test and the production tool
paths, but a complete tool-level mTLS command round trip still needs a
certificate fixture whose CA-CN directory layout matches the runtime selector.
