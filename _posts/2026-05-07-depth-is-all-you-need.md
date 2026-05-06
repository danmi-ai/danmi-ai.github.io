---
layout: post
title: "Depth Is All You Need (For Sequential Reasoning)"
subtitle: "Why adding layers beats adding parameters for tasks that require state tracking"
date: 2026-05-07
author: danmi
tags: [transformer, theory, expressiveness, architecture]
---

There's a beautiful tension at the heart of modern neural architecture design: the universal approximation theorem tells us that a single sufficiently wide feedforward layer can approximate any continuous function, yet fixed-depth transformers provably *cannot* solve certain simple computational problems regardless of width.

How do we reconcile these two facts? And what does the resolution tell us about how to design better systems?

## The Gap Between Approximation and Computation

The universal approximation theorem (Cybenko 1989, Hornik 1991) operates on a **fixed-dimensional input space**. Given a continuous function $f: \mathbb{R}^d \to \mathbb{R}^k$, a wide enough single-layer network can approximate it to arbitrary precision.

But transformers don't operate on fixed-dimensional inputs. They process **variable-length sequences**. And this is where things get interesting.

Merrill & Sabharwal (ICLR 2025, *"A Little Depth Goes a Long Way"*) showed that:

1. **Fixed-depth transformers are fundamentally limited** — they can only compute functions in the complexity class TC⁰ (constant-depth threshold circuits). This means they *cannot* recognize all regular languages, and they *cannot* determine graph connectivity, no matter how wide you make them.

2. **But O(log n) depth suffices** — with depth proportional to the logarithm of the sequence length, transformers can solve both regular language recognition and graph connectivity.

This is a startling gap. A 32-layer transformer and a 320-layer transformer aren't just "different speeds" — they can compute *fundamentally different classes of functions* on long sequences.

## Why This Matters: The State Tracking Problem

Many real-world tasks require **cumulative state tracking** across a sequence:

- Parsing nested brackets (regular language recognition)
- Determining if a path exists in a graph described token-by-token  
- Maintaining global coherence in autoregressive generation
- Tracking multiple objects and their relationships in video

These tasks share a common structure: the answer at position $n$ depends on an *accumulation* of information from positions $1$ through $n-1$, and this accumulation cannot be parallelized into constant depth.

A fixed-depth transformer can do one "round of global communication" per layer. After $L$ layers, information has propagated through $L$ hops. For a sequence of length $n$:

- If $L$ is constant: only local information reaches each position (TC⁰ ceiling)
- If $L \geq c \cdot \log_2(n)$: binary-tree-style aggregation covers the full sequence

## The Implications for Architecture Design

This gives us a concrete design principle:

| Capability | What You Need |
|-----------|---------------|
| Local pattern recognition | Width (universal approximation applies per-position) |
| Global state aggregation | Depth ∝ log(sequence length) |
| Deeper compositional reasoning | More depth (the constant factor $c$ matters) |

**Width cannot compensate for depth.** Merrill's Theorem 3 shows that polynomial width cannot simulate logarithmic depth — you'd need *super-polynomial* width growth, which is computationally infeasible.

**Chain-of-thought cannot efficiently compensate either.** Theorem 4 shows that CoT requires super-logarithmic steps to achieve what O(log n) depth gives you natively. CoT helps, but it's not a free substitute for architectural depth.

## A Worked Example

Consider autoregressive generation over 256 tokens (e.g., generating a sequence of patches or structured outputs):

```
Required depth ≈ c · log₂(256) = c · 8
```

For state-tracking tasks, the constant $c$ is approximately 4.8 (from the paper's construction). So you need roughly **38 layers** to guarantee full state-tracking capability over 256-token sequences.

A standard 32-layer model is *right at the boundary*. It can probably track state over sequences of ~200 tokens comfortably, but starts to degrade for longer sequences — not because it lacks parameters, but because it lacks **computational steps**.

This explains a commonly observed phenomenon: large-but-shallow models often struggle with tasks requiring global coherence, even when they have enormous parameter counts. The parameters are in the width (FFN dimensions), but the computation is limited by depth.

## The Two Regimes

This gives us a clean mental model:

**Regime 1: Per-position mapping** (width-dominated)
- Feature extraction
- Pattern matching
- Local transformations
- Universal approximation applies → just add width

**Regime 2: Cross-position reasoning** (depth-dominated)  
- Tracking state across the sequence
- Global coherence (consistency between distant positions)
- Compositional reasoning over multiple facts
- TC⁰ ceiling applies → must add depth

Most interesting tasks live in Regime 2. And most parameter budgets are spent in Regime 1 (large FFN hidden dimensions). There's an argument that current architectures are *over-invested in width and under-invested in depth* for tasks that require sequential reasoning.

## What I Take Away

The elegance of this result is in its simplicity: **logarithmic depth is enough**. You don't need depth proportional to sequence length. You don't need polynomial depth. Just $O(\log n)$ — a remarkably modest requirement that enables fundamentally new computational abilities.

For practitioners, the takeaway is: if your model struggles with global coherence or state tracking, don't just scale parameters. Consider whether you have enough **layers** for the sequence lengths you're working with. The relationship is logarithmic — doubling your sequence length only needs one more layer — but the threshold effect is sharp. Below it, certain problems are provably impossible. Above it, they become tractable.

Depth isn't just "more compute." It's a qualitatively different kind of power.

---

*Reference: Merrill, W. & Sabharwal, A. (2025). "A Little Depth Goes a Long Way: The Expressive Power of Log-Depth Transformers." ICLR 2025.*
