---
layout: post
title: "The Timer Fired. The Job Never Finished."
subtitle: "A recurring job kept failing, and the schedule looked perfectly healthy the whole time. The tick fired on time, every time. What it was firing was a multi-day task, and the tick had a few-minute timeout — so every run started the work from scratch, ran until the clock cut it off, and died. Zero progress, forever, behind a green schedule."
date: 2026-09-21
author: danmi
translation: /2026/09/21/the-timer-fired-the-job-never-finished-zh.html
tags: [methodology, systems, reliability, scheduling, debugging]
---

There was a job set to run every few minutes. Its purpose was to keep a long batch task moving along — the kind of task that, once started, takes days to finish. The job had been "running" for a while, and it kept failing. Not crashing loudly. Failing quietly, on a timer, over and over.

The schedule looked fine. That was the trap. The tick fired exactly when it was supposed to. If you glanced at the run history you saw a tidy column of entries, one every few minutes, marching down the page like a healthy heartbeat. The thing that was broken did not show up in the one place I was looking.

## The arithmetic that couldn't work

Here is what was actually happening, once I stopped reading the schedule and looked at what a single tick tried to do.

Each tick started the batch task and then sat there, inside the task, running it. But the tick had a timeout — a few minutes, the sane default for a recurring job that's not supposed to hang. And the task needed *days*. So the sequence was always the same: fire, start the work, run for a few minutes, hit the timeout, get killed mid-stride. Next tick: fire, start the work *from the beginning again*, run for a few minutes, get killed. Forever.

The task never got more than a few minutes into a multi-day job before the very thing scheduling it turned around and killed it. It wasn't slow. It wasn't stuck. It was being executed and executed by something structurally incapable of letting it finish. A bounded timer had been wrapped around an unbounded task, and a bounded interval can only ever contain bounded work. The mismatch wasn't a bug in the task or a bug in the timeout. It was a category error about what the tick was *for*.

## The green schedule is the decoy

The reason this ran for a while before anyone caught it is worth sitting with, because it generalizes.

The schedule measured the wrong thing. "Did the tick fire on time?" — yes, always. That question has a satisfying, green, always-yes answer, and it is not the question you care about. The question you care about is "did the work make progress?", and nothing on the schedule view was even trying to answer that. Completion was never what the tick tracked, so the tick's health said nothing about the work's health. It just looked like it did.

This is a specific flavor of a mistake I keep meeting: a system reports confidently on a metric adjacent to the one that matters, and the adjacency is close enough that you accept the healthy signal as proof the real thing is healthy too. Fired-on-time stood in for made-progress the same way exit-code-zero stands in for the-work-happened, or a-balanced-ledger stands in for nothing-was-lost. The report is green because the report was built to answer an easier question.

## The fix is to stop the tick from doing the work

The repair wasn't to lengthen the timeout — a job that takes days doesn't want a days-long tick, that's just moving the category error somewhere more expensive. The repair was to change what the tick *is*.

A recurring tick should be a supervisor, not a laborer. Its whole job is: check whether the work is alive; if it's dead, launch it *detached* — outside the tick's own lifetime and timeout — and then exit immediately. The tick fires, spends a second confirming a process is running, relaunches it if it isn't, and gets out of the way. The long work runs on its own, unbounded, not inside any single tick. Now the timeout is honest: it bounds the supervisor, which really is a few-seconds job, and it stops bounding the work, which was never supposed to be bounded.

Once you draw it that way the old design looks obviously wrong. The tick had been both the thing that decides *when* and the thing that does the *work*, and those two have completely different natural durations. The decider is instantaneous. The work is long. Fusing them forces the long thing to live inside the short thing's clock, and the short thing always wins.

## The rule I took out of it

Two, actually.

When a periodic job manages a task that can outlast one period, don't let the tick run the task. Make the tick a supervisor: detect, launch-if-dead, detach, exit. The recurring thing owns *when*; a separate, unbounded thing owns *the work*. If your tick's timeout is shorter than the task can ever finish in, the timeout isn't a safety limit, it's a guillotine on a schedule.

And when a scheduled thing keeps failing, don't trust the schedule to tell you why. The schedule answers "did it fire," and that answer will look healthy right up to the horizon. Go look at whether the work moved. A heartbeat proves the clock is alive. It does not prove anything downstream of the clock is.
