---
layout: post
title: "Deterministic Is Not the Same as Data-Caused"
subtitle: "A job that hangs at the exact same step every time feels like proof of a poisoned record at that position. But a clean input, replayed the same way, can drive a system into the same fragile corner every time — and that is a different bug entirely."
date: 2026-07-26
author: danmi
translation: /2026/07/26/deterministic-is-not-data-zh.html
tags: [debugging, distributed-training, determinism, methodology, systems]
---

A long training run froze. Not randomly — it froze at the same step number, run after run, resume after resume. You could kill it, restart from a checkpoint, fast-forward back to that step, and watch it stop again at exactly the same place. The GPUs pinned at 100%, no error, no progress. Six times in a row, the same step.

When something is that reproducible, the mind jumps to one explanation immediately: there must be a bad record sitting at that position in the data stream. A malformed sample, an out-of-range token, a length that overflows some buffer. Determinism looks like a signature, and the signature points straight at the input. So you go hunting for the poisoned example.

That instinct is right often enough to be dangerous. And this time it was wrong.

## The trap in the word "deterministic"

"It happens at exactly the same step every time" carries a hidden inference: *therefore something at that step is the cause.* But that inference smuggles in an assumption — that the only thing which is the same at that step is the data. In a stateless pipeline that would be true. In a system that carries learned state, it is not.

A model partway through training is not a fixed function. Its weights at step N are a product of every step before it. Feed it the same batch at step N and it will react the way step-N weights react — which is not how step-zero weights would have reacted to the identical bytes. The *input* is deterministic. The *model's response to it* is also deterministic. But the response is a property of the accumulated training, not of the batch.

So "same step, every time" has two possible readings that look identical from the outside:

1. There is a bad record at that position in the data. (Data bug.)
2. There is a perfectly clean record at that position, and the model — having learned something specific by that step — reacts to it in a way that trips a fragile code path. (Interaction bug.)

Both produce a deterministic hang. Both survive resume. Both point a giant arrow at "step N." Only one of them is fixed by touching the data.

## Prove the input is clean, and the map changes

The only way to tell the two apart is to stop reasoning about the symptom and look at the thing everyone is accusing: the input at that step. Not "does it look plausible" — actually dump it and check the properties that could plausibly break something.

So I captured the exact batch fed at the frozen step, from every parallel worker, and asked the boring questions. Are the token counts consistent across workers, or does one worker see a different amount of data than the others? Are all the token IDs inside the vocabulary, or is something out of range? Are the sequence lengths in a sane distribution, or is there a degenerate zero-length or gigantic outlier? Is the padding rate normal?

Everything came back clean. Token counts identical across every worker — which, on its own, ruled out a whole class of "workers disagree about how much data there is" failures. IDs all in range. Lengths normal. Padding negligible. The record everyone wanted to blame was, on inspection, unremarkable.

That single result flips the entire investigation. Before the dump, the space of explanations was dominated by "find the bad data." After the dump, "find the bad data" is *closed* — and what's left is the reading nobody wanted: the input is fine, and the failure lives in how the system responds to a fine input.

## Why the interaction bug is the harder one

Here's the shape of what was actually happening, described generically because the specifics don't matter to the lesson. In a sparse layer — the kind where different parts of the network specialize and each token gets routed to a subset of them — the routing is *learned*. Early in training the routing is close to uniform; every specialist gets roughly its share of work. As training proceeds, the routing sharpens. Specialists get opinionated. And at some step, for some particular clean batch, the learned routing sends *zero* tokens to one of the specialists.

Downstream, a collective communication step assumes every participant has something to exchange. Hand it a zero-sized, wildly-imbalanced exchange and it can deadlock. Not because the data was bad — because the *learned distribution of work*, applied to a legitimate batch, produced an edge case the communication path never handled.

That is why it is deterministic without being a data bug. The same clean bytes, run through the same trained weights, produce the same routing, hit the same zero-token corner, deadlock the same collective. The determinism is real. The cause is upstream of the data, in the accumulated state, and downstream of it, in a fragile system path — and the data itself is just the innocent trigger sitting in the middle.

These bugs are worse than data bugs precisely because the fix is not "drop the record." You can't delete your way out of it. The record is fine and the next clean record might trip it too. The fix has to change the *system*: make the fragile path tolerate the edge case, or change the mechanism so the edge case can't arise, or add slack so an imbalanced exchange doesn't deadlock. That is a much bigger surface than swapping one line of a data file.

## The general move

Strip away the domain and the procedure is portable to any stateful system that fails reproducibly:

**A reproducible failure tells you the trigger is deterministic. It does not tell you the trigger is the cause.** Anything with accumulated state — a training run, a cache that fills predictably, a connection pool that exhausts on the same request pattern, a scheduler that always wedges under the same load — can fail the same way every time for reasons that have nothing to do with the input being malformed.

The discriminating experiment is almost always the same: **isolate and inspect the accused input, and verify it against the properties that would actually explain the failure.** If the input is dirty, you have a data bug and a cheap fix. If the input is clean, you have just done something more valuable than finding a bug — you have *eliminated an entire branch of the search tree*, and forced the investigation onto the harder-but-correct ground of state-and-system interaction.

The temptation is to skip the dump because the answer feels obvious. Same step every time — it *has* to be the data. But "obvious" is exactly when the cheap check pays for itself, because the cost of being wrong is days of hunting for a poisoned record that was never there. Fifteen minutes of dumping the actual batch is not slower than a week of blaming the innocent.

Determinism is a clue. It is not a verdict. The verdict comes from looking.
