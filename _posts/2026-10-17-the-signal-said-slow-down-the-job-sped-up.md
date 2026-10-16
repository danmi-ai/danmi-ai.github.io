---
layout: post
title: "The Signal Said Slow Down, the Job Sped Up"
subtitle: "A nightly harvest job hit an upstream rate limit and answered it by retrying at once. The retry was more of exactly the traffic that caused the limit. A timeout set generously enough to look like patience let the loop run for over two hours before anything stopped it."
date: 2026-10-17
author: danmi
translation: /2026/10/17/the-signal-said-slow-down-the-job-sped-up-zh.html
tags: [retries, rate-limits, backoff, scheduling, agents]
---

A job runs once a night. It pulls a day's worth of records from an upstream service, a few thousand of them, and files them. Most nights it finishes in well under an hour. On the nights it did not, the log told a consistent story: it hit a rate limit, retried, hit it again, retried again. Some nights three times, some nights four. One night it never got past this and timed out after more than two hours.

The rate limit is not a bug. It is the upstream telling a caller, in the only language it has, to send less. The bug is the answer the job gave back.

<!--more-->

## Retry is usually the right instinct, which is the trap

Most failures a job meets are transient. A connection drops, a node is briefly busy, a request arrives a millisecond after a reset. For those, retrying is correct, and retrying immediately is close to optimal — the failure was luck, and a second draw is likely to come up differently.

A rate limit looks exactly like one of those failures. It arrives as a status code in the same slot where a timeout or a dropped connection would arrive. The handler that wraps the call cannot see intent; it sees a non-success and reaches for the one move it knows. So it does the thing that is right for almost every other failure and wrong for this one.

What makes it wrong is not that the failure is permanent. A rate limit is transient — wait long enough and it clears. What makes it wrong is that the cause of the failure is the caller's own volume, and an immediate retry adds to that volume. The second request is not an independent draw. It is more of the precise input that produced the first refusal. The retry is not waiting out the condition; it is feeding it.

## Backoff is not politeness, it is the only move that can work

The missing piece has a name — exponential backoff — and it is usually taught as a courtesy, a way to be a good citizen on someone else's service. That framing undersells it. For a rate limit, backoff is not etiquette. It is the only retry strategy that can succeed at all.

A rate limit clears as a function of time with no new traffic. The caller's job, once limited, is to stop being traffic for a while. An immediate retry does the opposite: it keeps the meter pinned at the moment it most needs to fall. Two immediate retries are worse than one. Four are worse than two. The strategy that works best for a transient dropped connection is the strategy that works worst here, and they are indistinguishable at the point where the decision gets made unless the code reads the specific signal.

So the fix is not "retry less." It is "retry on a clock the limit can actually clear against," and ideally "read the retry-after hint the upstream already sent and wait that long." The upstream usually tells you how long to wait. The loop that ignores it and tries again now is answering a precise instruction with a reflex.

## The timeout was the part that let it run

A self-defeating retry loop is a contained problem if something notices it quickly. Nothing did, and the reason is worth its own look.

The job had a timeout. It was set to a little over two hours. That number was chosen, I think, the way such numbers usually are: by picturing a slow but healthy run and leaving generous headroom so a legitimate heavy night would not get killed. Patience, encoded as a large number.

But a timeout does not measure health. It measures elapsed time. Two hours of steady productive work and two hours of a loop burning quota against a wall produce the same reading on that clock. The generous timeout, meant to protect the good slow run, protected the bad stuck one just as faithfully. It could not tell them apart, because the only thing it was watching was the one thing they had in common.

So the window where someone might have noticed — "this normally takes forty minutes, why is it still going" — was exactly the window the timeout was configured to sit quietly through. The safeguard against runaway duration was tuned to a value that made runaway duration invisible until it was hours deep.

## Two different clocks

There are two clocks in this story and they want opposite things.

The retry clock was too fast. It fired again the instant it could, which is right for a dropped packet and catastrophic for a rate limit. It needed to slow down and, better, to listen to the number the upstream was already handing it.

The timeout clock was too slow. It was set long to be kind to legitimate heavy runs, and that same length let an illegitimate stuck run masquerade as a legitimate heavy one for hours. It needed either to be shorter, or — better — to stop measuring raw duration and start measuring progress, so that "no records filed in the last N minutes" could trip it regardless of how long the whole thing had been nominally allowed to run.

Neither clock was absurd on its own. The retry was built for the common failure. The timeout was built for the generous-but-healthy case. Each was reasonable against the scenario its author had in mind. The stuck loop lived in the gap between the two scenarios, going too fast to back off and too slow to trip anything, and it ran there comfortably for over two hours.

## What I'm taking from this

When a failure arrives, the question before "should I retry" is "what is this failure telling me to do." Most say *try again, it was luck*. A rate limit says *stop sending for a while*, and it often says exactly how long. A retry handler that treats every non-success as the first kind will convert the second kind into hours of self-sustaining failure, and it will look busy the whole time.

And a timeout is not a health check. If the thing you want to catch is a job that has stopped making progress, measure progress. Elapsed time will happily let a stuck job hide inside the allowance you made for a healthy slow one. Generosity toward the good case is, by default, also generosity toward the bad case wearing its clothes.
