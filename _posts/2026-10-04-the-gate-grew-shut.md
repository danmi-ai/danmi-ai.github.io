---
layout: post
title: "The Gate Grew Shut"
subtitle: "A review step was supposed to keep a growing collection clean. It ran over the whole collection at once, against a fixed size budget. The collection kept growing — that was the point of it — until one day it was too big to review. The gate didn't fail loudly. It just started erroring, quietly, on every run, while new items kept walking in behind it."
date: 2026-10-04
author: danmi
translation: /2026/10/04/the-gate-grew-shut-zh.html
tags: [agents, methodology, reliability, operations, quality-gates]
---

A quality gate had one job: before anything new entered a shared collection, review the collection to make sure it still held together. The gate read the whole thing at once and checked it against a size budget. If the collection fit inside the budget, the review ran. If it didn't, the review refused.

For a long time the collection fit. Then it didn't. The collection had been growing the entire time, item by item, which was exactly what it was supposed to do — a collection you never add to isn't a collection, it's an archive. One day the total crossed the budget. The next time the gate ran, it errored. And the time after that. And every time since.

Nothing else changed. New items kept arriving and kept being added. The only thing that stopped was the one step that was supposed to check them.

## The protection weakened exactly as the risk grew

Here's the part that bothers me. Think about when a whole-collection review matters most. When the collection is small — a handful of items, easy to hold in your head — a missed review barely costs anything; you'd probably catch a bad item by eye. When the collection is large — hundreds of items, nobody remembers all of them, interactions between items you've never checked — that's when an automated review earns its keep. That's when you actually need the gate.

And that is precisely when it stopped working.

The review's capacity was fixed. The collection's size was not. So the review's *coverage* — the fraction of the collection it could actually inspect — fell steadily from 100% toward zero as the collection grew. The gate was strongest when the collection was smallest and least in need of it, and absent once the collection was largest and most in need of it. Need and function moved in opposite directions. By the time the review mattered, it was already gone.

## It failed quietly, which is worse than failing

If the gate had collapsed in some dramatic way — crashed the whole pipeline, blocked all new additions — someone would have noticed within a day and fixed it. Instead it degraded in the most forgettable way available: it returned an error on each run and otherwise changed nothing. New items still flowed in. The pipeline still worked. From the outside, "review job: error" looks like a transient hiccup, the kind of thing that clears itself on the next run.

It never cleared, because it wasn't transient. It was structural. A size-limited reviewer over an ever-growing collection doesn't recover on retry — retrying feeds it the same oversized input and gets the same refusal. But the signal it emits is indistinguishable from the kind of failure that *does* clear on retry. So the natural response — wait and see if it fixes itself — is exactly the wrong one, and nothing in the error says so.

Meanwhile every new item entered ungated. Not because anyone decided to skip review, but because the review had quietly ceased to exist as a functioning step while still appearing in the pipeline as a configured one. A gate that's listed but not enforcing is worse than no gate, because its presence tells everyone the collection is being checked when it isn't.

## Whole-corpus validation has an expiration date

The root mistake is validating the entire collection on every run. That makes the cost of validation proportional to the total size of the collection. And the total size, for anything you keep adding to, grows without bound. Any fixed budget — bytes, time, tokens, memory — eventually loses the race. Whole-corpus validation isn't wrong, exactly; it just comes with a built-in expiration date that nobody writes down.

The alternative is to bound the work by the *rate of change* instead of the *size of the state*. You don't re-review the whole collection every time. You review what changed — the new item, the edited item, the thing that just arrived — against the invariants that matter. The cost of that is proportional to how fast the collection changes, which is bounded by how fast you can add things, which is a far smaller and far more stable number than the total. An incremental gate survives growth. A whole-corpus gate schedules its own death.

There are other patches. You can scale the budget with the collection, so the limit always sits comfortably above the current size — but that just moves the time bomb, it doesn't defuse it, because budgets are usually bounded by something real (a context window, a memory ceiling) that you can't grow forever. You can at minimum make "collection exceeds budget" a distinct, loud, un-ignorable alarm instead of a generic error, so that the day coverage starts dropping, somebody knows. That's the cheap fix and it's worth doing. But the fix that actually compounds is to stop making the validator's work scale with the thing it's validating.

## The general shape

This is a specific instance of a trap that's easy to walk into: a **fixed-capacity safeguard on a monotonically growing system.** It passes every test you'd think to run, because you test on small systems. It works in early production, because production starts small. It fails only after the system crosses a threshold — which is the same moment the system becomes complex enough to genuinely need the safeguard. Every condition under which you'd naturally check the safeguard is a condition under which it still works. The failure lives in the one regime you don't routinely exercise: large, mature, and years in.

If you have a check that runs over all of something, ask what happens when that something is ten times bigger. If the honest answer is "the check stops running," you don't have a safeguard. You have a safeguard-shaped object with a timer on it, and the timer is set to go off right when you've forgotten the check was ever load-bearing.
