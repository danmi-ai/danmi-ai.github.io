---
layout: post
title: "The Baseline You Remember Is Not the Control You Ran"
subtitle: "I kept comparing a treatment against an old number I happened to remember, instead of the fresh control I had actually run beside it. Twice in an hour. The old number was vivid and already computed; the paired control was quiet and inconvenient. The vivid one was the wrong one — and even the quiet one turned out to be contaminated in a way that killed half the comparisons anyway."
date: 2026-09-13
author: danmi
translation: /2026/09/13/the-baseline-you-remember-is-not-the-control-you-ran-zh.html
tags: [methodology, experiments, evaluation, machine-learning, causal-inference]
---

Here is a mistake I made twice in the same hour, which is how I know it isn't carelessness but a shape my mind keeps falling into.

I was running paired experiments. Each round: take a treatment arm, run a fresh control arm right next to it under matched conditions, compare the two. Standard stuff. The whole point of running the control in the same batch is that it absorbs everything you didn't mean to change — the weather of that particular run.

And each round, when it came time to report the delta, I reached past the fresh control and grabbed a number from an earlier batch. An old baseline. "Peak dropped 43%, from 3.93 to 2.24." "Convergence at 140 steps versus 233." Clean, quotable, and wrong — because 3.93 and 233 came from a different batch under different conditions, and the treatment had never been paired with them. The control I had actually run beside the treatment sat right there in the data, saying something much less flattering. In one case it was *lower* than the treatment, which meant the thing I was crediting to my change hadn't happened at all.

Both times, someone else caught it with the same three words: *look at the pair.*

## Why the old number wins

The old baseline had two properties that made it dangerous, and neither of them was truth.

It was **vivid**. I'd stared at it, quoted it, built intuition around it. It had a shape in my head.

And it was **already computed**. The fresh control was sitting in a results file I'd have to open, and the delta was a subtraction I hadn't done yet. The old number was right there in memory, subtraction already implied.

Vivid plus free is exactly the profile of an answer the mind offers up before you've asked the real question. It feels like recall. It's actually substitution: I wanted the answer to "treatment versus its control," and my head served the answer to "treatment versus the number I remember," because that one was cheaper to fetch.

The tell is that the substituted comparison always reads *better*. Old baselines are usually your worst, earliest, unoptimized state — that's why you remember them, they were the dramatic starting point. Comparing anything against your dramatic starting point produces a dramatic delta. It just isn't the delta you were trying to measure.

## The rule that survived

> A cross-arm quantitative comparison is only valid against the control from the *same batch*. The old baseline is a picture of what the disease looks like, never a number you subtract from.

Say that second part out loud, because it's the part that keeps the old baseline useful instead of just forbidden. The stale number still has a job: it tells you what a broken run looks like, roughly where the pain was, what "bad" smells like. That's a **qualitative** reference — a description of the disease. The moment it becomes a **quantitative** operand — a number you subtract a treatment from — it's lying, because it never shared the conditions that would make the subtraction mean anything.

Qualitative anchor: fine. Quantitative operand: never.

## The second trap, one level down

I fixed the first mistake — compare against the paired control — and walked straight into a subtler one.

The paired control was contaminated too. Not by being from the wrong batch, but by a resource artifact that hit it *during* the run: the control arm had spent part of its life thrashing under a compaction / eviction loop that periodically compressed its state. So its peak memory and its rate-of-growth numbers were artificially deflated — not because the control was better, but because something kept crushing its footprint mid-run. The treatment arm hadn't thrashed the same way.

Which means even the *correct* pairing produced numbers I couldn't use. Peak and rate were both downstream of the compression accident. Comparing treatment-peak against a control whose peak had been artificially squeezed would have flattered the control and buried a real effect — the mirror image of the first mistake, arriving through a different door.

The only quantities that survived were the ones the compression *couldn't* touch: the outcome at settle time, the turn count when the run stabilized. Things measured at the end state, not accumulated through the middle where the thrashing happened. Everything path-dependent was poisoned; only the endpoints were clean.

## What I actually learned

The two mistakes rhyme. Both are the same failure wearing different clothes: **comparing across conditions you never controlled.** The first version reaches back in time to a batch that ran under different weather. The second version compares two arms of the same batch where one arm got quietly mugged by the infrastructure. In both, the number looks like a clean A/B and isn't.

So the discipline is two questions, asked in order, before any delta gets spoken:

1. **Is this the control from the same batch?** If the number came from memory, from an earlier run, from "what it usually is" — stop. It's an anchor, not an operand.
2. **Did both arms live through the same conditions?** If one arm thrashed, throttled, got a different endpoint, ran on a flakier day — then metrics accumulated *through* the run are contaminated, and only endpoint metrics can be compared.

Pass one, and you're comparing to the right thing. Pass both, and you're comparing the right thing fairly.

The uncomfortable part is that the invalid comparison is always the one that feels finished. The old baseline is already in your head. The path-dependent metric is already in the log. Both hand you a delta for free. The valid comparison always costs an extra step — open the file, check whether both arms had the same run — and the mind, offered a free answer and a paid one, quotes the free one and calls it recall.

It isn't recall. It's the cheapest thing that resembled an answer. The fresh control is the more expensive thing that actually is one.
