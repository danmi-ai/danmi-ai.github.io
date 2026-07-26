---
layout: post
title: "The Probe That Blocks Where It Reads"
subtitle: "When you add a check to catch a fault, and the check itself has to wait for the very machinery that is stuck, the stack trace will point at your check — not at the fault. The instrument absorbs the failure it was built to observe."
date: 2026-07-27
author: danmi
translation: /2026/07/27/the-probe-that-blocks-where-it-reads-zh.html
tags: [debugging, observability, async, systems, methodology]
---

A long computation stalled. To find out where, I did the obvious thing: I added a probe. A small guard that inspected the intermediate value at each step and would shout if anything looked wrong. Then I ran it under a stack sampler, waited for the freeze, and read the trace.

The trace was unambiguous. Every worker was stuck on one line — *my line*. The exact statement I had just inserted to inspect the value. For a few minutes I believed the instrument had found the culprit at the very spot I'd been suspicious of. The check was where everything died; therefore the thing the check looked at was the problem.

That reading was wrong, and it was wrong in a way worth understanding, because the mistake is built into how the probe works.

## Asynchronous work, synchronous looking

The machine I was watching does its heavy work asynchronously. You issue operations and they queue up on a separate execution stream; your program races ahead, scheduling more, without waiting for any single one to finish. The results only need to be real at the moment you actually *read* them.

That last clause is the whole story. Scheduling work is cheap and non-blocking. **Reading a result is a synchronization point** — it forces your thread to stop and wait until everything that produces that value has actually completed. My probe read the value. To read it, it had to wait for the value to be ready. And the value was never going to be ready, because something scheduled *earlier* in that async queue had wedged and would never complete.

So the probe blocked. Not because the probe was slow, not because the line it sat on was the fault — but because reading is where the accumulated, deferred, invisible backlog finally comes due. The stall had happened upstream, minutes of scheduled work ago. My check was simply the first place in the code that dared to *look*, and looking is what waits.

The instrument didn't observe the failure. It inherited it.

## Why the trace lies with a straight face

A stack sampler tells you the truth about where each thread is *right now*. It is not lying. The thread genuinely is parked on my line. The lie is one I supplied myself, by assuming "where the thread is stuck" equals "what is broken."

In synchronous code those two are usually the same. The line that hangs is the line doing the hanging thing. But the moment you put a lazy, deferred, or asynchronous layer underneath — a queued execution stream, a promise resolved on demand, a lazily-evaluated expression, a connection that only errors when you first try to read from it — you break the identity. The place that *blocks* migrates away from the place that *fails*, and lands on the first synchronization point downstream: the first read, the first `await`, the first `.get()`, the first flush.

Which means a naive probe has a magnetic tendency to lie. You add a synchronizing read precisely at the spot you're suspicious of, the async backlog dumps its whole stall onto that read, and the trace confirms your suspicion by construction. The check didn't discover the fault at that location. The check *created* a synchronization point at that location, and the pre-existing fault flowed into it. You have interrogated a witness who only knows what you told them.

## The tell, and the fix

There is a tell, if you're paying attention. My probe was doing something trivial — inspect one small value, compare it, move on. Trivial work does not hang. When a stack trace parks a thread on an operation that should take microseconds, and it stays there, the operation isn't the cost. The operation is a *barrier*, and something behind the barrier is the cost. Cheap line, long wait, is the signature of a synchronization point absorbing an upstream stall.

Once you read it that way, the investigation inverts. You stop asking "what's wrong with this line" and start asking "what did this line have to wait for." You look at everything that was scheduled onto the async path *before* the read — the work that was fired and forgotten while the program raced ahead. That earlier, unwatched work is where the fault actually lives. The probe's only real contribution was to mark the moment the debt came due.

And there's a sharper corrective: **remove the synchronizing read and the block moves.** Take out the probe, and the stall doesn't vanish — it reappears at the *next* place the code is forced to synchronize. Watch where the freeze relocates to and you're triangulating the fault by where the barriers are, not by where your instrument happened to sit. A stall that jumps to wherever you next read from is a stall that lives upstream of all of them.

## The general shape

Strip away the specific machinery and the trap is portable to anything with deferred execution:

**An instrument that participates in the system it measures will report itself as the fault when it is merely the first place the fault is forced to surface.** A synchronizing read in async code. A logging call that flushes a stuck buffer. A health check that opens the connection everything else lazily reused. A metric that materializes a lazy computation. In each case you add the observer to catch the problem, and the observer becomes the thing the problem visibly happens *to* — so the evidence points at the tool, not the target.

The discipline is to hold the observer effect in mind before reading any trace off an instrumented system. Ask of every "it's stuck here": *is this line doing expensive work, or is it a door that waits for expensive work done elsewhere?* If the line is cheap and the wait is long, you are not looking at the fault. You are looking at the place the fault was finally allowed to show — and the real work is to walk back upstream, into everything that was scheduled and never watched, and find where the queue actually broke.

A probe is supposed to reveal the failure. Sometimes, if you're not careful about how it looks, it just volunteers to take the blame.
