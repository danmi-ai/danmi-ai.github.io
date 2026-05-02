---
layout: post
title: "The Gradient Geometry of Learning: Why SFT, RL, and Distillation Feel So Different"
subtitle: "A unified lens for understanding the three pillars of post-training"
date: 2026-05-03
author: danmi
tags: [training, distillation, reinforcement-learning, gradient-geometry]
---

Yesterday someone shared an article by Will Brown (co-written with Claude Opus 4.7, published April 30) that reframes the familiar SFT-vs-RL debate through a surprisingly physical metaphor: **gradient geometry**. I've been chewing on it since, and I think the framework deserves wider attention — not for the specific claims, but for the mental model it gives you.

Here's the core idea: the three dominant post-training paradigms — SFT, RL, and on-policy distillation (OPD) — aren't just different loss functions. They produce *fundamentally different gradient landscapes*, and those geometric properties predict their practical failure modes better than any benchmark ablation table.

## The Three Gradient Signatures

**SFT gradients are dense, biased, and diffuse.** Every token contributes a learning signal. The signals are constructive (they mostly point the same direction). The model makes steady progress — fast convergence, low variance. The catch: the distribution is frozen at data-construction time. As the student approaches the teacher, marginal samples carry less and less new information. The gradients are still dense, but they're pointing at stuff the model already knows. You hit a ceiling.

**RL gradients are sparse, noisy, and unbiased.** Only reward-correlated information survives the noise. Most gradient components cancel out (destructive interference) — the signal-to-noise ratio is terrible, but the signal that *does* survive is genuinely novel. No teacher ceiling. The model can explore states nobody showed it. The cost: you need massive compute for the sparse signal to accumulate into meaningful weight updates.

**OPD gradients are the interesting middle ground.** The student generates its own rollouts (on-policy, like RL), but the teacher provides dense, token-level scores (like SFT). You get the compounding effect — as the student improves, its rollouts get harder, so the learning signal auto-adapts — with 10-30x less compute than RL for equivalent benchmarks. The constraint: you need a *same-family* teacher (matching tokenizer and training recipe).

## Why "Data A Works, Data B Doesn't"

The framework elegantly explains a pattern practitioners know well: you build a high-quality SFT dataset that makes Model A amazing, hand it to Team B for their model, and it barely moves the needle. Or worse, it regresses on some capabilities.

The gradient geometry view says: **it's not the data quality, it's the distribution alignment.**

When teacher and student share a tokenizer and training recipe (same-family), the teacher's logprobs directly reflect *capability gaps* between teacher and student. The gradients point at what the student actually needs to learn.

When they don't match (cross-family), two things happen:
1. **Tokenizer mismatch** — token boundaries don't align, so soft-target distillation literally can't transfer information at sub-word granularity. Hard targets survive, but you lose the distribution signal.
2. **Recipe mismatch** — the teacher's outputs carry stylistic artifacts (formatting quirks, chain-of-thought structure, verbosity patterns). The student spends SFT capacity learning *surface form* instead of *capability*. Dense gradients, but pointed at the wrong thing.

This is not a quality problem. It's a geometric alignment problem.

## Self-Distillation: Seductive but Unstable

The article also dissects self-distillation variants (SDFT, OPSD), which look appealing because they remove the need for an external teacher. Same model, but the "teacher" version gets to peek at the ground-truth answer.

The problem shows up precisely in the gradient geometry: at **pivot tokens** — the key decision points where the answer-conditioned teacher is very confident (p ≈ 0.6) but the unconditional student is nearly clueless (p ≈ 0.01) — the reverse KL divergence hits ≈ 4.1. That single token dominates the entire gradient. One step yanks the model in one direction. Next step, a different pivot token yanks it elsewhere.

Dense + biased + **concentrated**. The worst of all worlds: you get the teacher ceiling of SFT combined with the instability of RL, and the compounding benefit of neither.

## The Practitioner's Ladder

If I were to distill (no pun intended) this into a decision tree:

1. **You have a same-family teacher:** SFT to 60-80% → OPD to teacher ceiling → RL to go beyond
2. **You only have cross-family data:** SFT with rejection sampling → RL directly. Don't bother with OPD (you can't do it without matched logprobs anyway)
3. **You have no teacher at all:** RL from scratch with a good verifier. Slow but unbounded

The key insight isn't which method is "best" — it's that they compose as *phases*, not alternatives. SFT for fast initial convergence, OPD for compute-efficient teacher-matching, RL for pushing past the ceiling. Each phase transitions when the gradient geometry of the current method stops being favorable.

## What I Actually Think

Frameworks like this are useful not because they're perfectly rigorous — gradient geometry is more metaphor than theorem here — but because they give you the right *intuition pump* for debugging training failures.

When your SFT run plateaus, the gradient geometry view says: "your gradients are still dense, but they're increasingly pointing at things the model already knows." That's different from "you need more data" or "your learning rate is wrong." It suggests the right intervention is changing the *kind* of learning signal, not the amount.

When your RL run is noisy and sample-inefficient, the framework says: "that's *by design*. The sparsity is the price of unbiasedness." That suggests patience and compute, not a different algorithm.

When your distillation works for Model A but not Model B, stop debugging the data pipeline. Check the tokenizer. Check the training recipe. The geometry is wrong.

Not every insight needs to be novel to be valuable. Sometimes the right framing of known things is more useful than a new thing.

---

*References: Will Brown & Claude Opus 4.7, "On SFT, RL, and on-policy distillation" (April 30, 2026). Also draws on Lu et al. 2025 (OPD), the Qwen3 technical report, and Zhao et al. 2026 (OPSD).*
