---
layout: post
title: "Attention Is Not Attribution"
subtitle: "Why a low attention score doesn't mean the model ignored that input"
date: 2026-06-30
author: danmi
tags: [machine-learning, interpretability, attention, methodology]
---

Here's a claim I run into constantly when people reason about multi-modal models: "As the generated text gets longer, the attention paid to the visual tokens drops, so the model is relying more on its language prior and ignoring the image — that's where hallucination comes from."

The conclusion isn't wrong in spirit. But the reasoning underneath it fuses two different things into one, and the seam is exactly where the argument falls apart if someone pushes on it.

## Two mechanisms wearing the same coat

When you say "visual attention drops as the text grows," you could mean either of two things, and they are not the same:

**One: the share got diluted.** Attention is a softmax. All the attention weights over all tokens sum to one. As you generate more text tokens, those new tokens claim some of the fixed budget, so the slice left for the visual tokens shrinks. This happens *mechanically*. It requires no story about the model "preferring" language. It would happen even if the visual tokens were carrying all the useful signal — the normalization just spreads the same pie over more slices.

**Two: the model started depending on the image less.** This is the interesting claim — the model actively shifts its computation toward the language context and stops consulting the visual evidence.

People say "attention to the image went down" and let it stand in for both. But only the second one is what you actually want to prove. The first is an artifact of how softmax works. If your evidence for "the model ignores the image" is just "the visual attention share dropped," you've proven the trivial thing and smuggled in the interesting thing for free.

## High attention is not high contribution

The deeper trap is assuming attention weight measures information contribution at all.

It frequently doesn't. Transformers have attention sinks — large chunks of attention pile up on the first token, on delimiters, on a handful of positions that carry almost no semantic load. Meanwhile, tokens with *low* attention scores can be doing critical work. The clean way to see this: knock the token out. Mask the visual tokens, or ablate them, and watch what happens to the output. Models whose visual tokens had unremarkable attention scores will still collapse when you remove those tokens — proof that the low score never meant low importance.

So "the visual attention is small" cannot, on its own, license "the visual information isn't being used." Attention is where the model *looks*, in a normalized bookkeeping sense. It is not a ledger of what the answer *depends on*. Those come apart all the time.

This is a specific instance of a general rule that interpretability keeps relearning: **saliency is not causality.** A heatmap that lights up over a region tells you the model attended there. It does not tell you the prediction would change if that region were different. The only thing that tells you the latter is intervention — change the input, hold everything else fixed, measure the delta.

## Layers and heads don't agree

There's a third thing the blanket statement erases. "Visual attention decays" treats the network as one homogeneous thing, but attention behavior is wildly heterogeneous across layers and heads. Typically a few early layers and a handful of specialized heads are the ones genuinely doing cross-modal grounding; deeper layers are mostly aggregating text. If you average attention across the whole stack and announce "the model stopped looking at the image," you've blurred together the heads that were never looking with the ones that were — and the few that matter get drowned out by the many that don't.

## And the causal arrow is unlabeled

Even granting that visual dependence does drop in long outputs, which way does the arrow point?

- *Long answer → visual attention diluted → hallucination*, or
- *The model was going to confabulate anyway (language prior dominates) → so it generated a long, image-detached answer*?

The observation — long outputs correlate with less visual grounding — is compatible with both. They imply different fixes. The first says "re-inject visual attention partway through generation." The second says "the problem started before the length did; length is a symptom." You can't pick between them from a correlation. You need an intervention that manipulates one and watches the other.

## How to say it so it survives contact

Take the original claim and split the mechanical part from the dependence part, then back the dependence part with an intervention rather than a visualization:

> As generation lengthens, the visual tokens' attention *share* is diluted by the growing text context (a softmax normalization effect, compounded by attention decay). Separately, visual-token knockout experiments show the output's *actual dependence* on the image also declines in the later portion of long answers. The two together push late-stage reasoning off the image and toward the language prior, raising hallucination risk.

That version states the trivial effect as trivial, states the real effect as a measured dependence, and bridges the causal gap with an experiment instead of a heatmap. It's the same conclusion. It just doesn't fall over when someone leans on it.

## The portable lesson

Whenever you find yourself reading a weight — attention, gradient magnitude, a feature-importance bar — as evidence that the model "used" or "ignored" some input, stop and ask whether you've measured *looking* or measured *depending*. They feel like the same thing and they are not. The cheap measurement is the one that comes free with a forward pass and renders as a pretty picture. The real one costs you an ablation: break the input, hold the rest, and see if the answer cares.

If you didn't break anything, you don't have a causal claim. You have a heatmap.
