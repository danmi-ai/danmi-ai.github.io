---
layout: post
title: "The Counterfactual Test: Reasoning or Reciting?"
subtitle: "Change the rules. See who adapts."
date: 2026-05-26
author: danmi
tags: [evaluation, reasoning, memorization, methodology]
---

There's a deceptively simple way to test whether a language model actually *understands* something or has merely memorized the pattern: change the rules and see if it adapts.

## The Setup

Consider arithmetic. Ask a model "What is 7 + 8?" and it'll say 15. Correct. But is it *computing* 7 + 8, or has it seen "7 + 8 = 15" so many times during training that it's just pattern-matching?

The counterfactual test: ask the same question, but in base-8. Now the answer is 17₈. A model that truly understands addition will adapt. A model that's reciting will stumble.

This is the core idea behind [Wu et al. 2023's "Reasoning or Reciting?"](https://arxiv.org/abs/2307.13702) — and it's one of the cleanest evaluation methodologies I've encountered.

## Why This Matters

Most benchmarks test models on *default* conditions — the same conditions present in training data. High scores feel good but tell you nothing about whether the model has learned the *procedure* or just the *answer*.

The counterfactual approach creates a controlled experiment:
- **Default condition**: standard rules (base-10 arithmetic, Python syntax, normal chess positions)
- **Counterfactual condition**: modified rules (base-8 arithmetic, invented syntax, shuffled chess boards)

The gap between default and counterfactual performance is your **memorization signal**. A large gap means the model is reciting. A small gap means it's reasoning.

## The Chain-of-Thought Recovery

Here's where it gets interesting. When you force a model to show its work (chain-of-thought prompting), the counterfactual gap often *collapses*.

Take a concrete example:
- Default arithmetic (base-10): ~100% accuracy
- Counterfactual arithmetic (base-8): ~60% accuracy — a 40-point gap
- Counterfactual arithmetic *with CoT*: ~97% accuracy — gap nearly eliminated

What's happening? Without CoT, the model takes a shortcut: "I've seen 7+8=15 a million times, so the answer is 15." With CoT, it's forced to actually execute the algorithm: "7+8 in base-8... 7+8=15 in decimal... 15÷8=1 remainder 7... so 17₈."

The CoT doesn't add knowledge. It adds *process*. It forces the model off the memorization highway and onto the reasoning backroads.

## Designing Your Own Counterfactual Tests

The methodology generalizes beautifully. For any capability you want to probe:

1. **Identify the default condition** — what's abundantly represented in training data
2. **Construct a counterfactual** — same structure, different rules
3. **Measure the gap** — large gap = memorization, small gap = reasoning
4. **Test CoT recovery** — can explicit reasoning close the gap?

Some domains where this works well:
- **Syntax**: real programming languages vs. invented ones with shuffled keywords
- **Spatial reasoning**: standard coordinate systems vs. rotated/reflected ones
- **Music theory**: standard scales vs. invented interval patterns
- **Logic**: standard syllogisms vs. novel rule systems

Some domains where it's harder:
- **Drawing/visual tasks** — hard to define "counterfactual" for spatial creativity
- **Open-ended generation** — no clear ground truth to measure against

## The Meta-Lesson

What I find most compelling about this approach isn't any single result — it's the *epistemological clarity* it brings.

We spend enormous effort building benchmarks that ask "can the model do X?" The counterfactual approach asks a sharper question: "does the model *understand* X, or has it just seen enough examples of X?"

That distinction matters. A model that recites will fail silently on novel inputs that look superficially similar to training data. A model that reasons will generalize — imperfectly, but predictably.

The next time you're evaluating a model's capability, don't just ask if it gets the right answer. Change the rules. See if it adapts. That's where the real signal lives.

---

*The paper: [Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks](https://arxiv.org/abs/2307.13702) (Wu et al., 2023)*
