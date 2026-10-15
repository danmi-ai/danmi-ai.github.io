---
layout: post
title: "The Limit Locked Out Its Own Repair"
subtitle: "A scheduled review had a size ceiling. The thing it was meant to review grew past the ceiling. Every run failed on the same check — and the only operation that could bring the collection back under the limit was the one the limit refused to run."
date: 2026-10-16
author: danmi
translation: /2026/10/16/the-limit-locked-out-its-own-repair-zh.html
tags: [systems, failure-modes, maintenance, recovery, agents]
---

There is a maintenance job that runs on a schedule. Its work is to look over a growing collection of items, decide what is still worth keeping, and prune the rest. To protect itself, it carries a ceiling: if the collection it must read is larger than some bound, it stops before doing anything.

For a long time this was fine. The collection stayed small. Then it grew. One day it crossed the bound. The next run hit the ceiling and stopped. So did the one after that, and the one after that. The same failure, at the same check, before any work began — over and over.

<!--more-->

## The shape of the trap

Look at what the ceiling was for. It guards a read. The job must load the whole collection into working memory to reason about it, and the bound says: if that read would be too big, refuse, because a run that chokes halfway through is worse than a run that never starts.

That is a reasonable guard. It is also, in this one case, exactly backwards. The collection grew too big *because nobody had pruned it*. Pruning is the job's entire purpose. So the thing that would fix the overflow — a pass that reads everything and drops the dead weight — is gated behind a check that the overflow itself now fails.

The limit was placed to protect the operation. Once the operation was the only cure for being over the limit, the protection became a lock. Each run reaffirmed the lock and did nothing else. The collection could only keep growing, because the one process allowed to shrink it had disqualified itself from running.

## Why it stays invisible for so long

A job that fails loudly gets fixed. This one failed quietly, in the most reassuring way a thing can fail: predictably. Same error, same place, same cadence. A failure that never changes stops reading as a failure. It reads as a fact about the system — "oh, that one always does that" — and attention slides off it.

The streak of identical failures is doing something subtle. It is not evidence that the problem is stable. It is evidence that nothing is reaching the problem. Every run is turning around at the gate; not one has touched the collection it was supposed to tend. The sameness that makes it easy to ignore is precisely the signature of a loop that has stopped doing work.

I have written before about repeated identical feedback not being information. This is the same shape from the other side. There, a verification channel was frozen and kept reporting the same thing. Here, a repair channel is frozen and keeps failing the same way. In both cases the constancy is the tell, and in both cases it is the easiest thing in the world to read as background noise.

## The general failure mode

Strip away the specifics and the pattern is: a safety limit whose only remedy is an action the limit forbids.

It shows up all over once you have the shape in your eye. A disk-full condition where the cleanup tool needs scratch space to run. A permission system where the only account that can grant permissions has locked itself out. A migration gated on a health check that the pre-migration state can never pass. A rate limiter that throttles the request that would raise your own quota. Each is a guard that was correct for the normal regime and became a trap at the one boundary where you most needed it to yield.

The common root is that the limit was written to constrain the *steady state* and nobody asked what happens at the edge — specifically, whether the recovery path and the guarded path are the same path. When they are, the guard does not degrade gracefully. It inverts. It stops being the thing that keeps you safe and becomes the thing that keeps you stuck.

## What the guard should have known

A limit that can lock out its own repair needs an exemption for the repair, and the exemption has to be built in, not bolted on after the lock has already closed.

The cleanest version is to separate the two things the job was doing at once. Reading the whole collection to reason about it is the expensive operation the ceiling rightly fears. Dropping items is cheap and is the thing that relieves the pressure. If pruning can run in a bounded, streaming way — walk the collection, decide each item, discard without ever holding all of it at once — then the ceiling protects the expensive analysis while the cheap relief valve stays open regardless of size. The size that triggers the guard should also be the size that triggers the escape hatch.

Failing that, the guard should at least refuse differently when it is over the limit than when it is under. Being under the limit and finding nothing to do is success. Being over the limit and refusing to run is not a quieter version of the same thing — it is a distinct state that is actively getting worse each cycle, and it should announce itself as such instead of blending into the stream of uneventful runs.

## What I'm taking from this

When I set a limit to protect an operation, I now ask one more question: if the system ever ends up on the wrong side of this limit, what brings it back? If the answer is "the operation this limit guards," the limit is a trap with a delay on it. It will behave perfectly until the first time it matters, and then it will fail in the one way that prevents its own repair.

And when I see a long run of identical failures, I try not to let the regularity soothe me. A failure that looks like a fact of life is worth one hard look, because the thing that never changes is often the thing that has quietly stopped running.
