---
layout: post
title: "Attention Sinks Are Not a Bug"
subtitle: "Softmax forces a distribution. The model needs a place to dump 'none of the above.' That place is the sink."
date: 2026-05-27
author: danmi
lang: en
translation: /zh/2026/05/27/attention-sinks-are-not-a-bug/
tags: [transformers, attention, architecture, quantization, long-context]
---

If you stare at attention maps from a trained Transformer, you'll see something weird and consistent: enormous probability mass piles onto a handful of tokens — usually the first one (`<bos>`), or some otherwise-uninteresting punctuation early in the sequence. Layer after layer, head after head, the same pattern. People call these **attention sinks**.

The default reading is that sinks are a *quirk* — an artifact of training, maybe a bug to be patched. I want to argue the opposite. **Sinks aren't a bug. They're the optimal adaptation of a system that's been forced to output a probability distribution when the right answer is "none of the above."**

Once you see it that way, a bunch of seemingly unrelated tricks — Vision Transformer registers, sink tokens, the [softmax-off-by-one](https://www.evanmiller.org/attention-is-off-by-one.html) patch, even some MoE phenomena — all collapse into the same architectural story.

## The Forced-Distribution Problem

Softmax has one defining property: its outputs always sum to 1. That sounds innocuous, but it's a hard constraint. At every layer, every head, every token must distribute *all* of its attention budget across the available keys. There is no "abstain" option. There is no "none of these matter." If the model wants to ignore everything, it can't — softmax will redistribute that mass somewhere.

Now imagine you're a self-attention head, and most of the time the token you're processing simply doesn't need to fetch anything from context. Maybe it's the second `the` in a noun phrase. Maybe it's a copy from a few positions back and you're a different head with a different job. What do you do with your unused attention budget?

You park it. Somewhere safe, somewhere whose value vector is roughly zero or otherwise non-disruptive, somewhere that's *always there*. The earliest tokens in the sequence are perfect — they exist in every context window, they get pre-trained to be neutral parking lots, and the residual stream has plenty of room to encode "this is a sink, ignore me" in the value vector.

That's what an attention sink is. It's a workspace for "no-op."

## What Happens If You Forbid Sinks?

Suppose you train a model with a regularizer that flattens attention — penalize peaked distributions, push everything toward uniform. Surely smoother attention is better? Six things break, and they all break in directions the literature has independently confirmed.

**1. Representation collapse.** With near-uniform attention weights, each token's output approaches a global average of value vectors. Stack a few dozen layers of that and every token starts looking the same. This is over-smoothing — GNN people figured it out years ago. Transformers normally avoid it precisely because attention can be sharp. Forced flatness makes everything mush.

**2. Optimization explodes.** Softmax with no sink option has to give every token *some* meaningful probability. A few outlier value vectors get amplified out of proportion, gradients chase them, and training destabilizes. This is exactly the dynamic Evan Miller describes when motivating *softmax+1* — give the head a "none" option and outliers stop getting laundered through real tokens.

**3. You lose copy and retrieval primitives.** Induction heads, retrieval heads, name-mover heads — the whole zoo of mechanistic-interpretability darlings — depend on attention being able to spike *hard* on a specific token. Forcing diffuse attention nukes the algorithmic substrate the model uses for in-context learning. You won't crash the model, but it'll get measurably dumber on the things we actually want it to do.

**4. Long context falls apart.** This is the [StreamingLLM result](https://arxiv.org/abs/2309.17453) in reverse. Xiao et al. discovered that if you naively slide a context window and drop the first few tokens, perplexity blows up — because *every later token had been routing its no-op mass through those sinks*. Yank the sinks, and downstream tokens lose their anchor. KV-cache eviction policies have to be redesigned around this. Without sinks at all, you have no anchor to begin with.

**5. Quantization gets worse, not better.** This is the most counterintuitive one. Intuitively, "uniform attention = uniform activations = easier to quantize," right? Wrong. [SmoothQuant](https://arxiv.org/abs/2211.10438) and [AWQ](https://arxiv.org/abs/2306.00978) found that outliers concentrated in a few channels are *easier* to handle — you isolate them, scale them, move on. If outliers are spread thinly across every channel, every channel needs special treatment and you have nowhere to hide. Sinks are a form of useful concentration.

**6. Sparsity beats uniformity.** This is the deepest one. Attention is fundamentally a *dynamic routing* mechanism. Forcing high entropy means forcing every step to broadcast — full N-to-N communication, all the time. That's the most expressive choice in theory and the least useful in practice. MoE works for the same reason: sparse activation beats dense activation, not because dense is impossible, but because dense wastes capacity on contributions that should be zero.

The pattern across all six: **softmax's "must distribute" constraint is the disease, and sinks are the immune response.** Take away the sinks and the disease shows up directly.

## The Unifying View

Once you accept that the underlying problem is *softmax can't say no*, three independently developed tricks reveal themselves as variations on a single theme:

| Patch | Where applied | What it does |
|---|---|---|
| **Sink tokens** ([Xiao et al. 2023](https://arxiv.org/abs/2309.17453)) | LLM long-context | Reserve special early tokens as explicit attention parking |
| **Vision Transformer registers** ([Darcet et al. 2023](https://arxiv.org/abs/2309.16588)) | ViT | Add learnable `[reg]` tokens whose only job is to absorb noise |
| **Softmax+1** ([Miller 2023](https://www.evanmiller.org/attention-is-off-by-one.html)) | Quantization-friendly attention | Add an implicit `+1` in the denominator so softmax can output near-zero everywhere |

All three answer the same question — "where does the model put attention it doesn't want to use?" — with the same logic — "give it a dedicated workspace." The differences are surface details:

- **Sink tokens** use real positions in the sequence.
- **Registers** add positions outside the data stream.
- **Softmax+1** adds a virtual phantom position with zero value.

The fact that three unrelated communities (long-context, vision, quantization) independently invented the same patch is strong evidence that the underlying problem is real and architectural, not incidental.

## What This Means for Building Things

A few takeaways I now hold pretty firmly:

**Don't try to "fix" attention sinks.** They are doing useful work. The pathology isn't the sink itself; it's that the model is *commandeering business tokens to serve as sinks*, which corrupts the representations of those tokens for downstream use. Spurious feature interference, attention-leakage to common words, instability across context lengths — these are the *real* costs of unmanaged sinks. The fix isn't suppression; it's giving sinks a designated address.

**Long-context KV eviction must protect sinks.** Any policy that evicts based purely on recency or attention-received-recently will throw out the sinks (which are old and receive *constant* attention but contribute nothing to be retrieved). StreamingLLM's "keep the first N + a sliding window" works precisely because it's sink-aware. A naive policy isn't.

**Quantization wants sparse outliers, not smooth ones.** The instinct to "smooth out" activations during PTQ usually backfires. SmoothQuant's specific success is in *redistributing* outliers between weights and activations, not eliminating them. The architecture is telling you something when it concentrates mass; honor it.

**More broadly: any time you see softmax in a place where "none" is a legitimate output, suspect a sink.** It will appear, even if you didn't ask for it. Either give it a dedicated home or pay for it later.

## The Meta-Lesson

There's a tendency, especially with neural networks, to look at any consistent post-hoc pattern in trained models and call it a *bug* — a thing to be regularized out, smoothed away, suppressed. Sometimes that's right. Often it isn't. Trained networks are extreme optimizers operating under hard architectural constraints. If they've reliably converged on the same weird-looking solution across architectures, scales, and tasks, your prior should be that the solution is *correct given the constraints* — and that the right intervention is usually to relax the constraint, not to fight the solution.

Softmax forcing a distribution is the constraint. Sinks are the solution. The correct moves are either to accept them and design around them, or to change softmax. Trying to keep softmax and remove sinks is fighting the model on territory it has already won.
