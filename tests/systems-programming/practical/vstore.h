#ifndef PRACTICAL_VSTORE_H
#define PRACTICAL_VSTORE_H
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif
struct vs_store;
struct vs_options { size_t max_versions; size_t max_payload_bytes; };
struct vs_view { const void *data; size_t length; void *private_token; };
struct vs_stats {
 size_t live_versions, live_payload_bytes;
 size_t peak_versions, peak_payload_bytes;
 bool closed;
};
int vs_create(const struct vs_options *options, struct vs_store **out);
int vs_publish(struct vs_store *store, uint64_t key, const void *data, size_t length);
int vs_acquire(struct vs_store *store, uint64_t key, struct vs_view *out);
void vs_release(struct vs_store *store, struct vs_view *view);
int vs_get_stats(struct vs_store *store, struct vs_stats *out);
int vs_close(struct vs_store *store);
int vs_destroy(struct vs_store *store);
#ifdef __cplusplus
}
#endif
#endif
