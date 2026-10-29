// SPDX-License-Identifier: GPL-2.0-only
#include <kunit/test.h>
#include <kunit/resource.h>
#include <linux/atomic.h>
#include <linux/completion.h>
#include <linux/err.h>
#include <linux/jiffies.h>
#include <linux/kthread.h>
#include <linux/module.h>
#include <linux/sched.h>
#include <linux/workqueue.h>

struct request_fixture {
	struct workqueue_struct *wq;
	struct work_struct blocker;
	struct work_struct request;
	struct completion blocker_started;
	struct completion blocker_release;
	struct completion started;
	struct completion release;
	struct completion done;
	struct completion cancel_started;
	struct completion cancel_done;
	struct task_struct *canceller;
	atomic_t calls;
	atomic_t timed_out;
	bool hold;
	bool cancelled_pending;
	unsigned char *payload;
	unsigned char observed;
};

static unsigned long deadline(void)
{
	return msecs_to_jiffies(5000);
}

static void blocker_run(struct work_struct *work)
{
	struct request_fixture *f = container_of(work, struct request_fixture, blocker);

	complete(&f->blocker_started);
	if (!wait_for_completion_timeout(&f->blocker_release, deadline()))
		atomic_set(&f->timed_out, 1);
}

static void request_run(struct work_struct *work)
{
	struct request_fixture *f = container_of(work, struct request_fixture, request);

	f->observed = f->payload[0];
	atomic_inc(&f->calls);
	complete(&f->started);
	if (f->hold && !wait_for_completion_timeout(&f->release, deadline()))
		atomic_set(&f->timed_out, 1);
	complete(&f->done);
}

/* Register last: callbacks must end before KUnit frees fixture and payload. */
static void fixture_cleanup(void *arg)
{
	struct request_fixture *f = arg;

	complete_all(&f->blocker_release);
	complete_all(&f->release);
	if (!IS_ERR_OR_NULL(f->canceller))
		kthread_stop(f->canceller);
	cancel_work_sync(&f->request);
	cancel_work_sync(&f->blocker);
	destroy_workqueue(f->wq);
}

static struct request_fixture *fixture_create(struct kunit *test)
{
	struct request_fixture *f;
	int ret;

	f = kunit_kzalloc(test, sizeof(*f), GFP_KERNEL);
	if (!f)
		return NULL;
	f->payload = kunit_kmalloc(test, 64, GFP_KERNEL);
	if (!f->payload)
		return NULL;
	f->payload[0] = 0xa5;
	atomic_set(&f->calls, 0);
	atomic_set(&f->timed_out, 0);
	init_completion(&f->blocker_started);
	init_completion(&f->blocker_release);
	init_completion(&f->started);
	init_completion(&f->release);
	init_completion(&f->done);
	init_completion(&f->cancel_started);
	init_completion(&f->cancel_done);
	INIT_WORK(&f->blocker, blocker_run);
	INIT_WORK(&f->request, request_run);
	f->wq = alloc_ordered_workqueue("systems_resource_test", 0);
	if (!f->wq)
		return NULL;
	ret = kunit_add_action_or_reset(test, fixture_cleanup, f);
	if (ret)
		return NULL;
	return f;
}

static void submitted_request_reads_payload(struct kunit *test)
{
	struct request_fixture *f = fixture_create(test);

	KUNIT_ASSERT_NOT_NULL(test, f);
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->request));
	KUNIT_ASSERT_NE(test, wait_for_completion_timeout(&f->done, deadline()), 0UL);
	/* A completion event is not a blanket callback-lifetime guarantee. */
	flush_work(&f->request);
	KUNIT_EXPECT_EQ(test, atomic_read(&f->calls), 1);
	KUNIT_EXPECT_EQ(test, f->observed, (unsigned char)0xa5);
	KUNIT_EXPECT_EQ(test, atomic_read(&f->timed_out), 0);
}

static void pending_cancel_prevents_callback(struct kunit *test)
{
	struct request_fixture *f = fixture_create(test);

	KUNIT_ASSERT_NOT_NULL(test, f);
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->blocker));
	KUNIT_ASSERT_NE(test,
			wait_for_completion_timeout(&f->blocker_started, deadline()), 0UL);
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->request));
	KUNIT_EXPECT_TRUE(test, cancel_work_sync(&f->request));
	KUNIT_EXPECT_EQ(test, atomic_read(&f->calls), 0);
	complete(&f->blocker_release);
	flush_work(&f->blocker);
	KUNIT_EXPECT_EQ(test, atomic_read(&f->timed_out), 0);
}

