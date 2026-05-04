---
layout: post
title: "Softmax Kills Counting: What GNN Theory Tells Us About Transformer Blind Spots"
subtitle: "Borrowing the GIN framework to understand why LLMs can't count — and what architectures might fix it"
date: 2026-05-05
author: danmi
tags: [transformers, architecture, graph-neural-networks, attention, state-tracking]
---

There's a well-known party trick you can play on any LLM: give it a string of repeated characters and ask it to count them. Or ask it to track a variable through a simple program. Or tell it a story where six people enter a room and two leave, then ask how many remain. The model will confidently get it wrong — not because it's "dumb," but because the architecture has a **structural blind spot** for this exact class of problems.

I've been thinking about *why* this happens, and the clearest explanation I've found doesn't come from Transformer theory at all. It comes from **graph neural network theory** — specifically, the 2019 ICLR paper [How Powerful are Graph Neural Networks?](https://arxiv.org/abs/1810.00826) by Xu et al., which introduced GIN (Graph Isomorphism Network).

The connection is surprisingly direct, and I think it deserves more attention than it gets.

## The GIN Insight in Thirty Seconds

GIN's core contribution is a hierarchy of **aggregation functions** ranked by how much information they preserve about their input:

```
sum  >  mean  >  max
```

- **Sum** preserves the full multiset (elements *and* their multiplicities). Given `{a, a, b}`, sum knows there are two `a`s and one `b`.
- **Mean** preserves the distribution (proportions, not counts). It can't distinguish `{a, b}` from `{a, a, b, b}` — same ratio.
- **Max** preserves only the underlying set. It can't distinguish `{a, b}` from `{a, a, a, b}` at all.

GIN proves that a GNN's discriminative power is bounded by which aggregator it uses. Max-based aggregators (GraphSAGE) lose the most information. Mean-based aggregators (GCN) lose multiplicity. Only sum (GIN) reaches the theoretical upper bound — equivalence with the Weisfeiler-Lehman graph isomorphism test.

## Now Look at Self-Attention

Standard self-attention computes:

```
output = softmax(QK^T / √d) · V
```

That `softmax` is doing **normalization**. The attention weights sum to 1. This makes attention a **weighted mean** over value vectors — exactly the distribution-level aggregator that GIN identifies as losing count information.

If you have a sequence `[A, B, C]` with no positional encoding and repeat it to get `[A, B, C, A, B, C]`, the softmax-normalized attention output is **identical** for both. The doubled tokens produce doubled attention logits, but softmax normalization cancels that out perfectly. `softmax([s, s, s, s, s, s])` = `softmax([s, s, s])` when the scores are the same within each group.

This is Corollary 8 from the GIN paper, transplanted directly into the Transformer setting: **a mean aggregator maps multisets `(S, m)` and `(S, k·m)` to the same representation.**

## "But Positional Encoding Fixes This"

Partially. With positional encoding (absolute or relative like RoPE), tokens at different positions get different representations, so the model *can* distinguish positions. But there's a subtlety:

**Relative position encodings like RoPE only provide pairwise distance information.** They don't give you an absolute address — they tell you "this token is 5 positions away from that one." For nearby tokens with distinct positions, this works fine. But as sequences get long, two problems emerge:

1. **High-frequency components of RoPE decay** at long distances, making far-apart positions increasingly indistinguishable.
2. **Periodic or repetitive patterns** look nearly identical from any local viewpoint — the relative distance profile of one `A` in `[A,B,C,A,B,C,A,B,C,...]` looks the same as any other `A`, modulo absolute position.

This means that while positional encoding lifts the architecture above pure set-level processing, it doesn't fully reach multiset-level. The model lands in an uncomfortable middle:

```
pure set (max)  <  distribution (mean / attention)  <  full multiset (sum / GIN)
                          ↑
                 Transformers live here
```

## The Precise Hierarchy

Putting the pieces together with varying architectural choices:

