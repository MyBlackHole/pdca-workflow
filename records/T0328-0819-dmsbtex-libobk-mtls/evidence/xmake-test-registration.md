# xmake test registration

The dmsbtex and libobk ABI test targets now declare:

```lua
add_tests("default", {realtime_output = true})
```

Because this xmake version addresses named tests as `target/default`, the
following commands were used:

```text
xmake test dmsbtex_mtls_client_test/default
xmake test libobk_mtls_client_test/default
env CERT_DIR="$PWD/libs/tests/certs" xmake test sbt_transport_test/default
```

All three reported `100% tests passed`, with exit code `0`. The two ABI tests
ran against live mTLS-enabled `dm-ftp` and `FileTransferAgent` processes.

`xmake test dmsbtex_mtls_client_test` without `/default` still reports
`nothing to test`; that is xmake test-name syntax, not an unregistered test.