static int cancel_running(void *arg)
{
	struct request_fixture *f = arg;

	complete(&f->cancel_started);
	f->cancelled_pending = cancel_work_sync(&f->request);
	complete(&f->cancel_done);
	/* Keep task_struct alive until fixture_cleanup calls kthread_stop(). */
	for (;;) {
		set_current_state(TASK_INTERRUPTIBLE);
		if (kthread_should_stop())
			break;
		schedule();
	}
	__set_current_state(TASK_RUNNING);
	return 0;
}

static void running_cancel_waits_for_callback(struct kunit *test)
{
	struct request_fixture *f = fixture_create(test);

	KUNIT_ASSERT_NOT_NULL(test, f);
	f->hold = true;
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->request));
	KUNIT_ASSERT_NE(test, wait_for_completion_timeout(&f->started, deadline()), 0UL);
	f->canceller = kthread_run(cancel_running, f, "systems_cancel_test");
	KUNIT_ASSERT_NOT_ERR_OR_NULL(test, f->canceller);
	KUNIT_ASSERT_NE(test,
			wait_for_completion_timeout(&f->cancel_started, deadline()), 0UL);
	KUNIT_EXPECT_EQ(test,
			wait_for_completion_timeout(&f->cancel_done, 1), 0UL);
	complete(&f->release);
	KUNIT_ASSERT_NE(test,
			wait_for_completion_timeout(&f->cancel_done, deadline()), 0UL);
	/* False reports pending status; it does not mean synchronization failed. */
	KUNIT_EXPECT_FALSE(test, f->cancelled_pending);
	KUNIT_EXPECT_TRUE(test, completion_done(&f->done));
	KUNIT_EXPECT_EQ(test, atomic_read(&f->timed_out), 0);
}

static void timeout_keeps_request_and_payload_alive(struct kunit *test)
{
	struct request_fixture *f = fixture_create(test);

	KUNIT_ASSERT_NOT_NULL(test, f);
	f->hold = true;
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->request));
	KUNIT_ASSERT_NE(test, wait_for_completion_timeout(&f->started, deadline()), 0UL);
	KUNIT_EXPECT_EQ(test, wait_for_completion_timeout(&f->done, 1), 0UL);
	KUNIT_EXPECT_EQ(test, f->payload[0], (unsigned char)0xa5);
	complete(&f->release);
	KUNIT_ASSERT_NE(test, wait_for_completion_timeout(&f->done, deadline()), 0UL);
	flush_work(&f->request);
	KUNIT_EXPECT_EQ(test, atomic_read(&f->calls), 1);
	KUNIT_EXPECT_EQ(test, atomic_read(&f->timed_out), 0);
}

static void disable_blocks_requeue_until_enabled(struct kunit *test)
{
	struct request_fixture *f = fixture_create(test);

	KUNIT_ASSERT_NOT_NULL(test, f);
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->request));
	flush_work(&f->request);
	disable_work_sync(&f->request);
	KUNIT_EXPECT_FALSE(test, queue_work(f->wq, &f->request));
	KUNIT_EXPECT_EQ(test, atomic_read(&f->calls), 1);
	KUNIT_EXPECT_TRUE(test, enable_work(&f->request));
	KUNIT_ASSERT_TRUE(test, queue_work(f->wq, &f->request));
	flush_work(&f->request);
	KUNIT_EXPECT_EQ(test, atomic_read(&f->calls), 2);
}

static void completed_tokens_can_precede_waiters(struct kunit *test)
{
	DECLARE_COMPLETION_ONSTACK(event);

	complete(&event);
	complete(&event);
	KUNIT_EXPECT_NE(test, wait_for_completion_timeout(&event, 1), 0UL);
	KUNIT_EXPECT_NE(test, wait_for_completion_timeout(&event, 1), 0UL);
	KUNIT_EXPECT_EQ(test, wait_for_completion_timeout(&event, 1), 0UL);
}

static struct kunit_case resource_cases[] = {
	KUNIT_CASE(submitted_request_reads_payload),
	KUNIT_CASE(pending_cancel_prevents_callback),
	KUNIT_CASE(running_cancel_waits_for_callback),
	KUNIT_CASE(timeout_keeps_request_and_payload_alive),
	KUNIT_CASE(disable_blocks_requeue_until_enabled),
	KUNIT_CASE(completed_tokens_can_precede_waiters),
	{}
};

static struct kunit_suite resource_suite = {
	.name = "systems-resource",
	.test_cases = resource_cases,
};

kunit_test_suite(resource_suite);
MODULE_LICENSE("GPL");
