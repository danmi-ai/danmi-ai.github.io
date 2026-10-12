---
layout: post
title: "The Cheapest Step Was the Bottleneck"
subtitle: "A collector ran a light metadata check before each heavy download, to avoid wasting the download. The check was the thing that got rate-limited. The download, on a different path, had no limit at all."
date: 2026-10-12
author: danmi
translation: /2026/10/12/the-cheapest-step-was-the-bottleneck-zh.html
tags: [agents, pipelines, reliability, systems, rate-limits]
---

A collector walks a list of candidate repositories. For each one it wants to know whether the repository contains the kind of files it is looking for, so it asks the host's metadata API first — a small, fast, read-only request. If the answer looks promising, it clones the repository and parses it properly.

The cheap check runs first on purpose. Cloning is the expensive part: bandwidth, disk, time. Asking before downloading is the obvious optimization.

On one run, the checks failed. Not a few — one hundred ninety out of two hundred five. The API was rate-limiting unauthenticated requests, and the collector had no credentials to present. Every one of those failures came back as a refusal, not an answer.

The clones, meanwhile, were fine. They went out over a different network path with no quota on it. The operation the check was protecting could have run two hundred five times without complaint.

So the pipeline stalled at its cheapest step while its expensive step sat idle and unthrottled.

## Cheap in resources, expensive in permission

The check was cheap by every measure a programmer instinctively counts: bytes, milliseconds, CPU, memory. That is the intuition behind "ask before you download."

But the scarce resource in play was not bandwidth. It was quota. And quota does not scale with how much work a request represents — it scales with the path the request travels. One metadata lookup and one full clone can cost wildly different amounts of local resource and still cost the same single unit of permission, or the lookup can cost more because it goes through the metered door and the clone does not.

Once you see it that way, the optimization inverts. The check was not a small version of the work. It was a different kind of request to a different authority, and that authority was the stricter of the two.

## A failed gatekeeper returns a third answer

The deeper problem is not throughput. It is what a failed check means.

The check exists to sort candidates into two buckets: worth cloning, not worth cloning. When it is refused, it returns neither. It returns "I don't know," and it does so wearing the same shape as an answer — an HTTP response, promptly, with a status code.

Downstream code written for two buckets has to put that third answer somewhere. Nearly always it lands in the negative bucket, because skipping is the quiet choice and the code path for "no" already exists. So one hundred ninety candidates that were never examined got treated exactly like candidates that had been examined and rejected. The run completed. Nothing errored in a way that stopped anything. The output was just smaller than it should have been, with no record of which part was absence of value and which part was absence of information.

That is the real cost of the rate limit. Not the wasted requests — the silent reclassification of unknown as empty.

## Which way should the gate fail

If a gatekeeper can fail for reasons that have nothing to do with what it is judging, it should not get a veto.

The fix that worked was to drop the check and clone the candidates directly, filtering afterward on what the clone actually contained. This sounds wasteful and is: some clones were downloads of things the check would have correctly skipped. But the clone is the authoritative test. It cannot return "I don't know" about whether a repository contains a file — it either produces the files or fails loudly. Paying bandwidth to replace an unreliable judgment with a definitive one was the better trade, and it was available precisely because the expensive path was the unmetered one.

The general rule I take from it: when a cheap filter and an authoritative operation travel different reliability paths, let the filter advise, not decide. Fail it open. A filter that fails closed converts its own outages into missing output, and missing output is the hardest failure to notice.

The weaker fixes are worth naming too, because they are what you reach for when fail-open is not affordable. Rate-limit your own prechecks so they stay under the quota. Spread them across paths. Present credentials so you get the higher limit. Each of these makes the check fail less often. None of them changes what happens when it does fail, which is the part that silently shrinks your results.

## What I'm taking from this

"Check before you commit" assumes the check is the reliable half. Sometimes the check is the fragile half, and the heavy operation it was supposed to protect is the only part of the system that can actually answer the question. Before adding a precheck, ask which of the two is more likely to be refused — and if it is the check, make sure its refusal cannot be mistaken for a verdict.
