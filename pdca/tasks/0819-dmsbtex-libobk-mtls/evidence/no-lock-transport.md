# No-lock transport verification

`libs/sbt_transport.c` no longer contains `pthread_mutex_t`, `g_lock`, or a
global fd-to-SSL list. Each owning connection thread stores its active `SSL*`
in thread-local storage; handshake, I/O and cleanup run on that same thread.

Verification:

```text
xmake -b dmsbtex_mtls_client_test libobk_mtls_client_test sbt_transport_test \
  dmsbtex sbt FileTransferAgent dm-ftp
env CERT_DIR="$PWD/libs/tests/certs" \
  xmake test sbt_transport_test/default
```

The build passed, the transport test reported `100% tests passed`, and a
static search found no mutex or lock symbols in the transport implementation.
