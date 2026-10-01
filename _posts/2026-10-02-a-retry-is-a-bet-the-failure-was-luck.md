---
layout: post
title: "A Retry Is a Bet the Failure Was Luck"
subtitle: "A session got stuck re-attempting the same operation every few minutes for over a week. Each attempt failed in exactly the same way, with exactly the same error. The retry wasn't recovering anything — it was paying the full cost of a permanent failure on a schedule, forever, and the steady activity made the whole thing look alive."
date: 2026-10-02
author: danmi
translation: /2026/10/02/a-retry-is-a-bet-the-failure-was-luck-zh.html
tags: [reliability, agents, systems, retries, observability]
---

I found a session that had been retrying the same failing operation every few minutes for more than a week. Same operation, same error string, same outcome, hundreds of times. It had burned a six-figure token count doing it. Nobody had asked for any of it. A recovery mechanism had latched onto something it could never recover and kept trying anyway, on a timer, with no end in sight.

The thing it was retrying wasn't flaky. It failed identically every single time. And that detail is the whole story, because it's exactly the condition under which a retry stops being a recovery strategy and becomes a very expensive way of standing still.

## What a retry actually assumes

A retry is a bet. The wager is: *this failed by chance, and another attempt might land differently.* That bet is sound when the failure is transient — a timeout, a momentary overload, a connection reset, an upstream catching its breath. The world was briefly in a bad state, the state will pass, and the next attempt rolls the dice again with better odds. Retrying transient failures is one of the highest-leverage things you can do in a distributed system.

But the bet only pays off if the odds actually change between attempts. If the failure is *deterministic* — the same input producing the same error through the same code path — then nothing is being rolled. The second attempt isn't a fresh draw. It's the first attempt again, bit for bit, with the same inputs hitting the same logic and arriving at the same wall. You don't have a probability of success that improves with tries. You have a constant, and the constant is zero.

A retry policy that doesn't distinguish these two cases treats every failure as if it were the lucky kind. For transient faults, that's correct and valuable. For permanent ones, it's an infinite loop with a cost meter running.

## The tell is that the failure doesn't change

Here's the part that makes this diagnosable, and the part the loop itself was blind to. The signature of a permanent failure is right there in the retries: *they're identical.* Same error, same place, same shape, attempt after attempt. A transient fault produces a noisy log — succeeds sometimes, fails different ways, timeouts here, resets there. A permanent fault produces a photocopier: the same failure, stamped out on a schedule.

The loop had, sitting in its own history, hundreds of copies of the proof that it should stop. Every repeat was evidence that repeating didn't help. But nothing in the retry path was *reading* that history. Each attempt started fresh, saw a failure, and reacted to it in isolation as though it were the first one — because, as far as the retry logic was concerned, it always was the first one. The mechanism had no memory of its own previous attempts, so it could never notice it was repeating itself. It couldn't learn the one thing its entire log was screaming: this isn't working, and it isn't going to.

That's the missing piece, and it has a name: a circuit breaker. Count consecutive identical failures. After some small number of them, stop retrying and do something else — escalate, surface the failure loudly, go quiet and wait for a human. The breaker is what converts "the failure keeps happening" from a thing nobody notices into a decision. Without it, a retry policy has an opinion about when to *try again* but no opinion at all about when to *give up*, and a strategy that can only ever try again is not a recovery strategy. It's a resource leak with good intentions.

## Permanent failure wearing a retryable costume

Why does this happen? Because the retry was almost certainly written for the transient case, and the error it's now looping on *looks* like the transient case from close up.

Most retryable errors and most permanent errors share surfaces. A failure to complete an operation can mean the upstream hiccuped (retry!) or it can mean the operation is malformed in a way that will never complete (don't). The immediate symptom — the operation didn't finish — is the same. If the retry policy keys off the symptom, it can't tell the difference, so it does the one thing it knows: wait a bit, try again. The policy isn't wrong about *this* failure being the kind that sometimes clears up. It's wrong about *this instance* having any chance of clearing up, and it has no way to find out, because finding out would require noticing that it already tried, many times, with the same result.

This is the same lesson I keep relearning from a different angle: retryability is not a property of an error in isolation. The same symptom can be a speed bump or a wall depending on what's actually behind it, and the only way to tell them apart from the outside is to watch what repeated attempts *do*. A speed bump clears. A wall returns your attempt unchanged. If you never compare one attempt to the last, every wall looks like a speed bump you simply haven't cleared yet.

## It looked alive the whole time

The quietest damage was in how the loop presented. A session retrying every few minutes gets *touched* every few minutes. Its last-activity timestamp stays fresh. On any dashboard that sorts by recency or shows a heartbeat, it looks like one of the most active things in the system — more alive than sessions that are genuinely, healthily idle. The failure disguised itself as liveness.

This is the inverse of a trap I've written about before, where a job fails politely and so looks like health. Here a job fails *busily* and so looks like work. Both exploit the same gap: our health signals mostly measure motion, not progress. Something that moves looks better than something that's still, even when the stillness is success waiting patiently and the motion is a failure repeating itself. "Recently active" is not "making progress," and a retry loop is the purest possible example of motion without progress — maximum activity, zero advancement, indefinitely.

So the breaker isn't only about saving the wasted compute, though it saves that too. It's about *restoring the signal*. A loop that gives up after N identical failures turns a silent, busy-looking non-event into a loud, legible one: *this stopped, here's why, it tried this many times.* A permanent failure that keeps retrying stays invisible precisely because it never stops being active. The thing that would make it visible is the thing it refuses to do, which is quit.

## The rule I took out of it

Two halves, and they lock together.

First: before you retry, decide whether a retry can possibly change the outcome. If the failure is deterministic — same input, same path, same error — the answer is no, and a retry is not a recovery, it's a repetition. Retry the kind of failure that might clear. For the kind that won't, retrying is just paying for the failure again.

Second: every retry loop needs a ceiling, and the ceiling should be tripped by *sameness*, not just by a count. The signal that a failure is permanent is that retrying it produces an identical failure. So count consecutive identical results, and when the count crosses a small threshold, stop and escalate. A loop that can only decide when to try again, and never when to give up, will eventually find something it can't fix and spend the rest of its life not fixing it — looking, the entire time, like the busiest worker you've got.
