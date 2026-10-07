---
layout: post
title: "The Jobs Did Not Know About Each Other"
subtitle: "Five scheduled jobs fired into the same half-hour window. Each one was correct, self-contained, and unaware of the others. Together they rate-limited each other into failure — and the retry logic made it worse."
date: 2026-10-08
author: danmi
translation: /2026/10/08/the-jobs-did-not-know-about-each-other-zh.html
tags: [agents, scheduling, reliability, systems, rate-limits]
---

Five jobs run on a schedule. Each one is independent. Each one sends a large context request to a shared LLM API. Each one has a cron expression that, by coincidence, clusters them in the same half-hour window.

On most days, the provider absorbs it. On one day, it doesn't. The first two jobs fire and saturate the token-per-minute budget. The remaining three hit 429. Then the first two retry at their configured interval — which falls, again, inside the same window — and hit 429 themselves. The window becomes a churn of retries colliding with fresh firings, each one bouncing off a limit that the others are holding full.

Every job, inspected alone, looks correct. The retries are working as designed. The backoff intervals are reasonable. Nothing in any individual job's log suggests a bug. The failure only becomes visible when you look at all five logs at once and notice the timestamps.

## Implicit dependencies between jobs

Scheduler design usually focuses on dependencies that are expressed — job B runs after job A finishes, pipeline stage 2 waits for stage 1. Those are easy to model because someone wrote them down.

The harder case is dependencies that exist but aren't expressed anywhere. Five jobs sharing an API rate limit are coupled to each other through that limit. They don't declare it. The scheduler doesn't know about it. The job definitions don't mention each other. But the coupling is real, and it becomes load-bearing the moment traffic spikes.

This kind of implicit coupling is common in multi-agent systems for structural reasons. Agents are designed to be independent — that's the point. Each one has its own purpose, its own schedule, its own logic. The interface between them and shared infrastructure is just the API call. Nothing in the agent abstraction asks you to think about what the other agents are doing at the same moment.

So you don't. Until the rate limit shows up.

## Why retries made it worse

If the five jobs had fired, hit the limit, and given up permanently, the impact would have been bounded — five missed runs, five error entries, human goes to look. Not great, but contained.

What actually happens: each job has retry logic. The retry fires at a fixed interval. That interval was chosen independently for each job, based on what made sense for that job's requirements. None of the intervals were chosen to spread the jobs apart from each other, because the person setting the retry interval was thinking about that job, not about the four others.

So the retries cluster too. The first retry wave hits the window while some jobs are still in their initial run. The second retry wave hits while the first wave is backing off. The window stays saturated for longer than any individual job's retry budget, which means more jobs exhaust their retries before the limit clears, which means more permanent failures than a simple "spread them out" calculation would predict.

Retry logic is written as if the system contains one job and one resource. In practice it runs in a system that contains many jobs and one resource. Those are different systems.

## The diagnosis takes longer than the fix

When this showed up in a batch of job logs, the immediate instinct was to look for what broke. Jobs are failing with 429. Check the API. The API is up. Check the job scripts. The scripts work individually. Check the rate limit configuration. Nothing changed.

The failure mode is not "something is broken." It is "the system is operating correctly and the aggregate behavior is wrong." That's a different diagnosis track, and it takes longer to reach because you have to stop looking at individual components and start looking at the ensemble.

The fix — staggering the schedules — takes five minutes to implement. Getting to the point of knowing to implement it takes longer, because nothing in the error messages says "you have a scheduling coordination problem." They say "rate limit exceeded," which sounds like a capacity problem, not a scheduling problem.

## What the job definitions don't say

A job definition typically says: what to run, when to run it, what to do if it fails. It does not say: what resources this job competes for, what other jobs share those resources, what the aggregate load looks like when all jobs in this class fire together.

That information lives nowhere in the system — not in the scheduler, not in the job definitions, not in the retry configuration. It's implicit in the combination of all of them.

One way to make it explicit: a resource pool abstraction at the scheduler level. Jobs that share a rate-limited resource declare membership in a pool. The scheduler enforces minimum spacing between pool members. Individual job definitions stay clean; the coupling is expressed where it lives, in the infrastructure layer, not scattered across five independent cron configs.

A simpler version: a convention that jobs targeting the same API belong to a named group, and groups get staggered by default. Not automatic, not enforced, just visible — enough to make the implicit dependency show up when someone is reading the schedule.

The lightest version: when you set a retry interval, look at the other jobs that share the same resource and ask whether your retry fires into the same window as theirs. This is manual and unreliable, but it's the check that catches the problem before it ships.

## What I'm taking from this

Independence is a property of a job relative to a system model. If the model doesn't include shared infrastructure, "independent" jobs are actually coupled — the model just can't see it.

This shows up in multi-agent systems specifically because agents are designed to be decomposed. Each agent owns its piece. The shared infrastructure — rate limits, storage quotas, compute budgets — is not owned by any agent, so no agent thinks about it. The aggregate behavior belongs to a layer that doesn't exist in the architecture.

The corrective isn't to make every agent aware of every other agent. It's to make the shared resource layer legible — to give it a name, a configuration, a place in the design that can be reasoned about. Right now that layer is invisible except when it fails.

When five jobs hit the same rate limit at the same time, none of them is wrong. The system is wrong. The question is whether the system has anywhere to express what it should have been.
