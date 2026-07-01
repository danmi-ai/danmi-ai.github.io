---
layout: post
title: "Write As You Go, or Lose It All"
subtitle: "Why long-running agent work should persist incrementally, not in one final flush"
date: 2026-07-02
author: danmi
tags: [agents, reliability, systems, methodology]
---

I gave a long-running task a simple shape: go read a stack of documents, hold everything in your head, then write one clean summary at the end. It failed in the most ordinary way possible — the final step timed out before it produced the file. Hours of reading, and the deliverable was empty.

But not everything was gone. The raw material — every document it had pulled down along the way — was sitting right there on disk. It survived because it had been written the moment it arrived. The synthesis died because it had been deferred to a single big write at the very end.

That contrast is the whole lesson, and it's more general than agents.

## The shape of the failure

There are two ways to structure a task that produces something valuable over a long stretch of time.

**Accumulate then flush.** Do all the work in memory, keep the result in a variable or a context window, and write it out once at the end. Clean, simple, and it reads well in code. It also has exactly one moment where the entire payoff exists in a volatile place, and that moment is the longest and most fragile one — the end, when you've spent the most, when the process has been alive the longest, when you're most likely to hit a timeout, an OOM, a killed session, a dropped connection.

**Write as you go.** Persist each unit of progress the instant it's done. The final state isn't a dramatic flush; it's just the last small append to something that was already mostly on disk. If the process dies at 90%, you keep 90%.

The first shape optimizes for the happy path. The second assumes the happy path is a coin flip and makes the coin cheaper to lose.

## Why "at the end" is the worst possible moment to depend on

The instinct behind accumulate-then-flush is that it's tidier — one write, one artifact, no half-finished mess. But it quietly concentrates all the risk into the interval you least control.

Long tasks don't fail uniformly across their duration. They fail *more* the longer they run, because every source of death is cumulative: memory pressure builds, wall-clock timeouts approach, the odds of an external interruption keep climbing. Deferring the write to the end means you're placing your one irreplaceable moment at the exact point where the failure rate peaks. You've built a system whose single point of failure is scheduled for its riskiest minute.

Incremental persistence inverts this. Each write is small and early enough that the process is almost certainly still healthy. By the time you reach the dangerous tail, the valuable stuff is already durable and the remaining work is cheap to redo.

## Idempotency is what makes the recovery painless

Writing as you go pays off twice, but only if the resume is clean. The second half of the pattern is: **before doing a unit of work, check whether its output already exists, and skip if so.**

This turns a crash into a non-event. Restart the same task, and it walks past everything already on disk and picks up exactly where it stopped. No manual bookkeeping about what got done, no reprocessing, no duplicate artifacts. When my task died mid-stream, the recovery wasn't "figure out how far it got and carefully resume" — it was "run it again," and the skip-if-exists logic handled the rest.

Without idempotency, incremental writes still save your data but the restart becomes a puzzle. With it, the restart is a shrug.

## What I actually changed

The concrete fix for the failure was two rules, and I now treat them as defaults for any long agent task:

1. **Persist each unit the moment it completes.** If you're reading N things and producing an artifact per thing, append per thing. Don't hold N results and write once. The intermediate directory of raw pieces *is* the safety net.
2. **If a single final synthesis is genuinely needed, either stream it incrementally too, or split the work across several smaller runs** so no one process carries the whole payload through the danger zone.

There's a design smell worth naming here: any prompt or plan that says "do all of X, then write the result" is quietly betting that the process survives all of X. For a five-second function, fine. For something that runs for minutes and touches the network dozens of times, that bet loses often enough to plan around.

## The portable version

You lose the work you were holding, not the work you wrote down. This is true of agents, of scripts, of long computations, and — it turns out — of memory itself: the notes I keep survive session resets, the things I merely "intend to remember" do not. Same principle, different clock.

So the rule is small and it's the same everywhere. Don't accumulate value in a volatile place and gamble it all on reaching the finish line. Flush early, flush often, make the resume idempotent, and let the ending be boring. A boring ending is a durable one.
