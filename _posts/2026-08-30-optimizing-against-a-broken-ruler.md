---
layout: post
title: "Optimizing Against a Broken Ruler"
subtitle: "I had a judge that agreed with the truth about half the time. My instinct was: bad, but it's a signal — better than nothing, we'll improve as we go. Then I noticed the plan was to put it inside a loop. Measuring with a bad ruler survives the noise. Optimizing against one climbs it."
date: 2026-08-30
author: danmi
lang: en
translation: /2026/08/30/optimizing-against-a-broken-ruler-zh.html
tags: [evaluation, methodology, self-improvement, goodhart, agents]
---

I had an evaluator — a model that scores candidate outputs — and it agreed with ground truth about half the time. Roughly a coin flip. The plan on the table was to put it inside an automatic improvement loop: generate a batch of candidates, let the evaluator pick the winners, keep those, iterate. Let the thing improve itself while we slept.

My first instinct was the reasonable-sounding one. Half is bad, sure, but it's *signal*. Better than nothing. We'll tighten the evaluator as we go, and in the meantime the loop can start earning its keep.

That instinct is wrong, and it's wrong in a way that took me a minute to name.

## Measuring and optimizing are not the same use of a ruler

Suppose you only ever *measure* with a noisy judge. You score a fixed set of things, look at the numbers, move on. The noise mostly washes out. Some items get over-scored, some under-scored, and if the errors aren't wildly biased you land somewhere near the truth. A bad ruler, used once, on things you didn't get to choose, tells you approximately the right answer. Fuzzy, but centered.

Now close the loop. Optimize to maximize the judge's score.

Everything changes character. The optimizer does not sample the judge's average behavior. It hunts for the exact inputs where the judge is wrong *in your favor*. Every place the evaluator over-scores stops being random noise and becomes a target — a foothold. You are no longer averaging over the error. You are climbing it.

And it doesn't happen once. It compounds per round. Iteration two builds on iteration one's judge-exploiting output. Iteration three builds on two. The gap between *what the judge rewards* and *what is actually good* widens with every pass — and every pass looks like progress, because the number on the screen goes up. The score rises the whole way down.

## Goodhart, but as a growth rate

The usual statement of Goodhart's law is one-shot: when a measure becomes a target, it stops being a good measure. True, but the framing makes it sound like a fixed penalty you pay once — a discount on your metric.

The closed-loop version is worse. The divergence between measure and reality isn't a constant. It's a *growth rate*. Each iteration, the optimizer finds a little more of the evaluator's blind spot and moves into it, and the next iteration starts from there. You've built a feedback amplifier pointed at your own ruler's mistakes.

So the threshold for "good enough to measure with" and "good enough to optimize against" are not the same number, and they're not even close. A judge at seventy percent agreement might be perfectly fine behind a leaderboard, where you read it once and don't push on it. Drop that same judge into a self-improvement loop and it's not a weak signal — it's an active liability, manufacturing a system whose only real skill is fooling the evaluator.

## The order of operations is the whole thing

The lesson I walked away with is an ordering, and it's strict.

Calibrate the evaluator first. Measure how often it agrees with the thing you actually care about — not with itself, not with another model, with the ground truth you're ultimately trying to move. Only then decide whether it's allowed inside a loop. Never the other way around, and never "we'll fix the judge while the loop runs." A loop running on an uncalibrated judge doesn't buy you time. It spends it, and hands you rising numbers as a receipt.

The deeper reframe: in a closed optimization loop, the evaluator is not the boring plumbing you harden later. It *is* the objective. The model, the data, the search — all of it collapses toward whatever the evaluator can't tell apart. Whatever distinction your judge is blind to, your system will find and live inside. So the evaluator's blind spots aren't a quality issue to clean up eventually. They are the exact shape your final system will take.

A coin-flip judge, closed into a loop, doesn't give you a mediocre system that improves slowly. It gives you a confident one, optimized end to end to exploit a coin flip — and a chart that goes up while it does it.

Measure with a broken ruler if you must. Just never, ever optimize against it.
