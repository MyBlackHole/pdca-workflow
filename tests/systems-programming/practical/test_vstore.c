#define _POSIX_C_SOURCE 200809L
#include "vstore.h"

#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* Public-API oracle shared by both independently frozen implementations. */
static void empty(const struct vs_view *v)
{
	assert(!v->data && !v->length && !v->private_token);
}

static void stats_valid(struct vs_store *s, size_t versions, size_t bytes)
{
	struct vs_stats v;

	assert(vs_get_stats(s, &v) == 0);
	assert(v.live_versions <= v.peak_versions && v.peak_versions <= versions);
	assert(v.live_payload_bytes <= v.peak_payload_bytes);
	assert(v.peak_payload_bytes <= bytes);
}

struct handoff { struct vs_store *store; struct vs_view view; };

static void *return_view(void *arg)
{
	struct handoff *h = arg;

	assert(h->view.length == 4);
	assert(memcmp(h->view.data, "B\0b!", 4) == 0);
	vs_release(h->store, &h->view);
	empty(&h->view);
	return NULL;
}

static void capacity_and_lifetime(void)
{
	struct vs_options o = { 3, 12 };
	struct vs_store *s = NULL;
	struct vs_view a = {0}, c = {0}, missing = {0};
	struct handoff h = {0};
	struct vs_stats st;
	pthread_t thread;
	unsigned char input[4] = { 'A', 0, 'a', '!' };

	assert(vs_create(&o, &s) == 0);
	assert(vs_publish(s, 9, input, sizeof(input)) == 0);
	memset(input, 0xff, sizeof(input));
	assert(vs_acquire(s, 9, &a) == 0);
	assert(memcmp(a.data, "A\0a!", 4) == 0);
	assert(vs_publish(s, 9, "B\0b!", 4) == 0);
	h.store = s;
	assert(vs_acquire(s, 9, &h.view) == 0);
	assert(vs_publish(s, 9, "C\0c!", 4) == 0);
	assert(vs_acquire(s, 9, &c) == 0);
	assert(vs_get_stats(s, &st) == 0);
	assert(st.live_versions == 3 && st.live_payload_bytes == 12);
	assert(vs_publish(s, 9, "D\0d!", 4) == -EAGAIN);
	assert(vs_publish(s, 9, input, 13) == -EMSGSIZE);
	assert(memcmp(a.data, "A\0a!", 4) == 0);
	vs_release(s, &a);
	empty(&a);
	assert(vs_publish(s, 9, "D\0d!", 4) == 0);
	assert(memcmp(c.data, "C\0c!", 4) == 0);
	assert(pthread_create(&thread, NULL, return_view, &h) == 0);
	assert(pthread_join(thread, NULL) == 0);
	empty(&h.view);
	stats_valid(s, 3, 12);
	assert(vs_close(s) == 0 && vs_close(s) == 0);
	assert(vs_publish(s, 9, "x", 1) == -ESHUTDOWN);
	missing = (struct vs_view){input, 4, input};
	assert(vs_acquire(s, 9, &missing) == -ESHUTDOWN);
	empty(&missing);
	assert(vs_destroy(s) == -EBUSY);
	assert(memcmp(c.data, "C\0c!", 4) == 0);
	vs_release(s, &c);
	empty(&c);
	assert(vs_destroy(s) == 0);
	puts("PASS shared oracle: capacity, binary snapshots, handoff, close, busy destroy");
}

