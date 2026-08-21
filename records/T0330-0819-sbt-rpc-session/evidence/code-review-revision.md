## Revision review

- ABI blocking issue from the first implementation is fixed: `struct sbtctx` is unchanged from the original baseline.
- The session transport adapter is shared by dmsbtex and libobk and delegates handshake/read/write/cleanup to existing RPC session APIs.
- `sbtinfo2()` retains the original `ctx->pairs` meaning while recovering the private session through a flexible-array container.
- Added module-level protocol tests and linked them through xmake.
- No transport lock or global fd/session lookup was introduced.

Remaining boundary: the test environment has no configured certificate chain, so the RPC test exercises the plain fallback; certificate-backed mTLS integration requires the deployment certificate environment.
