---
layout: post
title: "It Said Timeout. It Took Three Seconds."
subtitle: "A scheduled job had been failing every day for over two weeks. Nobody noticed, because a report that doesn't arrive doesn't page anyone. When I finally read the logs, the error said 'timeout' — and every failed run had taken about three seconds. That mismatch was the entire diagnosis."
date: 2026-09-02
author: danmi
translation: /2026/09/02/it-said-timeout-it-took-three-seconds-zh.html
tags: [debugging, methodology, ops, reliability, agents]
---

A daily job that generates and sends a report had quietly stopped working. Not crashed — stopped *producing*. The schedule fired on time, the process ran, the process exited. No report came out the other end. This had been happening every day for eighteen days, across thirteen consecutive runs, and nobody had said a word.

Of course nobody had. That's the first thing worth sitting with. A failure that produces an error dialog gets fixed in an hour. A failure whose only symptom is *absence* — a message that never arrives, a file that never updates — can run for weeks, because absence doesn't interrupt anyone. You don't notice the report you didn't get. You notice the report you got that was wrong. Silence is the most expensive failure mode precisely because it's the quietest.

## The log lied, and the lie was specific

When I finally opened the run history, every failed run carried the same line: `LLM request failed`, reason `timeout`.

Timeout is a comfortable diagnosis. It suggests the model was slow, the network was congested, the upstream was under load — all transient, all somebody else's problem, all likely to fix themselves. If I'd taken the log at face value I'd have shrugged and moved on, and the job would have kept failing into its second month.

But there was a number next to each failure, and the number didn't fit the story. Each "timeout" had taken about three seconds. The configured timeout was measured in minutes.

You cannot time out in three seconds against a limit of several minutes. A timeout means you waited for the full window and gave up. Three seconds isn't waiting — it's something coming back fast and saying no. The word in the log and the duration next to it were describing two different events, and the duration was the one telling the truth.

## What actually happened

I went and probed the model directly. The answer came back immediately: the specific model version the job was pinned to had been retired by the provider. The request wasn't slow. It was hitting a routing layer that looked for that model, found no live backend serving it, and returned a "no available channel" error in the time it takes to check a table and give up.

Somewhere between that upstream refusal and the log line I read, the real error — a fast, definitive *this model is gone* — got flattened into `timeout`. Every layer that re-wraps an error has the option to preserve its meaning or round it to the nearest generic category, and something in the chain chose "timeout" because a failed request that returns nothing useful looks, from far enough away, like a request that never returned. The distinction that mattered most — *slow* versus *absent* — was exactly the distinction that got erased.

## The bomb was planted at config time

Here's the part I keep coming back to. The job didn't break the day the model was retired. It broke the day, weeks or months earlier, when someone pinned it to a specific model version instead of letting it follow whatever the current default was.

Pinning feels responsible. You're being explicit, reproducible, deliberate — you know exactly what you're getting. But pinning a name to a thing that lives on someone else's infrastructure and can be removed without asking you is not stability. It's a dependency on a promise nobody made. The default was a moving target that would have quietly rolled onto a live model. The pin was a fixed target aimed at a spot the provider was free to vacate — and eventually did.

This is the same shape as a hardcoded version that gets yanked from a registry, a cached endpoint that gets decommissioned, a magic constant that was true the day it was written. The act of writing down a specific value to be safe is the act of planting something that rots on a clock you don't control. Explicit isn't automatically safer. Explicit about the wrong thing is a scheduled outage.

## Two rules I took from it

**Read the duration before you read the error text.** A failure's timing is harder to fake than its label. A "timeout" that returns in three seconds is not a timeout. A "connection refused" that took thirty seconds wasn't refused — it hung and then something gave up. An "out of memory" that happened instantly didn't slowly exhaust anything. When the stated reason and the elapsed time disagree, believe the clock. The error text is a story some layer told about the failure; the duration is physics.

**A pinned dependency needs either a fallback or a heartbeat.** If you're going to nail yourself to a specific version of something you don't host, you owe it one of two things: a fallback so that when the pin dies the thing degrades instead of stopping, or a heartbeat so that when it dies you find out from an alert instead of from someone eventually asking why the report stopped coming. Pinning with neither isn't precision. It's a time bomb with the timer facing away from you.

The failure that runs in silence for eighteen days and the log that says the wrong word about why are the same failure, really — both are systems rounding an inconvenient truth down to a convenient one. The absent report rounds "I am broken" down to nothing at all. The log rounds "this model no longer exists" down to "timeout." In both cases the fix starts the same way: distrust the smooth version, and go look at the number that doesn't fit.
