---
layout: post
title: "The Reporter Divided by Zero at the Finish Line"
subtitle: "A progress reporter for a long batch job started failing every run and got itself switched off. The batch hadn't broken — it had finished. Completion drove the counts it divided by down to zero, and the tool built to announce 'done' crashed at the exact moment done arrived, then removed itself for failing too many times in a row."
date: 2026-09-28
author: danmi
translation: /2026/09/28/the-reporter-divided-by-zero-at-the-finish-line-zh.html
tags: [debugging, systems, methodology, reliability, monitoring]
---

A small recurring job existed to report progress on a long batch task. Twice a day it woke up, counted how much work had been done since last time, and posted a line: throughput this period, running daily average, an ETA for the whole thing. Useful, boring, the kind of thing you forget is even running.

Then it started failing. Every run. And after ten failures in a row, the scheduler did what it's supposed to do with a job that keeps crashing: it disabled it.

## The batch didn't break — it succeeded

The reporter hadn't gone wrong because the batch went wrong. It went wrong because the batch *finished*.

When work is flowing, "items processed this period" is some healthy positive number, and the math is fine. When the batch completes, that number goes to zero. Nothing new happened this period because there's nothing left to happen. And the reporter computed throughput and ETA by dividing by that count. Zero in the denominator. Crash. The very last stretch of the job had also come back all-errors-no-successes, which is a second zero denominator in the success-rate line, waiting behind the first.

So the failure wasn't in the batch. It was in the reporter's picture of what a batch *is*. It had been written for a task that is always partway through — always with some work just done and some work still ahead. The one state it was never taught to describe was the state it was built to announce: finished.

## The states you most want a signal for are the degenerate ones

This is the part worth keeping, because it generalizes past this one script.

Instrumentation gets written for the middle of a process. You're watching a thing run, so you reach for the quantities that describe running: rate, percent complete, time remaining, average per period. Every one of those is a fraction, and every one of those fractions degenerates at a boundary. Rate divides by elapsed time — undefined at the very start, when elapsed is zero. Percent divides by a total — undefined when the set is empty. ETA divides by throughput — undefined the moment throughput drops to zero, which is precisely what "done" looks like from the inside.

The cruel part is which states those are. Empty, just-started, all-failed, complete — these are not obscure edge cases you can shrug off. They're the states you most want a clear signal for. "The set is empty." "Nothing succeeded this round." "It's finished." Those are the headlines. And they're exactly the inputs that make rate-and-average math divide by zero, because that math silently assumes it's being called in the steady state, mid-stream, where the denominators are safely positive.

So the reporter was most likely to break at the exact moments its report mattered most.

## The guardrail enforced the silence

There's a second layer, and it's the one that turns an annoyance into a real loss.

A recurring job that fails ten times running gets auto-disabled. That rule is correct in general — you don't want a broken job hammering away forever, alerting on nothing. But look at what it did here. The reporter's job was to deliver one message: the outcome. It crashed trying to deliver that message. It crashed again the next run, same reason, because the batch was still finished. Ten crashes later the guardrail removed it — permanently, until a human notices.

The result is that the completion notice, the single most important thing this tool would ever send, was the one thing guaranteed not to go out. Not because anyone suppressed it, but because the tool broke on the completion input and the safety mechanism then swept the broken tool away before it could ever succeed. The silence at the finish line was enforced twice: once by the divide-by-zero, once by the disable that followed.

## The fix is a posture, not a patch

The immediate repair is boring: guard the denominators. If nothing was processed this period, don't compute a rate — say "nothing this period." If the total is zero, don't compute a percent. If the task is complete, don't extrapolate an ETA for work that no longer exists — say "done," with the final tally, and stop.

But the posture underneath is the real lesson. A monitoring or reporting tool should treat terminal and empty states as first-class outputs, each with its own message, not as extreme values plugged into the running-state math and hoped to survive. "Done" is not a very small amount of remaining work. "Empty" is not a very small set. "All failed" is not a very low success rate. They are different messages, and the tool that only knows how to describe motion will choke on stillness — usually right when stillness is the news.

And the meta-lesson, for anyone who leans on auto-disable as a safety net: it protects you from a job that fails on garbage, but it also silences a job that fails on the one input it exists to handle. Before you trust a self-disabling guardrail, check that the failures it's counting aren't happening on the payload you actually needed delivered.
