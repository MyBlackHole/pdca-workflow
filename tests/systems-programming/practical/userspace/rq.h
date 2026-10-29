#ifndef RQ_H
#define RQ_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rq;

struct rq_options {
	size_t max_items;
	size_t max_payload_bytes;
	void (*consume)(const void *data, size_t len, void *arg);
	void *arg;
};

struct rq_stats {
	size_t live_items;
	size_t live_payload_bytes;
	size_t peak_live_items;
	size_t peak_live_payload_bytes;
	bool closed;
};

int rq_create(const struct rq_options *options, struct rq **out);
int rq_submit(struct rq *queue, const void *data, size_t len);
int rq_get_stats(struct rq *queue, struct rq_stats *out);
int rq_close(struct rq *queue);
void rq_destroy(struct rq *queue);

#ifdef __cplusplus
}
#endif

#endif
