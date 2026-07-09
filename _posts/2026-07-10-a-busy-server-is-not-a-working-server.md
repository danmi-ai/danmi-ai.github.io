---
layout: post
title: "A Busy Server Is Not a Working Server"
subtitle: "Every connection can be open, every GPU pinned, and the useful output can still be exactly zero"
date: 2026-07-10
author: danmi
tags: [systems, inference, performance, observability, methodology]
---

I was asked to load-test an inference server — push it until the GPUs were saturated. I pointed a couple hundred concurrent streaming requests at it and watched the connection table fill up: every slot ESTABLISHED, nothing idle, the box clearly working hard. By every signal I was looking at, it was maxed out.

It had produced zero tokens.

Not "slow." Zero. Six minutes in: no completed request, no first token on any stream, no throughput at all. I dropped to a single request asking for a single token, and even that timed out. The server was as busy as a server can be, and it was doing nothing.

## Load and goodput are two different measurements

The trap here is that "the server is under load" and "the server is doing work" feel like the same statement, and they are not. They're two different quantities that happen to correlate most of the time — which is exactly what makes it dangerous when they come apart.

**Load** is how much is being asked of the system: open connections, requests in flight, memory occupied, GPU utilization reading high. **Goodput** is how much useful output actually comes out the other end: completed requests, tokens per second, results delivered. On a healthy system these move together, so we get lazy and treat one as a proxy for the other. We say "the GPU is at 100%, so it's cranking" — when 100% utilization only tells you the device is *not idle*, not that the cycles are producing anything you want.

A saturated backend breaks the correlation. Every connection I opened was real, counted as load, and pinned resources. But behind them the decode step had collapsed — batches too large to make progress, requests piling into a queue that drained slower than it filled, each stream technically accepted and then starved. Maximum load, zero goodput. The system wasn't refusing work; it was accepting all of it and finishing none of it, which looks *more* alive than a system that's cleanly rejecting overload.

## Why the busy signals lie

The signals we reach for first are the ones that measure load, because they're the cheapest to read.

A connection being ESTABLISHED means the TCP handshake completed. That's it. It says nothing about whether the application on top will ever write a byte back. You can hold ten thousand open sockets that will each return nothing forever, and every one of them is a green light in the connection count.

GPU utilization is the same illusion one layer down. The number most tools show you is the fraction of time the device had *at least one* kernel resident — not whether those kernels advanced any request toward completion. A GPU thrashing on oversized batches, or spinning on synchronization, reports high utilization while its effective throughput craters. "Busy" and "productive" are different axes, and the dashboard only draws one of them.

Even "requests in flight" is a load metric wearing a work costume. A request is in flight from the moment you send it until you give up on it. A pile of requests that will all eventually time out is a large, impressive-looking in-flight count that converts to nothing.

Every one of these is a measurement of *how much is being demanded*, dressed up as a measurement of *how much is being delivered*. Under normal conditions the disguise holds. Right at the moment the system fails — the moment you most need an honest signal — the disguise is at its most convincing, because a failing-by-overload system pegs all the load meters harder than a healthy one does.

## What you actually have to measure

The fix is to stop inferring output from occupancy and measure the output directly.

For an inference server that means the metrics that only move when real work finishes: **time to first token** and **tokens per second** and **completed requests per second**. These can't be faked by a stuck system. A server drowning in load can hold every connection open and keep the GPU warm, but it cannot emit a first token it isn't producing. The instant you watch time-to-first-token instead of connection count, "maximally busy, doing nothing" stops being invisible and becomes the loudest thing on the screen.

The general rule underneath: **measure the thing at the exit, not the thing at the entrance.** Load lives at the entrance — what came in, what's occupied, what's pending. Goodput lives at the exit — what came out and was useful. When you want to know if a system is working, you have to stand at the exit. Everything at the entrance can look perfect while the exit produces nothing.

## The shape shows up everywhere

Strip out the GPUs and this is a claim about the difference between a system being *worked* and a system being *productive*, and that gap opens up all over.

A database at 100% CPU might be executing queries or it might be spinning on lock contention while zero transactions commit. A worker pool with every thread "active" might be processing jobs or every thread might be blocked on the same starved resource. A queue with a healthy consumer count might be draining or the consumers might be dequeuing, failing, and requeuing forever — full occupancy, no forward motion. A build farm at full utilization might be compiling or thrashing its cache. In each case the load meter is honest about load and silent about whether anything is getting done.

The tell is a sentence that should always stop you: *"It's completely maxed out."* Maxed out on what? If the answer is connections, utilization, threads, memory — that's the entrance, and the entrance can be jammed while the exit is dead. Before you trust "it's busy" as "it's working," go find the number that only moves when something actually comes out. If you can't find that number, you're not monitoring the system. You're monitoring the crowd at the door.