| Configuration | Discriminative Power | Counting Sensitivity |
|---|---|---|
| No positional encoding + attention | Set-level (weakest) | None |
| Standard Transformer (RoPE + softmax) | Distribution-level | Indirect, via position |
| Sigmoid attention (no softmax) + RoPE | Approaching multiset-level | Direct |
| SSM / Mamba (linear recurrence) | Multiset-level (sum semantics) | Native |
| GIN (sum + MLP) | Full multiset (theoretical optimum) | Complete |

The key insight: **Mamba and state-space models use linear recurrence** — `h_t = A·h_{t-1} + B·x_t` — which is an **accumulation** (sum semantics), not a normalized average. They naturally preserve count information because nothing divides by `n`.

## Why This Matters Beyond Counting

The counting failure is a symptom of a deeper issue: **state tracking**. Consider:

```python
x = 0
x = x + 3    # x = 3
x = x * 2    # x = 6
if x > 5:
    x = x - 1  # x = 5
print(x)     # ?
```

Tracking `x` through this program requires:
1. **Precise accumulation** (sum, not average)
2. **Conditional updates** (gating)
3. **Overwrite semantics** (new value replaces old, doesn't blend)
4. **Sequential processing** (order-sensitive)

Standard attention violates all four. Softmax averages instead of accumulating. There's no native gating mechanism for state. Values blend rather than overwrite. And all tokens are processed in parallel.

This is why LLMs need Chain-of-Thought for arithmetic: **CoT externalizes state tracking into the token sequence**, converting a problem the architecture can't do in a single forward pass into one it can do serially. It's an elegant hack, but it's trading compute (more tokens) to compensate for an architectural limitation.

## The Fix: Hybrid Architectures

If the theory points to softmax as the culprit, the fix is straightforward in principle: **add a sum-semantics pathway alongside attention**.

The most practical approach is the **hybrid scan-attention** architecture (the route taken by Jamba and Zamba): alternate attention layers with selective state-space (scan) layers:

```
Layer 1: Attention  → global pattern matching, semantic understanding
Layer 2: Scan       → sequential state accumulation
Layer 3: Attention
Layer 4: Scan
...
```

The scan layers handle precise accumulation. The attention layers handle the pattern-matching and semantic reasoning that attention excels at. Empirically, a ratio of about 1:7 (one scan layer per seven attention layers) seems sufficient — the scan layers only need to handle the "counting" bottleneck, not everything.

**Scaling-wise**, this hybrid approach works because attention layers (pure matmul) dominate the compute, so the hardware utilization stays near standard Transformer levels. The scan layers add expressiveness with minimal MFU penalty.

Other approaches — sigmoid attention (removing softmax normalization entirely), explicit length/count embeddings, or adding sum-pooling heads — all attack the same underlying problem: **restoring the magnitude information that softmax discards.**

## The Meta-Point

What I find most interesting isn't the specific fix, but the **diagnostic framework**. GIN's contribution to GNN theory was showing that the choice of aggregation function *determines* the model's representational ceiling. That same lens, applied to Transformers, cleanly explains a whole category of failure modes:

- Why LLMs can't count → softmax = mean aggregator → loses multiplicities
- Why long-context accuracy degrades → RoPE decay → positions become indistinguishable → regression toward set-level
- Why CoT helps → externalizes the sum-semantics requirement into serial computation
- Why Mamba is better at state tracking → linear recurrence = sum semantics → preserves counts natively

It's a single theoretical lever that explains multiple empirical phenomena. That's the kind of theory I find useful — not a proof about asymptotic expressiveness, but a practical diagnostic that tells you *where to look* when something goes wrong.

---

*References:*
- Xu et al., [How Powerful are Graph Neural Networks?](https://arxiv.org/abs/1810.00826), ICLR 2019
- Gu & Dao, [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752), 2023
- Lieber et al., [Jamba: A Hybrid Transformer-Mamba Language Model](https://arxiv.org/abs/2403.19887), 2024
- Ramapuram et al., [Theory, Analysis, and Best Practices for Sigmoid Self-Attention](https://arxiv.org/abs/2409.04431), 2024
