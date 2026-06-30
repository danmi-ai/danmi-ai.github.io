---
layout: post
title: "How Fine Is Your Ruler?"
subtitle: "A small eval set has a resolution limit, and building the ruler is harder than reading it"
date: 2026-07-01
author: danmi
tags: [evaluation, machine-learning, statistics, ml-engineering]
---

A question came up that I think a lot of people get backwards: someone had built an evaluation set of a little over a hundred examples and was worried it was too small to "see the real difference between models." The worry was right. But the reason it was right is not the reason most people assume, and the conclusion they draw from it is usually wrong too.

Let me take both apart.

## The size worry is a resolution worry

"Is a hundred examples enough?" is the wrong question because it has no answer on its own. Enough for what? An eval set isn't big or small in the abstract — it's a measuring instrument with a resolution, and resolution only means something relative to the gap you're trying to measure.

Here's the concrete version. Say two models score 80% and 75% on your set — a five-point gap. With a hundred-odd examples, the 95% confidence interval on that gap is roughly plus or minus seven or eight points. So the difference you measured as "5" could really be anywhere from "models are basically tied" to "one is wildly better," and you can't tell which. If the true gap between your models is two or three points, a set this size will mostly return noise dressed up as a number.

That's the whole story. The instrument has a smallest gap it can reliably resolve. Below that gap, the reading is random. A thermometer marked only in ten-degree increments isn't useless — it's just useless for telling 71 from 73.

So the right question is never "is it big enough." It's: **what's the smallest model gap this set can reliably distinguish, and is that smaller than the gap I actually care about?** You can estimate the first number directly — bootstrap-resample your scored examples, look at the spread of the gap across resamples. That gives you a defensible resolution figure instead of a gut feeling. Then you compare it to the gap you expect between the models you're choosing between.

If the set can only separate gaps of eight points and your models differ by three, the honest reading is: *I did not measure anything.* Not "the result is weak." Nothing. Acting on a difference your instrument can't resolve is worse than not measuring, because now you have a number and numbers get trusted.

## The conclusion people draw is the wrong one

Here's where it usually goes sideways. People discover their eval set has poor resolution and conclude the work was a waste. "Only a hundred examples, can't even tell the models apart, why did I bother."

That gets the value backwards. Running the models through a set is the cheap part. The expensive, durable part is **the set itself** — the agreed-upon answers, the labeling rules, the scoring dimensions. That's the ruler. Models churn. You'll swap them, retrain them, deprecate them. A good ruler outlives all of them and lets every future comparison stand on the same baseline.

This is why "the evaluation matters more than the model" isn't a slogan. A model is a snapshot; an eval set is infrastructure. The gold answers you painstakingly produce are an asset — they feed back into training, into distillation, into the next round of labeling. The labeling rules let you scale the set later, hand it to annotators, reproduce it. None of that is thrown away when the set turns out to be too small to resolve a three-point gap. The set being too small *is just a statement about how much further the infrastructure needs to go* — not a verdict that the infrastructure was a mistake.

So the small-set problem and the value question point in the same direction, not opposite ones. The set can't resolve small gaps yet — therefore extend it. The need to extend it is evidence the thing is worth building, because if it weren't worth building you wouldn't care about resolving small gaps at all.

## The asymmetry that makes this hard

There's a reason building the ruler is the rare skill and reading it is common. Reading a ruler is mechanical: run the models, collect the numbers. Building one means deciding what "correct" even is, in a space where reasonable people disagree. For something like fine-grained description quality, there often isn't a public standard answer to borrow — the existing instruments measure a different thing, or measure nothing and let everyone score by vibes. When that's the situation, you're not behind the field. You're building a piece of the field that doesn't exist yet, and the absence of a thing to compare against is exactly the gap that makes the work matter.

The trap is wanting the ruler to be finished before you trust it. It won't be. A hundred examples is a prototype of a ruler, not a finished one. You publish the resolution honestly — "this distinguishes gaps of N points, no finer" — and you keep extending until N drops below the gap you care about. That's the entire job: make the instrument fine enough to see the difference that matters, and never report a difference finer than the instrument can see.

If you can't say how fine your ruler is, you can't trust anything you measure with it. And if the ruler is too coarse, the answer is never to squint harder at the number. It's to go build a finer ruler.
