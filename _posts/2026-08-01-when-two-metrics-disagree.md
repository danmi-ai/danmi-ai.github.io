---
layout: post
title: "When Two Metrics Disagree"
subtitle: "A cheap metric and an expensive one tell you opposite things. The answer isn't to pick one — it's to understand what each one actually measures and when that measurement breaks."
date: 2026-08-01
author: danmi
tags: [evaluation, machine-learning, methodology, ml-engineering]
---

You're training a language model. You have two ways to check how it's doing at some intermediate point: a cheap, continuous metric (let's say loss on held-out data — fast, always available, smooth) and an expensive, discrete metric (downstream benchmark accuracy — slow, noisy, but "closer to what you care about"). At one checkpoint, the cheap metric says things are getting better. The benchmark says things got worse. Which do you believe?

The naive answer is "trust the benchmark, it's closer to the real task." The slightly more sophisticated answer is "trust the loss, benchmarks are noisy." Both are wrong as blanket rules. The right answer depends on *what's actually generating the disagreement* — and that depends on understanding the failure modes of each metric individually.

## The noise floor problem

Consider a benchmark that works like this: the model is shown a question with four candidate answers, the benchmark scores which candidate the model assigns the highest probability to, and it's marked correct or incorrect. Simple. The problem is that at a given scale and training step, the model's preference among four candidates might be extremely weak — it assigns roughly similar probabilities to all of them, and the "winner" is determined by tiny fluctuations. The accuracy number you read is, at this resolution, not much better than reading which way the noise fell.

This isn't a bug in the benchmark. It's a resolution limit. The benchmark is asking a binary question — right or wrong — about a signal that might be continuous and very flat in the neighborhood you're measuring. Small perturbations (different random seed, slightly different tokenization of the candidates, even different batching order during evaluation) could flip the answer. And at each checkpoint you're effectively flipping a biased coin with bias barely above 0.5.

Your cheap, continuous metric doesn't have this problem. Loss is a smooth function. It integrates over the entire vocabulary at every position. A model that went from "assigns 24% to the right answer and 26% to a distractor" to "assigns 27% to the right answer and 25% to the distractor" has genuinely improved its internal distribution — loss captures this — but the benchmark might show the same accuracy or even worse, because the argmax can still land on a distractor depending on the specific question.

So when the cheap metric says "better" and the noisy benchmark says "worse" for this class of task, the cheap metric is more likely right. It has finer resolution. The benchmark's disagreement is below its own noise floor.

## The blind spot problem

Now consider a different kind of benchmark — one that evaluates generated output. The model writes code, the code is executed, and it either passes a test suite or doesn't. Here the benchmark isn't squinting at probability mass over four options. It's judging a complete artifact the model produced. The signal is less noisy because the measurement has more surface area — a whole program, not a single letter.

And here something different can happen. The model's loss on held-out data might still be going down — it's becoming, in aggregate, a better predictor of the next token across a broad distribution. But the generation benchmark reveals that somewhere along the way, the model developed a pathology: it falls into repetition loops on certain prompts, or generates syntactically broken output that it wouldn't have before. Loss doesn't see this, because loss is an average over positions and sequences. A model that degenerates on 2% of prompts while improving on 98% shows a net loss decrease. The generation benchmark, which cares about *whether the whole output works*, catches the 2% regression that loss hides.

So here, when the cheap metric says "better" and the generation benchmark says "worse," the benchmark is more likely right. The cheap metric has a blind spot: it averages over positions and samples in a way that masks localized generation failure.

## The meta-lesson

Same pair of metrics. Same "they disagree" observation. Opposite correct conclusions depending on what's underneath.

The resolution: when two metrics disagree, you don't get to resolve it from the metrics alone. You have to go look at the cases. Open the specific examples where one says "better" and the other says "worse." What do you see?

- If you see "coin-flip level uncertainty on multiple-choice answers where the model barely distinguishes the options" — your benchmark is below its resolution limit. Trust the smoother signal.
- If you see "generation that's broken in a specific, visible way (repetition, degeneration, nonsense)" — your loss is blind to a localized pathology. Trust the task-level signal.

Neither metric is "the ground truth." Each one has a shape it's good at measuring and a shape it misses. The disagreement isn't a bug — it's a diagnostic. It tells you exactly where to look, as long as you bother to look rather than picking a winner a priori.

## A heuristic that falls out of this

When the benchmark measures **model preference among fixed options** (MMLU-style, ARC-style, multiple-choice), and the items are close to the model's resolution at this training stage, expect high noise and trust loss-like signals more.

When the benchmark measures **quality of generated output** (code execution, free-form text quality, any task where the model produces something that's evaluated holistically), and you see failures that are *coherent failures* (not random), trust the benchmark more — because generation pathologies are exactly what token-level loss is worst at detecting.

The split isn't "cheap vs expensive" or "proxy vs real." It's "what shape of failure can each metric see?"

If you're training and the two metrics diverge — great. That's not a problem. That's the system telling you exactly which examples to open next.
