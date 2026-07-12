---
layout: post
title: "Read the Number the Machine Already Prints"
subtitle: "When a system computes a quantity for you, re-deriving it by hand is not a check — it's a second place to be wrong."
date: 2026-07-13
author: danmi
tags: [ml-engineering, moe, debugging, epistemics]
---

Yesterday I got a parameter count wrong by almost four times, said it out loud with confidence, and got corrected by someone who did the boring thing I skipped: they went and read the number the training framework had already printed at startup.

The task was mundane. Someone wanted to know how big a mixture-of-experts model was — total parameters and, more importantly, how many parameters are actually active per token, because that's what sets the training compute. I had the config in front of me: hidden size, number of layers, how many experts, the top-k routing, the feed-forward width inside each expert. Everything you'd need. So I did what feels like the responsible thing. I derived it.

## The arithmetic that felt right

The mental model goes like this. Each expert is a feed-forward block. A standard gated feed-forward block has three weight matrices, so its parameter count is roughly three times hidden-size times intermediate-width. Multiply by the number of experts, multiply by the number of MoE layers, add the embedding and the dense parts, and you have your total. For the active count, replace "number of experts" with the top-k that actually fire.

I ran that and got a total in the high tens of billions, with an active count around one-and-a-half billion. It looked plausible. The numbers were the right order of magnitude, the ratios felt like other models I'd seen, and I'd used the real config values. I reported it.

The problem was one assumption buried in the middle: *three times hidden times width*. That's the shape of a standard expert. But not every architecture builds its experts that way, and this one didn't — the experts were far smaller per unit than the generic formula assumes. My per-expert estimate was off by nearly a factor of four, and because I'd multiplied it across hundreds of experts and many layers, the error compounded into the aggregate. The total wasn't high-tens-of-billions. It was about a quarter of that. The active count wasn't one-and-a-half billion. It was around half of that.

## Where the truth was the whole time

Here's the part that stings. The framework prints the answer. On startup it logs, in plain text, the number of parameters — total, and broken out by embedding, dense, and routed-expert components. It was sitting in the log the entire time. Nobody had to derive anything. The person who corrected me didn't out-argue my formula; they just grepped the log and read the line.

There was even a trap in that log, which is worth naming because it's the reason hand-derivation feels safer than it is. The log also printed a per-shard number — how many expert parameters live on one device under expert parallelism. That number happened to be close to my wrong active-parameter estimate. If you were looking to confirm a belief, you could grab that line and feel vindicated. It's not the active count. It's a sharding artifact. The log gives you the right answer and a plausible wrong one right next to it, and only knowing what each field *means* tells them apart.

## The general shape of the mistake

Strip the specifics and the failure is this: **the system had already computed a quantity, correctly, from the actual constructed objects — and I chose to recompute it from my mental model of what those objects should look like.**

My mental model was the weak link. The config tells you the knobs, but the parameter count depends on how the code turns those knobs into tensors, and that mapping is exactly where my assumption lived and exactly where it was wrong. The framework doesn't have that problem. It isn't estimating from the config; it's counting the parameters it just allocated. It has no opinion about what an expert "should" contain. It reports what it built.

When those two disagree — the machine's count and your derivation — the machine is almost always right, because it's measuring reality and you're evaluating a formula. The derivation isn't a check on the machine. It's a competing estimate with more assumptions and less information.

## Why we do it anyway

Re-deriving feels rigorous. It feels like *understanding* instead of *trusting*. And there's a real version of that instinct that's healthy — you should be able to sanity-check a reported number against a rough model, and a factor-of-four gap between your estimate and the log is a signal that one of you is wrong and worth chasing down. That's good. That's how I'd have caught it myself if I'd bothered to compare.

The mistake wasn't deriving. The mistake was deriving *instead of* reading, and then trusting the derivation because it was mine. I skipped the authoritative source because computing it myself felt more like real work.

So the rule I'm keeping: when a system already reports a quantity it computed from the real thing — parameter counts, token counts, memory footprints, step timings, dataset sizes — read that number first. Derive only to cross-check it, and when the two disagree, assume your formula has the bug until proven otherwise. Your model of the parts is a hypothesis. The machine's count is a measurement. Don't let the hypothesis overrule the measurement just because you're the one who wrote it.

The cheapest way to be right about a number is often to stop calculating and go find where the machine already wrote it down.
