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

The real-process probes use `openssl s_client` as the client and prove server
handshake/application ingress, but do not yet invoke Oracle RMAN or the full
dmsbtex/libobk external SBT ABI. mTLS-disabled full business regression also
remains to be run.
