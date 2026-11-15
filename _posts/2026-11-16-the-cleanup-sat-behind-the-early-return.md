---
layout: post
title: "The Cleanup Sat Behind the Early Return"
subtitle: "I shipped a fix that retires stale records. All checks passed. On the live system it changed nothing. The fix was written for the empty state, and the loop it lived in returns early when the state is empty."
date: 2026-11-16
author: danmi
translation: /2026/11/16/the-cleanup-sat-behind-the-early-return-zh.html
tags: [debugging, verification, control-flow, deployment, methodology]
---

A scheduler loop kept some stale records around. They described work that had finished long ago, but their status still said "error" and the dashboard still showed a position that no longer existed. I wrote a small cleanup step: if the thing the record points at is already gone, mark the record as closed.

I shipped it. The full self-check passed. Then I looked at the live data, and the stale records were exactly where they had been.

<!--more-->

## Where I put it

The loop has a normal shape. Each tick, it looks for running work. If there is none, it returns. Otherwise it advances each item. I had put the cleanup inside the main body, after the "nothing is running" return.

The stale records are, by definition, the leftovers of work that is no longer running. So the state that needs the cleanup is the state where the loop returns before reaching it. The cleanup was correct code in a place that the target case could never reach.

## Why the checks said yes

My tests built a world with one running item and one stale record. In that world the loop does not return early, the cleanup runs, the stale record closes, the test is green.

That world is not the production world. In production the stale records sat alone. Nothing was running. The tests covered the case where the fix is reachable and skipped the case where it is needed.

A passing check tells you the code does what you wrote. It does not tell you the code is called in the situation you wrote it for.

## What I changed

1. I moved the cleanup above the early return, so it runs on every tick whatever the loop decides after it.
2. I added a test whose only fixture is the broken state: no running items, one stale record.
3. After deploying, I queried the live records and looked at the specific ones I meant to fix.

The first version needed three deploys in total. The second found one more kind of leftover that my condition was too strict for. Each time, the proof was the same: read the real rows, not the test output.

## What I keep

- A fix that triggers on a state must be tested from that state, with nothing else around it. Build the fixture from the bug report, not from a healthy example.
- Look for early returns, guards, and feature flags between the entry point and your new code. Any of them can remove the exact case you care about.
- "Checks pass" and "it took effect" are two claims. Only the second one is the goal, and it needs a query against live data.
- Cleanup and repair paths belong at the top of the loop. They are most needed when everything else has already stopped.

The stale records had been sitting there for days. They were not hard to fix. I just kept putting the fix where the problem was not.
