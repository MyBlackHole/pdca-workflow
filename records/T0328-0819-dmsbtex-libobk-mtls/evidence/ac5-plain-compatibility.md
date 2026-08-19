# T0328 Do Evidence

## Build

Command:

```text
xmake -b dmsbtex sbt FileTransferAgent dm-ftp sbt_transport_test
```

Result: passed (`build ok`). The four requested SBT/service targets and the
transport integration test compile and link with `sbt_transport` and
`tls_cert`.

## mTLS transport test

Command:

```text
env CERT_DIR="$PWD/libs/tests/certs" \
  build/linux/x86_64/debug/sbt_transport_test
```

Result: exit code `0`. The forked TCP client/server load the existing CA,
client and server certificates, complete mutual TLS handshakes, and exchange
`sbt`/`ok` payloads through `sbt_transport_send/recv`.

## I/O boundary check

Command:

```text
rg -n '\\b(send|recv|read|write)\\s*\\(' \
  dmsbtex/network.c libobk/lib/logic/oracleCmdTbl.c libs/sbt_transport.c
```

Result: raw `send/recv` calls occur only in `libs/sbt_transport.c` as the
plain fallback; dmsbtex and libobk protocol paths call the transport wrapper.

## Hygiene

`git diff --check` passed.
