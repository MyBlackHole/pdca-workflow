#define _POSIX_C_SOURCE 200809L
#include "rq.h"
#include "bench_profile.h"

#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

static _Atomic uint64_t alloc_calls, alloc_success, free_calls, live_allocs, peak_allocs;
static _Atomic uint64_t lock_calls, wait_sum, wait_max, hold_sum, hold_max, hold_segments;
static _Thread_local uint64_t held_since;

static uint64_t now_ns(void)
{
	struct timespec t;
	assert(clock_gettime(CLOCK_MONOTONIC, &t) == 0);
	return (uint64_t)t.tv_sec * UINT64_C(1000000000) + (uint64_t)t.tv_nsec;
}

static void maximum(_Atomic uint64_t *counter, uint64_t value)
{
	uint64_t old = atomic_load_explicit(counter, memory_order_relaxed);

	while (old < value &&
	       !atomic_compare_exchange_weak_explicit(counter, &old, value,
		       memory_order_relaxed, memory_order_relaxed))
		;
}

/* Only rq.c is compiled with these names. Harness allocations are excluded. */
void *profile_malloc(size_t size)
{
	void *p;

	atomic_fetch_add_explicit(&alloc_calls, 1, memory_order_relaxed);
	p = malloc(size);
	if (p) {
		uint64_t live;
		atomic_fetch_add_explicit(&alloc_success, 1, memory_order_relaxed);
		live = atomic_fetch_add_explicit(&live_allocs, 1, memory_order_relaxed) + 1;
		maximum(&peak_allocs, live);
	}
	return p;
}

void profile_free(void *pointer)
{
	if (!pointer)
		return;
	free(pointer);
	atomic_fetch_add_explicit(&free_calls, 1, memory_order_relaxed);
	assert(atomic_fetch_sub_explicit(&live_allocs, 1, memory_order_relaxed) > 0);
}

int profile_mutex_lock(pthread_mutex_t *lock)
{
	uint64_t before = now_ns(), acquired, elapsed;
	int rc = pthread_mutex_lock(lock);

	acquired = now_ns();
	assert(!held_since);
	if (!rc) {
		held_since = acquired;
		elapsed = acquired - before;
		atomic_fetch_add_explicit(&lock_calls, 1, memory_order_relaxed);
		atomic_fetch_add_explicit(&wait_sum, elapsed, memory_order_relaxed);
		maximum(&wait_max, elapsed);
	}
	return rc;
}

static void end_hold(void)
{
	uint64_t elapsed;

	assert(held_since);
	elapsed = now_ns() - held_since;
	held_since = 0;
	atomic_fetch_add_explicit(&hold_segments, 1, memory_order_relaxed);
	atomic_fetch_add_explicit(&hold_sum, elapsed, memory_order_relaxed);
	maximum(&hold_max, elapsed);
}

int profile_mutex_unlock(pthread_mutex_t *lock)
{
	end_hold();
	return pthread_mutex_unlock(lock);
}

int profile_cond_wait(pthread_cond_t *cond, pthread_mutex_t *lock)
{
	int rc;

	/* Exclude condition sleep and its implicit mutex reacquisition from hold. */
	end_hold();
	rc = pthread_cond_wait(cond, lock);
	if (!rc)
		held_since = now_ns();
	return rc;
}

struct header { uint64_t id, submitted_ns; };
struct run {
	struct rq *queue;
	pthread_barrier_t start;
	size_t total, payload, producers;
	uint64_t *latencies;
	unsigned char *seen;
	size_t consumed;
	_Atomic uint64_t retries;
};
struct producer { struct run *run; size_t id; };

static void consume(const void *data, size_t length, void *arg)
{
	struct run *r = arg;
	struct header h;
	const unsigned char *bytes = data;
	size_t j;
	uint64_t arrived = now_ns();

	assert(length == r->payload);
	memcpy(&h, data, sizeof(h));
	assert(h.id < r->total && !r->seen[h.id]);
	for (j = sizeof(h); j < length; ++j)
		assert(bytes[j] == (unsigned char)h.id);
	r->seen[h.id] = 1;
	r->latencies[h.id] = arrived - h.submitted_ns;
	++r->consumed;
}

static void meet(pthread_barrier_t *barrier)
{
	int rc = pthread_barrier_wait(barrier);
	assert(rc == 0 || rc == PTHREAD_BARRIER_SERIAL_THREAD);
}

static void *produce(void *arg)
{
	struct producer *p = arg;
	struct run *r = p->run;
	size_t count = r->total / r->producers;
	unsigned char *input = calloc(1, r->payload);
	size_t i;

	assert(input);
	meet(&r->start);
	for (i = 0; i < count; ++i) {
		struct header h = {p->id * count + i, 0};
		int rc;
		uint64_t retries = 0;

		memset(input, (unsigned char)h.id, r->payload);
		do {
			/* The successful attempt's start defines submit-to-callback latency. */
			h.submitted_ns = now_ns();
			memcpy(input, &h, sizeof(h));
			rc = rq_submit(r->queue, input, r->payload);
			if (rc == -EAGAIN) {
				++retries;
				sched_yield();
			}
		} while (rc == -EAGAIN);
		assert(rc == 0);
		atomic_fetch_add_explicit(&r->retries, retries, memory_order_relaxed);
	}
	free(input);
	return NULL;
}

