#!/usr/bin/env python3
"""
Java Advanced — Batch 1
Topics: java-multithreading, java-concurrency-advanced
Unit 14 (Java Advanced), orders 107-108
Run: python3 scripts/gen_java_advanced_batch1.py [--overwrite]
"""

import json, sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/dsa-java"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "java-multithreading",
        "unit": 14,
        "order": 107,
        "title": "Java Multithreading",
        "summary": "Master Thread lifecycle, synchronization, volatile, wait/notify, and thread-safe patterns in Java.",
        "prereqs": ["dsa-java-arrays"],
        "guide": """# Java Multithreading — Make Your Code Do Two Things At Once

## Mental Model
A thread is an independent path of execution inside a JVM process. Every Java program starts with one thread (main). Creating more lets you do work in parallel — but sharing state between them is where bugs hide.

```
Process (JVM)
├── Thread: main()          ← always exists
├── Thread: http-handler-1  ← your server handling request 1
├── Thread: http-handler-2  ← your server handling request 2
└── Thread: GC              ← JVM internal
```

## Creating Threads

### Way 1 — extend Thread
```java
class CounterThread extends Thread {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(getName() + ": " + i);
        }
    }
}
new CounterThread().start();  // start(), NOT run() — run() executes in current thread!
```

### Way 2 — implement Runnable (preferred — decouples task from thread)
```java
Runnable task = () -> System.out.println("Hello from: " + Thread.currentThread().getName());
Thread t = new Thread(task);
t.start();
```

### Way 3 — ExecutorService (production way)
```java
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(() -> processRequest(req));
pool.shutdown();   // graceful: wait for submitted tasks to finish
```

## Thread Lifecycle
```
NEW → start() → RUNNABLE ⟷ (scheduler decides) ⟷ RUNNING
                  │                                    │
                  └── wait() / sleep() ──→ WAITING/TIMED_WAITING
                  └── synchronized block busy ──→ BLOCKED
                  └── run() returns ──→ TERMINATED
```

## The Race Condition Problem
```java
class Counter {
    int count = 0;                // shared mutable state — DANGER
    void increment() { count++; } // NOT atomic: read → add → write (3 ops)
}
Counter c = new Counter();
// Two threads calling c.increment() 1000 times each
// Expected: 2000. Actual: somewhere between 1000 and 2000. BUG.
```

## Synchronized — Mutual Exclusion Lock
```java
class SafeCounter {
    private int count = 0;

    synchronized void increment() {  // only one thread at a time
        count++;
    }

    synchronized int get() { return count; }
}
```
`synchronized` acquires the object's intrinsic lock. Other threads block until it's released.

### Synchronized block (finer granularity)
```java
private final Object lock = new Object();

void transfer(Account from, Account to, int amount) {
    synchronized(lock) {     // lock specific object, not `this`
        from.debit(amount);
        to.credit(amount);
    }
}
```

## volatile — Visibility Guarantee
```java
class FlagExample {
    volatile boolean running = true;    // force reads/writes to main memory

    void stop() { running = false; }

    void run() {
        while (running) { /* work */ }  // without volatile, compiler may cache `running` in register
    }
}
```
`volatile` solves visibility (every thread sees the latest value) but NOT atomicity. Don't use for compound operations like `count++`.

## wait / notify — Thread Coordination
```java
class BoundedQueue<T> {
    private final Queue<T> queue = new LinkedList<>();
    private final int max;

    synchronized void put(T item) throws InterruptedException {
        while (queue.size() == max) wait();    // release lock, pause
        queue.add(item);
        notifyAll();                            // wake waiting consumers
    }

    synchronized T take() throws InterruptedException {
        while (queue.isEmpty()) wait();
        T item = queue.poll();
        notifyAll();                            // wake waiting producers
        return item;
    }
}
```
**Rule:** always call `wait()` inside a `while` loop — not `if` — because of spurious wakeups.

## Common Pitfalls
- **Calling `run()` instead of `start()`**: runs in current thread — no new thread created
- **Deadlock**: Thread A holds lock 1, waits for lock 2. Thread B holds lock 2, waits for lock 1. Both stuck forever. Fix: always acquire locks in the same order.
- **Using `volatile` for `count++`**: volatile doesn't make compound ops atomic. Use `AtomicInteger`.
- **Not calling `pool.shutdown()`**: threads keep running, JVM won't exit.
- **`synchronized(this)` in different instances**: each instance has its own lock — no mutual exclusion across instances.

## Connections
- `java-concurrency-advanced` — builds on this with java.util.concurrent tools
- `dsa-java-queues` — BlockingQueue is the thread-safe version
- `system-design-fundamentals` — thread pools are core to server architecture
""",
        "questions": [
            {"id": "jmt-q1", "type": "mcq", "prompt": "What is the correct way to start a new thread from a `Thread` subclass instance `t`?", "choices": ["t.run()", "t.start()", "t.execute()", "Thread.run(t)"], "answerIndex": 1, "explanation": "`start()` creates a new OS thread and calls `run()` in it. Calling `run()` directly executes in the current thread — no concurrency.", "tags": ["thread-basics"]},
            {"id": "jmt-q2", "type": "mcq", "prompt": "What does `volatile` guarantee in Java?", "choices": ["Atomicity of compound operations", "Visibility: every thread reads the latest written value from main memory", "Thread-safe increment", "Lock acquisition"], "answerIndex": 1, "explanation": "`volatile` ensures visibility — no CPU cache or compiler register caching. It does NOT make `count++` atomic (that's 3 operations).", "tags": ["volatile"]},
            {"id": "jmt-q3", "type": "codeOutput", "prompt": "What is the expected value of `count` after two threads each call `increment()` 1000 times, where `increment()` does `count++` without synchronization?", "choices": ["Always 2000", "Always 1000", "Somewhere between 1000 and 2000 (non-deterministic)", "Compilation error"], "answerIndex": 2, "explanation": "Without synchronization, `count++` is a read-add-write race condition. Both threads can read the same value, both add 1, and one write is lost.", "tags": ["race-condition"]},
            {"id": "jmt-q4", "type": "mcq", "prompt": "What does `synchronized` on a method do?", "choices": ["Runs the method in a new thread", "Acquires the object's intrinsic lock — only one thread can execute it at a time", "Makes the method atomic at CPU level", "Prevents the method from being overridden"], "answerIndex": 1, "explanation": "`synchronized` on an instance method acquires `this` object's monitor lock. On a static method, it acquires the class object's lock.", "tags": ["synchronized"]},
            {"id": "jmt-q5", "type": "mcq", "prompt": "Why must `wait()` always be called inside a `while` loop (not `if`)?", "choices": ["It's just style convention", "Spurious wakeups — a thread can wake up without being notified, so the condition must be re-checked", "while loops are faster", "If causes a deadlock"], "answerIndex": 1, "explanation": "The JVM can wake up a waiting thread without an explicit notify (spurious wakeup). Always recheck the condition after waking.", "tags": ["wait-notify"]},
            {"id": "jmt-q6", "type": "mcq", "prompt": "What causes a deadlock?", "choices": ["Too many threads", "Two threads waiting for locks held by each other, indefinitely", "A thread calling sleep()", "Forgetting to call start()"], "answerIndex": 1, "explanation": "Deadlock: Thread A holds lock 1, waits for lock 2. Thread B holds lock 2, waits for lock 1. Neither can proceed. Prevention: always acquire multiple locks in the same order.", "tags": ["deadlock"]},
            {"id": "jmt-q7", "type": "mcq", "prompt": "What is `Executors.newFixedThreadPool(4)`?", "choices": ["Creates 4 threads immediately and runs 4 tasks", "Creates a pool of 4 reusable threads — tasks queue up when all are busy", "Creates 4 thread groups", "Limits JVM to 4 threads total"], "answerIndex": 1, "explanation": "A fixed thread pool reuses threads. New tasks queue in a `LinkedBlockingQueue` when all threads are busy. Better than creating a new `Thread` per task.", "tags": ["thread-pool", "executor"]},
            {"id": "jmt-q8", "type": "mcq", "prompt": "What happens if you call `pool.shutdown()` vs `pool.shutdownNow()`?", "choices": ["Both immediately kill all threads", "shutdown() waits for running tasks to finish; shutdownNow() interrupts running threads and returns queued tasks", "shutdownNow() is deprecated", "No difference"], "answerIndex": 1, "explanation": "`shutdown()` is graceful — no new tasks accepted, running tasks finish. `shutdownNow()` is forceful — interrupts running threads via interrupt().", "tags": ["executor", "thread-pool"]},
            {"id": "jmt-q9", "type": "codeOutput", "prompt": "Thread A acquires lock on `obj1` then tries `obj2`. Thread B acquires lock on `obj2` then tries `obj1`. What happens?", "choices": ["One thread wins", "Deadlock — both threads block indefinitely", "java.lang.DeadlockException is thrown", "The JVM detects and resolves it automatically"], "answerIndex": 1, "explanation": "Classic deadlock scenario. Java does NOT automatically resolve deadlocks — the threads freeze forever. Fix: enforce lock ordering (always acquire obj1 before obj2).", "tags": ["deadlock"]},
            {"id": "jmt-q10", "type": "multi", "prompt": "Which are valid Thread states in Java?", "choices": ["NEW", "RUNNABLE", "SLEEPING", "BLOCKED", "TERMINATED", "IDLE"], "answerIndexes": [0, 1, 3, 4], "explanation": "Java Thread.State enum: NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED. SLEEPING and IDLE are not Java thread states.", "tags": ["thread-lifecycle"]},
            {"id": "jmt-q11", "type": "mcq", "prompt": "What is the difference between `notify()` and `notifyAll()`?", "choices": ["No difference", "notify() wakes one random waiting thread; notifyAll() wakes all waiting threads", "notifyAll() is deprecated", "notify() broadcasts to all threads in the JVM"], "answerIndex": 1, "explanation": "Prefer `notifyAll()` in most cases — safer because `notify()` might wake the wrong thread. `notifyAll()` ensures the right thread eventually re-evaluates its condition.", "tags": ["wait-notify"]},
            {"id": "jmt-q12", "type": "mcq", "prompt": "What is a race condition?", "choices": ["Two threads running at the same speed", "Outcome depends on relative timing/interleaving of threads — non-deterministic result", "A thread that finishes before another", "A synchronized method that is too slow"], "answerIndex": 1, "explanation": "A race condition occurs when correctness depends on timing. The classic example: read-modify-write without synchronization.", "tags": ["race-condition"]},
            {"id": "jmt-q13", "type": "mcq", "prompt": "Which of the following makes `count++` thread-safe without synchronized?", "choices": ["volatile int count", "AtomicInteger count; count.incrementAndGet()", "final int count", "static int count"], "answerIndex": 1, "explanation": "`AtomicInteger.incrementAndGet()` uses CPU-level compare-and-swap (CAS) instructions — atomic without a lock. `volatile` alone doesn't make `++` atomic.", "tags": ["atomics", "volatile"]},
            {"id": "jmt-q14", "type": "codeOutput", "prompt": "What does `Thread.sleep(1000)` do?", "choices": ["Terminates the thread after 1 second", "Pauses the current thread for at least 1000ms, releasing CPU but NOT releasing locks", "Pauses all threads for 1 second", "Releases all held locks for 1 second"], "answerIndex": 1, "explanation": "`sleep()` pauses the thread but retains any locks it holds. This is different from `wait()` which releases the lock.", "tags": ["sleep", "thread-basics"]},
            {"id": "jmt-q15", "type": "mcq", "prompt": "What is a ThreadLocal variable?", "choices": ["A variable accessible by all threads", "Each thread has its own independent copy of the variable", "A variable that can only be written by one thread", "A variable stored on the heap"], "answerIndex": 1, "explanation": "`ThreadLocal<T>` provides thread-isolated storage. Each thread sees its own copy — no synchronization needed. Common use: per-request state in web servers.", "tags": ["thread-local"]},
            {"id": "jmt-q16", "type": "mcq", "prompt": "What does `Runnable` provide over extending `Thread`?", "choices": ["Better performance", "Decouples the task from thread lifecycle; class can still extend another class", "Access to more Thread methods", "Automatic synchronization"], "answerIndex": 1, "explanation": "Java is single-inheritance. `Runnable` lets your class extend a business class AND be scheduled on a thread. Extending `Thread` wastes your one inheritance slot.", "tags": ["runnable", "thread-basics"]},
            {"id": "jmt-q17", "type": "mcq", "prompt": "What is a daemon thread?", "choices": ["A thread that runs with root privileges", "A background thread that JVM kills when all non-daemon threads finish", "A thread that never throws exceptions", "A thread with higher priority"], "answerIndex": 1, "explanation": "Daemon threads (e.g., GC thread) exist to serve others. Set via `t.setDaemon(true)` before start(). JVM exits when only daemon threads remain.", "tags": ["daemon-thread"]},
            {"id": "jmt-q18", "type": "multi", "prompt": "Which problems does `synchronized` solve?", "choices": ["Visibility (ensures value written by one thread is seen by another)", "Atomicity (compound operations treated as one)", "Deadlock prevention", "Performance improvement"], "answerIndexes": [0, 1], "explanation": "`synchronized` provides both visibility (happens-before relationship) and mutual exclusion (atomicity). It does NOT prevent deadlocks and can reduce performance.", "tags": ["synchronized"]},
            {"id": "jmt-q19", "type": "mcq", "prompt": "What does `Thread.join()` do?", "choices": ["Merges two threads into one", "Causes the calling thread to wait until the target thread terminates", "Starts the thread", "Interrupts the thread"], "answerIndex": 1, "explanation": "`t.join()` blocks the calling thread until `t` finishes. Used to wait for results from a thread before proceeding.", "tags": ["thread-basics", "join"]},
            {"id": "jmt-q20", "type": "mcq", "prompt": "When is `synchronizedMap` preferred over `ConcurrentHashMap`?", "choices": ["Always — it's safer", "Never — ConcurrentHashMap is always better", "When you need full-map locking (e.g., iterating + modifying atomically); ConcurrentHashMap allows concurrent reads/writes but iteration may not be fully consistent", "When performance is not important"], "answerIndex": 2, "explanation": "`ConcurrentHashMap` uses segment-level locks for high throughput. `synchronizedMap` locks the entire map per operation. Use `synchronizedMap` only when you need atomic compound operations on the whole map.", "tags": ["concurrent-collections"]},
        ],
        "flashcards": [
            {"id": "jmt-fc1", "front": "start() vs run()", "back": "`start()` creates a new OS thread and calls `run()` in it. `run()` directly executes in the current thread — no new thread. Always call `start()`.", "tags": ["thread-basics"]},
            {"id": "jmt-fc2", "front": "volatile — what it does and doesn't do", "back": "DOES: guarantees visibility (latest value from main memory, no caching). DOESN'T: make compound operations (count++) atomic. Use AtomicInteger for that.", "tags": ["volatile"]},
            {"id": "jmt-fc3", "front": "Deadlock prevention rule", "back": "Always acquire multiple locks in the same global order. Thread A: lock(obj1) then lock(obj2). Thread B: lock(obj1) then lock(obj2). Never reverse the order.", "tags": ["deadlock"]},
            {"id": "jmt-fc4", "front": "wait() must be in while, not if", "back": "Spurious wakeups: JVM can wake a thread without notify(). Always: `while (!condition) wait()`. The condition must be re-checked after every wakeup.", "tags": ["wait-notify"]},
            {"id": "jmt-fc5", "front": "Thread pool sizing rule of thumb", "back": "CPU-bound tasks: pool size ≈ CPU cores. I/O-bound tasks: pool size = cores × (1 + wait_time/compute_time). Too many threads → context-switch overhead.", "tags": ["thread-pool"]},
            {"id": "jmt-fc6", "front": "sleep() vs wait()", "back": "`sleep()`: pauses thread, KEEPS locks, requires no monitor. `wait()`: pauses thread, RELEASES lock, must be called inside synchronized block. Both throw InterruptedException.", "tags": ["sleep", "wait-notify"]},
            {"id": "jmt-fc7", "front": "ThreadLocal use case", "back": "Per-thread state without synchronization. Classic uses: database connection per thread, user session in web framework, SimpleDateFormat (not thread-safe). Set via `tl.set(val)`, get via `tl.get()`.", "tags": ["thread-local"]},
            {"id": "jmt-fc8", "front": "AtomicInteger vs synchronized", "back": "AtomicInteger: lock-free using CAS hardware instruction. Faster for single-variable increments. synchronized: heavier lock, needed for multi-variable atomic operations.", "tags": ["atomics"]},
        ],
        "project": {
            "brief": "Design a thread-safe producer-consumer task queue in Java. Producers submit tasks (Runnable). Consumers pull and execute tasks. Requirements: bounded queue (max 10 tasks), producers block when full, consumers block when empty, graceful shutdown (drain queue then stop). Design the class structure: fields, constructors, methods. Identify every point where synchronization is needed and why. Note which operations must be atomic. You don't need to write running code — map out the design decisions.",
            "checklist": [
                {"id": "jmt-p1", "text": "Identify shared mutable state and the synchronization primitive for each", "weight": 25},
                {"id": "jmt-p2", "text": "Design put() and take() with correct wait/notifyAll logic in while loops", "weight": 25},
                {"id": "jmt-p3", "text": "Design shutdown() that drains the queue before stopping consumer threads", "weight": 25},
                {"id": "jmt-p4", "text": "Identify 2 potential bugs (e.g., calling run() instead of start(), spurious wakeup, deadlock scenario) and explain how your design avoids them", "weight": 25},
            ],
            "hints": [
                "The queue, a `running` flag, and the count are shared state — each needs careful handling.",
                "For shutdown: set `running=false`, then `notifyAll()` so blocked consumers can check the flag.",
                "Use `while (queue.isEmpty() && running) wait()` in take() — not `if` — to handle spurious wakeups.",
                "Consider using `java.util.concurrent.BlockingQueue` and explaining why it's preferable to a hand-rolled solution.",
            ],
        },
    },
    {
        "id": "java-concurrency-advanced",
        "unit": 14,
        "order": 108,
        "title": "Java Concurrency Advanced",
        "summary": "Deep dive into java.util.concurrent: ReentrantLock, CompletableFuture, ForkJoinPool, ConcurrentHashMap, and virtual threads (Project Loom).",
        "prereqs": ["java-multithreading"],
        "guide": """# Java Concurrency Advanced — java.util.concurrent Mastery

## Mental Model
`java.util.concurrent` (JUC) is a toolkit built on top of `synchronized`/`wait`/`notify`. It solves the same problems but with higher-level abstractions, better performance, and more composability.

```
Low level:  synchronized, volatile, wait/notify
    ↓ JUC wraps and extends these:
Mid level:  ReentrantLock, Semaphore, CountDownLatch, CyclicBarrier
High level: ExecutorService, CompletableFuture, ForkJoinPool
Data:       ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
```

## ReentrantLock — Explicit Lock
```java
ReentrantLock lock = new ReentrantLock();

void transfer(int amount) {
    lock.lock();
    try {
        // critical section
        balance -= amount;
    } finally {
        lock.unlock();   // ALWAYS in finally — never forget!
    }
}
```

### Why use ReentrantLock over synchronized?
- `tryLock()` — non-blocking: try to acquire, do something else if busy
- `lockInterruptibly()` — can be interrupted while waiting
- `Condition` — multiple wait-sets per lock (better than single `wait()`)
- Fairness option: `new ReentrantLock(true)` — threads get lock in FIFO order

```java
Condition notFull  = lock.newCondition();
Condition notEmpty = lock.newCondition();

void put(T item) {
    lock.lock();
    try {
        while (size == max) notFull.await();   // more targeted than notifyAll
        add(item);
        notEmpty.signal();
    } finally { lock.unlock(); }
}
```

## CompletableFuture — Async Programming
```java
// Chain async operations without blocking
CompletableFuture<String> cf = CompletableFuture
    .supplyAsync(() -> fetchUserFromDB(userId))     // runs on ForkJoinPool
    .thenApply(user -> user.getName().toUpperCase())// transform result
    .thenCompose(name -> fetchEmailFor(name))       // chain another async op
    .exceptionally(ex -> "default@email.com");      // handle errors

String email = cf.get(); // block and get result
```

### Key methods
| Method | Purpose |
|--------|---------|
| `supplyAsync(supplier)` | Start async task, returns value |
| `runAsync(runnable)` | Start async task, no return |
| `thenApply(fn)` | Transform result (sync) |
| `thenCompose(fn)` | Chain another CF (async) |
| `thenCombine(cf, fn)` | Combine two CFs when both complete |
| `allOf(cf1, cf2, ...)` | Wait for ALL to complete |
| `anyOf(cf1, cf2, ...)` | Wait for ANY to complete |
| `exceptionally(fn)` | Handle exception, return fallback |
| `whenComplete(fn)` | Run action regardless of success/failure |

## ForkJoinPool — Divide and Conquer
```java
class SumTask extends RecursiveTask<Long> {
    private final long[] arr;
    private final int from, to;

    @Override
    protected Long compute() {
        if (to - from <= 1000) {           // base case: small enough to compute
            long sum = 0;
            for (int i = from; i < to; i++) sum += arr[i];
            return sum;
        }
        int mid = (from + to) / 2;
        SumTask left  = new SumTask(arr, from, mid);
        SumTask right = new SumTask(arr, mid,  to);
        left.fork();                       // schedule left asynchronously
        return right.compute() + left.join(); // compute right here, wait for left
    }
}

ForkJoinPool pool = ForkJoinPool.commonPool();
long total = pool.invoke(new SumTask(arr, 0, arr.length));
```

## ConcurrentHashMap — Lock Striping
```java
// Traditional synchronized approach (slow — locks whole map)
Map<String, Integer> syncMap = Collections.synchronizedMap(new HashMap<>());

// ConcurrentHashMap — fine-grained locks per bucket segment
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// Atomic update operations — crucial!
map.compute("key", (k, v) -> v == null ? 1 : v + 1);   // atomic
map.computeIfAbsent("key", k -> new ArrayList<>());      // atomic
map.merge("key", 1, Integer::sum);                        // atomic

// WRONG — two operations, not atomic:
int old = map.get("key");
map.put("key", old + 1);   // race condition!
```

## Semaphore — Rate Limiting
```java
Semaphore semaphore = new Semaphore(3);  // max 3 concurrent

void callExternalAPI() throws InterruptedException {
    semaphore.acquire();           // block if 3 already running
    try {
        // call the API
    } finally {
        semaphore.release();       // always release
    }
}
```
Use for: connection pool limits, rate limiting, parking lot problem.

## CountDownLatch — One-Time Gate
```java
CountDownLatch ready = new CountDownLatch(3);  // waits for 3 countdowns

// Three worker threads signal readiness
new Thread(() -> { setup(); ready.countDown(); }).start();

// Main thread waits
ready.await();  // blocks until count reaches 0
startProcessing();
```
Single-use. Use `CyclicBarrier` for reusable multi-phase barriers.

## Virtual Threads (Project Loom — Java 21+)
```java
// Platform thread — OS thread, expensive (1-2 MB stack each)
Thread t = new Thread(task); t.start();

// Virtual thread — JVM-managed, lightweight (few KB, millions possible)
Thread vt = Thread.ofVirtual().start(task);

// With executor
ExecutorService exec = Executors.newVirtualThreadPerTaskExecutor();
exec.submit(() -> blockingDatabaseCall());  // doesn't block an OS thread!
```

**Key insight:** Virtual threads park when they do I/O (DB, HTTP, file) — freeing the carrier OS thread for other work. Enables 10x higher throughput for I/O-bound servers without async/reactive code.

## Common Pitfalls
- **Not putting `lock.unlock()` in finally**: an exception before unlock → locked forever
- **Mixing synchronized and ReentrantLock on same object**: both are different mechanisms — doesn't work
- **compute() in ConcurrentHashMap for expensive operations**: the lambda runs under a lock — keep it fast
- **Using CompletableFuture.get() in event loop threads**: defeats async — use `thenApply` instead
- **Virtual threads + synchronized**: if a virtual thread blocks inside `synchronized`, it pins its carrier thread (pre-Java 24 issue). Use ReentrantLock with virtual threads.

## Connections
- `java-multithreading` — foundational concepts needed first
- `system-design-fundamentals` — thread pools, async I/O are core design patterns
- `cloud-fundamentals` — reactive/async patterns in cloud-native apps
""",
        "questions": [
            {"id": "jca-q1", "type": "mcq", "prompt": "What advantage does `ReentrantLock.tryLock()` have over `synchronized`?", "choices": ["It's always faster", "It tries to acquire the lock without blocking — returns false immediately if busy", "It prevents deadlocks automatically", "It doesn't need finally"], "answerIndex": 1, "explanation": "`tryLock()` is non-blocking — perfect for implementing timeouts or fallback logic when a resource is busy. `synchronized` always blocks until the lock is available.", "tags": ["reentrant-lock"]},
            {"id": "jca-q2", "type": "mcq", "prompt": "Why MUST `lock.unlock()` be in a finally block?", "choices": ["It's just convention", "If an exception occurs before unlock(), the lock is never released — deadlock for all other threads", "finally runs faster", "unlock() throws if not in finally"], "answerIndex": 1, "explanation": "If the critical section throws, without `finally`, the lock stays acquired. All other threads waiting for it will block forever.", "tags": ["reentrant-lock"]},
            {"id": "jca-q3", "type": "mcq", "prompt": "What does `CompletableFuture.thenCompose()` do vs `thenApply()`?", "choices": ["thenApply chains sync transforms; thenCompose chains async ops that return another CompletableFuture (avoids nesting)", "They are identical", "thenCompose is for error handling", "thenApply runs on a separate thread"], "answerIndex": 0, "explanation": "`thenApply(fn)`: fn returns a plain value (sync transform). `thenCompose(fn)`: fn returns a `CompletableFuture` — used to chain async operations without `CompletableFuture<CompletableFuture<T>>` nesting.", "tags": ["completable-future"]},
            {"id": "jca-q4", "type": "mcq", "prompt": "What is wrong with: `int v = map.get(k); map.put(k, v+1);` on a ConcurrentHashMap?", "choices": ["ConcurrentHashMap doesn't support get/put", "Not atomic — another thread can modify the value between get and put", "put needs synchronized", "get returns null always"], "answerIndex": 1, "explanation": "Even though individual get/put are thread-safe, the two-step read-modify-write is a race condition. Use `map.compute(k, (key, val) -> val == null ? 1 : val + 1)` for atomic update.", "tags": ["concurrent-hashmap"]},
            {"id": "jca-q5", "type": "mcq", "prompt": "What is a virtual thread (Project Loom)?", "choices": ["A thread simulated by the OS", "A lightweight JVM-managed thread that parks when doing I/O, freeing the OS thread for other work", "A thread for UI rendering only", "A thread that runs faster than platform threads"], "answerIndex": 1, "explanation": "Virtual threads are JVM-scheduled and very cheap (few KB each). When they block on I/O, the JVM parks them and the underlying OS thread is freed. Enables millions of concurrent tasks.", "tags": ["virtual-threads", "project-loom"]},
            {"id": "jca-q6", "type": "mcq", "prompt": "What is a Semaphore used for?", "choices": ["Ensuring only one thread runs at a time", "Controlling the number of concurrent threads accessing a resource (permits-based throttling)", "Signaling threads to wake up", "Providing multiple conditions"], "answerIndex": 1, "explanation": "A Semaphore with N permits allows N threads concurrently. Perfect for connection pools, API rate limiting, or any resource with a fixed capacity.", "tags": ["semaphore"]},
            {"id": "jca-q7", "type": "mcq", "prompt": "What does `CompletableFuture.allOf(cf1, cf2, cf3).join()` do?", "choices": ["Completes as soon as any one CF completes", "Blocks until ALL three CompletableFutures complete", "Cancels all CFs", "Runs them sequentially"], "answerIndex": 1, "explanation": "`allOf()` returns a new CF that completes when all provided CFs complete. Use to wait for multiple parallel operations.", "tags": ["completable-future"]},
            {"id": "jca-q8", "type": "mcq", "prompt": "CountDownLatch vs CyclicBarrier — key difference?", "choices": ["No difference", "CountDownLatch is one-shot (can't reset); CyclicBarrier is reusable and runs a barrier action when all parties arrive", "CyclicBarrier only works with 2 threads", "CountDownLatch requires equal counts"], "answerIndex": 1, "explanation": "Use `CountDownLatch` for one-time coordination (e.g., wait for N services to start). Use `CyclicBarrier` for multi-phase algorithms where N threads must sync at each phase.", "tags": ["countdown-latch", "cyclic-barrier"]},
            {"id": "jca-q9", "type": "codeOutput", "prompt": "What does `ForkJoinPool.commonPool()` refer to?", "choices": ["A pool created per application", "The JVM-wide shared pool, also used by parallel streams and CompletableFuture by default", "A pool for daemon threads only", "A pool limited to 1 thread"], "answerIndex": 1, "explanation": "The common pool is JVM-wide. `CompletableFuture.supplyAsync()` and parallel streams use it by default. Avoid blocking operations inside it — use a custom pool for I/O.", "tags": ["fork-join-pool"]},
            {"id": "jca-q10", "type": "mcq", "prompt": "What does `RecursiveTask.fork()` do in ForkJoinPool?", "choices": ["Starts a new OS thread", "Schedules the task for async execution in the pool without blocking", "Splits the task into exactly 2", "Copies the task data"], "answerIndex": 1, "explanation": "`fork()` schedules the task asynchronously. `join()` waits for and retrieves its result. The pattern: fork left, compute right locally, join left.", "tags": ["fork-join-pool"]},
            {"id": "jca-q11", "type": "mcq", "prompt": "Why is `ConcurrentHashMap.compute()` preferred for atomic updates?", "choices": ["It's faster than put()", "The entire read-modify-write operation runs atomically under a bucket lock", "It avoids null values", "It triggers CAS at CPU level"], "answerIndex": 1, "explanation": "`compute()` holds the bucket lock for the entire lambda execution, making the read-modify-write atomic. Never call expensive operations inside `compute()` though — it blocks other threads updating that bucket.", "tags": ["concurrent-hashmap"]},
            {"id": "jca-q12", "type": "mcq", "prompt": "What is lock striping in ConcurrentHashMap?", "choices": ["Locking the entire map", "Dividing the map into segments/buckets, each with its own lock — allows concurrent access to different buckets", "A deprecated feature from Java 7", "Locking only on write, not read"], "answerIndex": 1, "explanation": "ConcurrentHashMap (Java 8+) locks at the bucket/bin level, not the whole map. Multiple threads can update different buckets concurrently — much better throughput than `synchronizedMap`.", "tags": ["concurrent-hashmap"]},
            {"id": "jca-q13", "type": "mcq", "prompt": "What is the issue with virtual threads and `synchronized` blocks (pre-Java 24)?", "choices": ["Virtual threads cannot enter synchronized blocks", "A virtual thread inside a synchronized block pins its carrier OS thread — defeating the benefit", "synchronized is deprecated for virtual threads", "No issue — works normally"], "answerIndex": 1, "explanation": "Before Java 24, when a virtual thread blocks inside `synchronized`, it pins the carrier thread (the OS thread can't be used by other virtual threads). Use `ReentrantLock` with virtual threads to avoid pinning.", "tags": ["virtual-threads"]},
            {"id": "jca-q14", "type": "multi", "prompt": "Which are thread-safe collection alternatives in java.util.concurrent?", "choices": ["ConcurrentHashMap", "CopyOnWriteArrayList", "Collections.synchronizedList()", "ArrayList", "BlockingQueue"], "answerIndexes": [0, 1, 4], "explanation": "ConcurrentHashMap, CopyOnWriteArrayList, and BlockingQueue are JUC thread-safe. `Collections.synchronizedList()` is synchronized but not JUC. `ArrayList` is not thread-safe.", "tags": ["concurrent-collections"]},
            {"id": "jca-q15", "type": "mcq", "prompt": "When is CopyOnWriteArrayList appropriate?", "choices": ["High-write scenarios", "Read-heavy scenarios with rare writes — each write creates a new copy of the array", "Multi-producer queues", "When exact iteration order is needed"], "answerIndex": 1, "explanation": "COW creates a new array copy on every mutation — reads are always lock-free. Perfect for observer/listener lists (rare changes, frequent iteration). Bad for high-write workloads.", "tags": ["concurrent-collections"]},
            {"id": "jca-q16", "type": "mcq", "prompt": "What does `CompletableFuture.exceptionally(fn)` do?", "choices": ["Rethrows the exception", "Handles the exception and provides a fallback value — the chain continues normally", "Cancels the CompletableFuture", "Logs the exception"], "answerIndex": 1, "explanation": "`exceptionally(fn)` is like a catch block for async chains. If any stage throws, fn is called with the exception and returns a recovery value.", "tags": ["completable-future", "error-handling"]},
            {"id": "jca-q17", "type": "mcq", "prompt": "What is the advantage of virtual threads for I/O-bound servers?", "choices": ["They use less CPU", "Millions of virtual threads can exist; blocking I/O parks the virtual thread instead of blocking an OS thread — much higher concurrency", "They bypass the JVM", "They eliminate synchronization needs"], "answerIndex": 1, "explanation": "Traditional: 1 OS thread per connection → max ~10k connections. Virtual threads: 1 virtual thread per connection, I/O parks it → millions of connections on same hardware.", "tags": ["virtual-threads"]},
            {"id": "jca-q18", "type": "mcq", "prompt": "What does `Executors.newVirtualThreadPerTaskExecutor()` do?", "choices": ["Creates a fixed pool of virtual threads", "Creates a new virtual thread for each submitted task — like newCachedThreadPool but with virtual threads", "Reuses virtual threads from a pool", "Creates OS threads faster"], "answerIndex": 1, "explanation": "Each submitted task gets its own virtual thread. Since virtual threads are cheap, this scales to millions of concurrent tasks — ideal for I/O-heavy workloads.", "tags": ["virtual-threads", "executor"]},
            {"id": "jca-q19", "type": "mcq", "prompt": "What is the 'Work Stealing' algorithm in ForkJoinPool?", "choices": ["Threads steal CPU time", "Idle threads steal tasks from busy threads' local queues — better CPU utilisation", "Threads steal from main queue only", "A deprecated scheduling algorithm"], "answerIndex": 1, "explanation": "Each ForkJoinPool thread has a local deque. When idle, it steals tasks from the end of busy threads' deques. This minimises idle time in divide-and-conquer algorithms.", "tags": ["fork-join-pool"]},
            {"id": "jca-q20", "type": "multi", "prompt": "Which are valid reasons to use ReentrantLock over synchronized?", "choices": ["Need tryLock() with timeout", "Need lockInterruptibly()", "Need multiple Condition objects per lock", "Need lock without a try block", "Need fairness (FIFO lock acquisition)"], "answerIndexes": [0, 1, 2, 4], "explanation": "ReentrantLock provides: tryLock() with/without timeout, lockInterruptibly(), multiple Conditions, and optional fairness. These are impossible with synchronized.", "tags": ["reentrant-lock"]},
        ],
        "flashcards": [
            {"id": "jca-fc1", "front": "ReentrantLock unlock() rule", "back": "Always in `finally`: `lock.lock(); try { ... } finally { lock.unlock(); }`. Exception before unlock = permanent deadlock for all waiting threads.", "tags": ["reentrant-lock"]},
            {"id": "jca-fc2", "front": "thenApply vs thenCompose", "back": "`thenApply(fn)`: fn returns T (sync transform). `thenCompose(fn)`: fn returns `CompletableFuture<T>` (async chain). Use thenCompose to avoid CF<CF<T>> nesting.", "tags": ["completable-future"]},
            {"id": "jca-fc3", "front": "ConcurrentHashMap atomic update", "back": "`map.compute(key, (k,v) -> v == null ? 1 : v+1)` — atomic. `map.get()` then `map.put()` — race condition. For aggregation use `merge()`: `map.merge(key, 1, Integer::sum)`.", "tags": ["concurrent-hashmap"]},
            {"id": "jca-fc4", "front": "Virtual thread benefit (one sentence)", "back": "I/O-blocking parks the virtual thread, freeing its OS carrier thread — enables millions of concurrent connections without reactive/async complexity.", "tags": ["virtual-threads"]},
            {"id": "jca-fc5", "front": "Semaphore pattern", "back": "`sem.acquire()` then `try { ... } finally { sem.release() }`. Use for: DB connection pools, API rate limiting, any fixed-capacity resource.", "tags": ["semaphore"]},
            {"id": "jca-fc6", "front": "CountDownLatch vs CyclicBarrier", "back": "CountDownLatch: one-shot gate, countdown to 0, can't reset. CyclicBarrier: reusable, all N parties call `await()` to sync at a phase, can reset.", "tags": ["countdown-latch"]},
            {"id": "jca-fc7", "front": "ForkJoin pattern", "back": "`left.fork()` (async), then `right.compute()` (sync in current thread), then `left.join()` (wait for left). Compute locally, don't fork both — avoids unnecessary overhead.", "tags": ["fork-join-pool"]},
            {"id": "jca-fc8", "front": "Virtual thread + synchronized trap", "back": "Pre-Java 24: `synchronized` inside a virtual thread pins the carrier OS thread, defeating concurrency. Use `ReentrantLock` with virtual threads to avoid pinning.", "tags": ["virtual-threads"]},
        ],
        "project": {
            "brief": "Design an async HTTP request aggregator. It calls 3 external APIs in parallel (user profile, orders history, recommendations), merges the results, and returns within a 2-second timeout. Use CompletableFuture. Also design: (1) a connection pool using Semaphore to limit to 10 concurrent outbound connections, (2) a fallback for when any API fails, (3) a timeout strategy. Sketch the CompletableFuture chain — no running code needed, just pseudo-Java showing the composition.",
            "checklist": [
                {"id": "jca-p1", "text": "Model 3 parallel API calls with supplyAsync + thenApply", "weight": 20},
                {"id": "jca-p2", "text": "Combine results with allOf() or thenCombine() correctly", "weight": 20},
                {"id": "jca-p3", "text": "Add exceptionally() fallback for each API call", "weight": 20},
                {"id": "jca-p4", "text": "Implement 2-second timeout with orTimeout(2, SECONDS)", "weight": 20},
                {"id": "jca-p5", "text": "Design Semaphore-based connection pool wrapping each API call", "weight": 20},
            ],
            "hints": [
                "Use `CompletableFuture.allOf(cf1, cf2, cf3).thenApply(v -> merge(cf1.join(), cf2.join(), cf3.join()))`",
                "Each individual CF should have `.exceptionally(ex -> defaultValue)` before combining.",
                "orTimeout(2, TimeUnit.SECONDS) on the combined CF. Handle TimeoutException in exceptionally.",
                "Semaphore wrapper: `sem.acquire(); try { return callAPI(); } finally { sem.release(); }` — wrap this in supplyAsync.",
            ],
        },
    },
]


def write_topic(topic: dict, overwrite: bool = False) -> None:
    path = OUT / f"{topic['id']}.json"
    if path.exists() and not overwrite:
        if len(topic.get("questions", [])) >= 20:
            print(f"  SKIP {path.name}")
            return
    path.write_text(json.dumps(topic, indent=2, ensure_ascii=False))
    print(f"  WROTE {path.name} ({len(topic.get('questions', []))}q, {len(topic.get('flashcards', []))}fc)")


if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    print(f"Writing Java Advanced batch 1 → {OUT}/")
    for t in TOPICS:
        write_topic(t, overwrite)
    print("Done.")

