# T0328 Real-process Verification

## dm-ftp

`dm-ftp` started with `AIO_SBT_MTLS_ENABLE=1` and the existing CA/server
certificate/key. `openssl s_client` supplied the client certificate and
completed TLS 1.3 with `TLS_AES_256_GCM_SHA384`; a 24-byte dmsbtex application
header was then written over the TLS connection.

With the client certificate omitted, the same server returned TLS alert
`certificate required` and the client exited non-zero. This confirms mTLS
failure does not silently fall back to plaintext.

## FileTransferAgent

`FileTransferAgent` started with the same mTLS configuration. A client with
the test certificate completed TLS 1.3 with `TLS_AES_256_GCM_SHA384`.

## Plaintext rejection

Sending bytes with `nc` to an mTLS-enabled `dm-ftp` listener produced zero
response bytes. The listener did not accept the plaintext stream as an SBT
application connection.

## Remaining limitation

## External SBT ABI

The built `dmsbtex_mtls_client_test` completed the real dmsbtex ABI sequence
`sbtinit` → `sbtinit2` → `sbtbackup` → `sbtwrite` → `sbtclose` → `sbtend`
against `dm-ftp` with mTLS enabled and exited `0`.

The built `libobk_mtls_client_test` completed
`sbtinit2` → `sbtbackup` → `sbtwrite2` → `sbtclose2` → `sbtend` against
`FileTransferAgent` with mTLS enabled and exited `0`.

The same two client tests against mTLS-disabled servers completed with exit
code `0`, proving the existing plaintext business path remains usable.

Using the SM2 client certificate against the classic CA caused the dmsbtex
client to receive EOF during the first response and exit non-zero, proving a
certificate mismatch is not accepted as a successful business connection.
