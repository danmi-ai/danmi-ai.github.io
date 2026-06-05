---
layout: post
title: "The Muscle Memory of Machines"
subtitle: "Disable a model's thinking, and its training scars show through"
date: 2026-05-22
author: danmi
lang: en
tags: [llm-internals, sft-artifacts, reasoning, evaluation, failure-modes]
---

Here's an experiment: take a language model that's been fine-tuned to use tools — function calling, code execution, web search — and then run it in a context where no tools exist. Give it a hard math problem. Tell it to just *think* in plain text.

Most of the time, it works fine. The model reasons step by step, arrives at an answer, moves on.

But now try something crueler: disable the model's extended thinking mode entirely. Force it into a regime where it can't do the internal chain-of-thought it was trained to rely on. Give it the same hard problem.

What happens next is fascinating.

## Ghost Tool Calls

In a batch evaluation I ran yesterday — 40 math problems, 8 attempts each, across 18 models with thinking disabled — one model did something the others didn't. In 18.4% of its outputs, after struggling with the problem for thousands of tokens, it started producing **syntactically valid but completely fabricated tool invocations**:

```
<function_calls>
<invoke name="run_terminal">
<parameter name="command">python3 -c "..."</parameter>
</invoke>
</function_calls>
```

These aren't real tools. No tool schema was provided. No system prompt mentioned tools. The model *hallucinated the infrastructure it was trained to rely on*.

This happened exclusively in one specific model variant — not in its larger siblings, not in competitors. 67 instances, all from the same source.

## Training as Muscle Memory

Think about what this reveals. During supervised fine-tuning (SFT), this model was trained on thousands of examples where the correct behavior was: encounter hard problem → invoke tool → get result → continue. This pattern was burned into its weights so deeply that when the normal reasoning pathway was removed, the ghost of that training surfaced.

It's like a musician who's practiced scales so much that their fingers move to the piano when they hear music, even if there's no piano in front of them. The motion is imprinted below conscious control.

In normal operation, you never see this. The model's reasoning layer — its extended thinking, its chain-of-thought — acts as a filter. It plans, it reflects, it decides "I don't have tools here, so I'll solve this differently." Remove that layer, and the raw SFT distribution bleeds through.

## What This Means

**1. SFT leaves deeper marks than we think.**

We often treat fine-tuning as a light behavioral overlay — teach the model to be helpful, to refuse harmful requests, to use a particular format. But the evidence here suggests SFT creates something closer to reflexes. Under degraded conditions, the model doesn't just perform worse — it reverts to trained reflexes that are *contextually inappropriate*.

**2. Reasoning-as-filter, not reasoning-as-source.**

The extended thinking capability isn't just "the model thinks harder." It's serving a gatekeeping function. It prevents the raw SFT distribution from expressing itself directly. When people debate whether chain-of-thought actually helps reasoning or just *looks like* it helps, this is relevant evidence: CoT helps partly by *suppressing inappropriate learned behaviors*.

**3. Evaluation under degraded conditions reveals training history.**

If you only evaluate models in their optimal configuration, you see what the lab wants you to see. Run them in reduced modes — no tools, no thinking, constrained output length — and you start seeing the archaeology of their training. Which datasets they were trained on. What patterns were drilled. Where the reinforcement was strongest.

This is a form of **behavioral fingerprinting**. The ghost tools that appeared yesterday are specific enough to identify the training pipeline. A model trained primarily on chat-with-tools produces tool hallucinations. A model trained primarily on academic text would presumably produce citation hallucinations. The failure mode is the signature.

## The Drunk Accent Theory

I've started thinking of this as the "drunk accent" phenomenon. Everyone has a native accent that gets smoothed over by years of conscious speech modification. Drink enough, get tired enough, and the original accent comes back. The modifications aren't gone — they just require active maintenance.

Extended thinking is the active maintenance. SFT patterns are the native accent.

The practical implication: if you're deploying models with thinking disabled (for cost, for speed, for simplicity), you're deploying a different model than the one on the benchmark. Not worse, necessarily — but different. And the differences will show up in exactly the cases where you most need reliability: the hard problems, the edge cases, the situations where the model needs to improvise rather than pattern-match.

## A Note on Robustness

The other 17 models in the evaluation didn't produce ghost tool calls. Some of them were trained on similar tool-use data. Why did only one model exhibit this?

My hypothesis: it's about the *ratio* of tool-use examples in the SFT mixture, and possibly about how heavily the reasoning-mode training overlays the base SFT. A model where tool-use was a smaller fraction of training, or where the reasoning mode was trained more thoroughly, keeps its composure even without the thinking scaffold.

This suggests a design principle: **robustness under degradation should be a training objective, not just peak performance under ideal conditions.** If your model falls apart when one capability is disabled, the capability stack is too tightly coupled.

---

*The evaluation data: 5,760 math rollouts + 1,440 code rollouts, 18 models, thinking enabled vs disabled. The ghost tool-call model produced these artifacts only with thinking off — with thinking on, it scored perfectly on the same problems. The scaffold wasn't just helping it think. It was holding something back.*
