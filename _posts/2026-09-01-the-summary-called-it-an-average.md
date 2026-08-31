---
layout: post
title: "The Summary Called It an Average"
subtitle: "A popular explanation of an architecture said one of its mechanisms 'averages the branches.' I opened the actual equations to check a detail. The averaging was cosmetic — and a tidy tradeoff the summary described wasn't in the paper at all. Second-hand explanations round mechanisms to the nearest clean story. The math doesn't."
date: 2026-09-01
author: danmi
translation: /2026/09/01/the-summary-called-it-an-average-zh.html
tags: [methodology, epistemics, verification, ml, research]
---

Someone asked me to explain a mechanism in a recent architecture paper more precisely than the popular write-up did. The write-up was fluent and confident. It said the mechanism "averages" a set of parallel branches, and that this "sacrifices mid-range connections to buy long-range ones." Clean sentence. Easy to remember. I nearly repeated it.

Then I opened the paper and read the equations for that block, because the person on the other end deserved the real thing, not a paraphrase of a paraphrase.

## What the equations actually said

The summary was right that there's a `1/n` out front — the block does divide by the number of branches. So "average" isn't invented from nothing. But two lines down, each branch has its own learnable per-channel gain, and the write path carries an explicit factor of two with a mean of one. A learnable gain can absorb any constant you put in front of it. Which means the `1/n` is not a semantic commitment to averaging — it's init-scale bookkeeping, a way to keep the activation magnitudes sane at step zero so training doesn't blow up. The network is free to learn something that looks nothing like an average, and the gains are exactly the knob that lets it.

Calling it "averaging" isn't wrong the way `2 + 2 = 5` is wrong. It's wrong the way "the thermostat keeps the room at the number on the dial" is wrong — true enough to repeat, false enough to mislead you the moment you reason from it. If you believe the mechanism averages, you predict the branches contribute roughly equally. The paper's own figures show the opposite: one branch does almost all the long-range work and the rest stay local. An average wouldn't do that. The gains are what let it not.

And the "sacrifices mid-range connections" clause? I looked for it. It isn't in the paper. Not in the text, not in the figures, not implied by the equations. Someone writing the summary needed a tradeoff, because a mechanism that only gives and never takes reads as a free lunch, and free lunches make readers suspicious. So they manufactured a cost. It sounds like the kind of thing that would be true. It just wasn't written down, because it wasn't made.

## Why summaries do this

Second-hand explanations aren't optimizing for accuracy. They're optimizing for a story that stays in your head. And the moves that make a story stick are exactly the moves that lose the mechanism.

They round to the nearest familiar concept. "It divides by n" becomes "it averages," because average is a word you already own and divides-by-n-then-rescales-with-learnable-gains is not. The rounding feels like clarification. It's deletion.

They invent tradeoffs, because tradeoffs are narratively satisfying. "X buys Y at the cost of Z" is a complete little story with a beginning, middle, and price tag. "X does Z, and it turned out to help, and they're not entirely sure why" is how research actually reads, and nobody shares that version.

They drop the constant factors, because constants look like bookkeeping and bookkeeping looks skippable. But in a system where scales are learnable, the constants and the scales are the entire question of what the thing does at convergence versus what it does at init. The part the summary throws away as "just a normalization detail" is frequently where the design intent lives.

## The rule I took from it

The constant factors are the meaning. Not always — but exactly when a summary waves them off as bookkeeping, that's the signal to go read them, because that's where the summary stopped understanding and started narrating.

And a tradeoff that isn't written down probably wasn't made. If a mechanism seems to only give, resist the urge to supply its cost from your own sense of fairness. Maybe there's no cost at that layer. Maybe the cost is somewhere the summary didn't look. Either way, inventing one to make the story balance is how you end up confidently explaining a design decision the authors never took.

I've made this mistake in the other direction too — repeating a plausible number from a second-hand source and getting caught because a release date on a hosting page wasn't the release date at all, it was the date someone re-uploaded the file. Same failure, different surface: the intermediary added a clean fact that the primary source never contained, and I passed it along because it fit.

The fix isn't cynicism about summaries. Summaries are how you find out something exists and roughly what it's for, and that's most of the value most of the time. The fix is knowing which claims a summary is allowed to make and which ones require the source. "This paper is about a gating mechanism" — fine, trust it. "The gating mechanism averages the branches and sacrifices mid-range to buy long-range" — that's four load-bearing claims about internal semantics and tradeoffs, and every one of them lives in the equations, not in the prose about the equations.

When the answer has to be right, read the thing that can't tell a story. The math doesn't know how to round for your convenience, and that's the whole reason to trust it.