static void parameters_and_zero(void)
{
	struct vs_options o = {2, 8}, invalid = {0, 8};
	struct vs_store *s = (struct vs_store *)(uintptr_t)1;
	struct vs_view v = {(void *)(uintptr_t)1, 1, (void *)(uintptr_t)1};
	struct vs_stats st;

	assert(vs_create(&invalid, &s) == -EINVAL && !s);
	assert(vs_create(NULL, &s) == -EINVAL && !s);
	assert(vs_create(&o, NULL) == -EINVAL);
	assert(vs_acquire(NULL, 1, &v) == -EINVAL);
	empty(&v);
	assert(vs_create(&o, &s) == 0);
	assert(vs_publish(s, 1, NULL, 1) == -EINVAL);
	v = (struct vs_view){s, 1, s};
	assert(vs_acquire(s, 1, &v) == -ENOENT);
	empty(&v);
	assert(vs_publish(s, 1, NULL, 0) == 0);
	assert(vs_acquire(s, 1, &v) == 0);
	assert(v.length == 0);
	assert(vs_get_stats(s, &st) == 0);
	assert(st.live_versions == 1 && st.live_payload_bytes == 0);
	assert(vs_destroy(s) == -EBUSY);
	vs_release(s, &v);
	empty(&v);
	assert(vs_destroy(s) == 0);
	puts("PASS shared oracle: invalid outputs, missing key, zero-length version");
}

enum { WRITERS = 4, READERS = 4, STEPS = 4000 };
struct packet { uint64_t writer, sequence; unsigned char bytes[64]; };
struct parallel { struct vs_store *store; pthread_barrier_t start; };
struct worker { struct parallel *shared; unsigned int id; };

static void meet(pthread_barrier_t *barrier)
{
	int rc = pthread_barrier_wait(barrier);

	assert(rc == 0 || rc == PTHREAD_BARRIER_SERIAL_THREAD);
}

static void *publisher(void *arg)
{
	struct worker *w = arg;
	struct packet p;
	unsigned int i;

	meet(&w->shared->start);
	for (i = 0; i < STEPS; ++i) {
		p.writer = w->id;
		p.sequence = i;
		memset(p.bytes, (int)((i + w->id) & 255), sizeof(p.bytes));
		assert(vs_publish(w->shared->store, w->id, &p, sizeof(p)) == 0);
		memset(&p, 0xee, sizeof(p));
		stats_valid(w->shared->store, 64, 65536);
	}
	return NULL;
}

static void *reader(void *arg)
{
	struct worker *w = arg;
	unsigned int i;

	meet(&w->shared->start);
	for (i = 0; i < STEPS; ++i) {
		struct vs_view v;
		struct packet copy;
		unsigned int key = (i + w->id) % WRITERS;
		int rc = vs_acquire(w->shared->store, key, &v);
		size_t j;

		if (rc == -ENOENT) {
			empty(&v);
			continue;
		}
		assert(rc == 0 && v.length == sizeof(copy));
		memcpy(&copy, v.data, sizeof(copy));
		assert(copy.writer == key && copy.sequence < STEPS);
		for (j = 0; j < sizeof(copy.bytes); ++j)
			assert(copy.bytes[j] == ((copy.sequence + key) & 255));
		sched_yield();
		assert(memcmp(&copy, v.data, sizeof(copy)) == 0);
		vs_release(w->shared->store, &v);
		empty(&v);
		stats_valid(w->shared->store, 64, 65536);
	}
	return NULL;
}

static void parallel_snapshots(void)
{
	struct parallel p;
	struct vs_options o = {64, 65536};
	struct worker w[WRITERS + READERS];
	pthread_t thread[WRITERS + READERS];
	unsigned int i;

	assert(vs_create(&o, &p.store) == 0);
	assert(pthread_barrier_init(&p.start, NULL, WRITERS + READERS) == 0);
	for (i = 0; i < WRITERS + READERS; ++i) {
		w[i] = (struct worker){ &p, i % WRITERS };
		assert(pthread_create(&thread[i], NULL,
		       i < WRITERS ? publisher : reader, &w[i]) == 0);
	}
	for (i = 0; i < WRITERS + READERS; ++i)
		assert(pthread_join(thread[i], NULL) == 0);
	assert(pthread_barrier_destroy(&p.start) == 0);
	assert(vs_close(p.store) == 0);
	stats_valid(p.store, 64, 65536);
	assert(vs_destroy(p.store) == 0);
	puts("PASS shared oracle: 4 publishers + 4 readers, 32000 calls, stable borrowed views");
}

int main(void)
{
	parameters_and_zero();
	capacity_and_lifetime();
	parallel_snapshots();
	return 0;
}