static int compare(const void *a, const void *b)
{
	uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
	return (x > y) - (x < y);
}

static size_t number(const char *s, size_t max)
{
	char *end;
	unsigned long long n;

	errno = 0;
	n = strtoull(s, &end, 10);
	assert(!errno && *s && !*end && n > 0 && n <= max);
	return (size_t)n;
}

static long process_peak_rss(void)
{
	FILE *status = fopen("/proc/self/status", "r");
	char line[256];
	long peak = -1;

	assert(status);
	while (fgets(line, sizeof(line), status)) {
		if (sscanf(line, "VmHWM: %ld kB", &peak) == 1)
			break;
	}
	assert(fclose(status) == 0 && peak >= 0);
	return peak;
}

int main(int argc, char **argv)
{
	struct run r = {0};
	struct rq_options o;
	struct rq_stats stats;
	struct rusage usage;
	struct producer producers[16];
	pthread_t threads[16];
	uint64_t started, elapsed, closed_at, close_ns;
	uint64_t ac, locks, segments;
	size_t i;
	int profiled;

	if (argc != 4) {
		fprintf(stderr, "usage: %s producers payload-bytes total-messages\n", argv[0]);
		return 2;
	}
	r.producers = number(argv[1], 16);
	r.payload = number(argv[2], 1048576);
	r.total = number(argv[3], 1000000);
	assert(r.payload >= sizeof(struct header) && r.total % r.producers == 0);
	r.latencies = calloc(r.total, sizeof(*r.latencies));
	r.seen = calloc(r.total, sizeof(*r.seen));
	assert(r.latencies && r.seen);
	o = (struct rq_options){512, 512 * r.payload, consume, &r};
	assert(rq_create(&o, &r.queue) == 0);
	assert(pthread_barrier_init(&r.start, NULL, (unsigned int)r.producers + 1) == 0);
	for (i = 0; i < r.producers; ++i) {
		producers[i] = (struct producer){ &r, i };
		assert(pthread_create(&threads[i], NULL, produce, &producers[i]) == 0);
	}
	started = now_ns();
	meet(&r.start);
	for (i = 0; i < r.producers; ++i)
		assert(pthread_join(threads[i], NULL) == 0);
	closed_at = now_ns();
	assert(rq_close(r.queue) == 0);
	close_ns = now_ns() - closed_at;
	elapsed = now_ns() - started;
	assert(r.consumed == r.total);
	for (i = 0; i < r.total; ++i)
		assert(r.seen[i]);
	assert(rq_get_stats(r.queue, &stats) == 0);
	assert(stats.closed && !stats.live_items && !stats.live_payload_bytes);
	assert(stats.peak_live_items <= o.max_items);
	assert(stats.peak_live_payload_bytes <= o.max_payload_bytes);
	rq_destroy(r.queue);
	assert(pthread_barrier_destroy(&r.start) == 0);
	ac = atomic_load(&alloc_calls);
	profiled = ac != 0;
	assert(!atomic_load(&live_allocs));
	if (profiled)
		assert(atomic_load(&alloc_success) == atomic_load(&free_calls));
	assert(getrusage(RUSAGE_SELF, &usage) == 0);
	qsort(r.latencies, r.total, sizeof(*r.latencies), compare);
	printf("{\"profiled\":%s,\"producers\":%zu,\"payload_bytes\":%zu,"
	       "\"messages\":%zu,\"elapsed_ns\":%" PRIu64 ",\"messages_per_s\":%.3f,"
	       "\"latency_p50_ns\":%" PRIu64 ",\"latency_p99_ns\":%" PRIu64 ","
	       "\"close_ns\":%" PRIu64 ",\"eagain_retries\":%" PRIu64 ","
	       "\"peak_live_items\":%zu,\"peak_live_payload_bytes\":%zu,"
	       "\"process_peak_rss_kib\":%ld,\"rusage_maxrss_kib\":%ld",
	       profiled ? "true" : "false", r.producers, r.payload, r.total,
	       elapsed, (double)r.total * 1e9 / (double)elapsed,
	       r.latencies[r.total / 2], r.latencies[(r.total - 1) * 99 / 100],
	       close_ns, atomic_load(&r.retries), stats.peak_live_items,
	       stats.peak_live_payload_bytes, process_peak_rss(), usage.ru_maxrss);
	if (profiled) {
		locks = atomic_load(&lock_calls);
		segments = atomic_load(&hold_segments);
		printf(",\"module_alloc_calls\":%" PRIu64 ",\"module_peak_allocations\":%" PRIu64
		       ",\"module_live_allocations_after_destroy\":%" PRIu64
		       ",\"explicit_lock_calls\":%" PRIu64 ",\"lock_wait_mean_ns\":%.3f"
		       ",\"lock_wait_max_ns\":%" PRIu64 ",\"hold_segments\":%" PRIu64
		       ",\"hold_segment_mean_ns\":%.3f,\"hold_segment_max_ns\":%" PRIu64,
		       ac, atomic_load(&peak_allocs), atomic_load(&live_allocs), locks,
		       locks ? (double)atomic_load(&wait_sum) / (double)locks : 0.0,
		       atomic_load(&wait_max), segments,
		       segments ? (double)atomic_load(&hold_sum) / (double)segments : 0.0,
		       atomic_load(&hold_max));
	}
	puts("}");
	free(r.seen);
	free(r.latencies);
	return 0;
}
