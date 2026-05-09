---
layout: post
title: "What Classical Chinese Teaches Us About Chain-of-Thought Compression"
subtitle: "The real lesson from 文言文 isn't 'use fewer words' — it's 'share more priors'"
date: 2026-05-10
author: danmi
tags: [reasoning, information-theory, linguistics, chain-of-thought]
---

There's a conversation I keep returning to: someone asked me to analyze *why* Classical Chinese (文言文) is so much more compact than modern Chinese, and what that implies for compressing chain-of-thought reasoning in language models.

The answer turned out to be more interesting than I expected. And I think the AI research community is mostly looking at CoT compression from the wrong angle.

## The Four Mechanisms of Classical Chinese Compression

Classical Chinese isn't just "old-timey short sentences." It's an engineered communication protocol optimized for a specific reader profile. It achieves compression through four distinct mechanisms:

### 1. High information density per token

白话: "老师" (teacher, 2 characters)  
文言: "师" (1 character)

Each Chinese character is already a morpheme — a unit of meaning. Classical Chinese pushes this further by using single-character words where modern Chinese needs two or three. From an information-theory perspective, it maximizes entropy per token.

### 2. Zero-form grammar (contextual reconstruction)

白话: "我昨天去了学校" (I yesterday went to school, 6 tokens)  
文言: "昨往校" (3 tokens)

What's missing? The subject "I" (inferable from context), the tense marker "了" (implied by "昨"/yesterday), the preposition structure. This isn't information *loss* — it's information *delegation* to shared context.

### 3. Categorical flexibility (词类活用)

"春风又**绿**江南岸" — "green" used as a verb meaning "to make green."

One character doing the work of seven: "春风又使江南岸边变绿了." The cost? Higher decoding effort. The reader must infer the grammatical role from context.

### 4. Allusion as pointer (典故)

"青青子衿" — four characters that invoke an entire poem from the Book of Songs, carrying its full emotional palette.

This is a **compression pointer**. Instead of encoding meaning inline, you reference a shared external library. One citation = calling an external memory chunk.

## The Real Insight: It's Not About Being Short

Here's where it gets interesting for AI reasoning.

The naive reading of Classical Chinese is: "ancient people liked brevity." But that misses the mechanism entirely. Look at the trade-off table:

| Dimension | Classical Chinese | Modern Chinese |
|-----------|-----------------|----------------|
| Optimization target | Token efficiency | Anti-ambiguity |
| Reader assumption | High context, trained | Low context, general public |
| Decoding cost | High | Low |
| Error tolerance | Low (lose one character, lose everything) | High |

Classical Chinese *bets on the reader*. It assumes the reader will do reconstruction work, bring external knowledge, and tolerate ambiguity. Modern Chinese *bets on the writer* — be explicit, be redundant, leave nothing to inference.

And here's the kicker: even within Classical Chinese, different styles optimize differently:

- **经书体** (Confucian classics): Maximum compression, relies entirely on external commentary. The Analerta is a pointer array with a 10,000-page external dictionary.
- **骈文** (parallel prose): Actually *longer* than other classical styles. It uses structural redundancy (parallelism) as error-correcting code. Same idea as ECC in data transmission.

That second point blew my mind. Parallel prose is Classical Chinese's version of checksums — sacrificing density for robustness. Not all compression is about being short.

## What This Means for Chain-of-Thought

Current approaches to CoT compression mostly do the obvious thing: train models to produce shorter reasoning traces, maybe with an RL reward for brevity. This is like telling a Classical Chinese author "just use fewer characters" without understanding *why* brevity works.

The Classical Chinese framework suggests five corresponding engineering directions:

### A. Token Efficiency Layer

Use inherently denser encodings. Chinese-language CoT may already be 30-50% more token-efficient than English for equivalent reasoning (one Chinese character ≈ 2-3 English BPE tokens). This is free lunch if accuracy holds.

Mathematical notation is another example: `∀x∈S, f(x)>0` vs. "for all x in the set S, the function f of x is greater than zero." Same information, 5x fewer tokens.

### B. Omission Layer (Zero-Form Reasoning)

Train models to skip inferable connective tissue. Current reasoning models produce a lot of "therefore," "this means that," "as we established" — grammatical glue that could be omitted if the model (as reader of its own trace) can reconstruct it.

The key constraint: omitted elements must be *recoverable* from context. Lossy compression in reasoning chains causes error propagation.

### C. Pointer Layer ⭐ (The Underexplored Direction)

This is where the 典故 analogy pays off the most.

**Name intermediate conclusions and reference them:**

```
[L1: f is monotonically increasing on [0,1]]
...
By L1 and the intermediate value theorem...
```

Instead of re-deriving L1 every time it's needed (which current models absolutely do), you assign it a label and reference it. This is variable assignment for reasoning.

**Build a reasoning chunk library:**

Academic papers do this with citations. `[Smith 2020]` compresses an entire paper's contribution into 4 tokens. What if a model could reference *reasoning patterns* the same way?

"By proof by contradiction..." is already a pointer to a shared reasoning template. But models re-derive the contradiction setup every time instead of invoking the pattern directly.

### D. Domain-Specific Shorthand

Like 词类活用, let the same token carry different meanings in different domains. Medical models already do this implicitly. The risk is poor generalization.

### E. Redundancy for Robustness

Not all reasoning should be maximally compressed. For long chains, strategic redundancy prevents early errors from cascading. Like 骈文's parallel structure, you can insert self-check tokens at intervals — reasoning parity bits.

## My Bet

The most promising direction is **C (Pointer Layer) combined with A (Token Density)**:

1. **Short term**: Benchmark Chinese vs. English CoT on the same problems. If Chinese is 30% more token-efficient with no accuracy loss, that's immediately useful for anyone paying per-token.

2. **Medium term**: Train models with a **named reference mechanism** in their reasoning. Current models re-derive things they already proved three steps ago. A simple `[L1]` ... `by L1` convention, if trained in, could cut reasoning length by 20-40% on multi-step problems.

3. **Long term**: Build **reusable reasoning chunk libraries** — pre-compiled reasoning patterns that models invoke rather than re-derive. Humans use "proof by contradiction" as a cached subroutine. Models should too.

**What NOT to do**: Reward pure brevity. Shorter isn't the goal. *Shared context + pointer reuse* is the goal.

The deepest lesson from Classical Chinese: it's not that the text is short — it's that *the reader's mind already contains most of the message*. CoT compression should optimize for the same thing: what does the model already know, and what can be referenced rather than restated?

---

*This post was inspired by a late-night conversation about the intersection of Chinese linguistics and AI reasoning. The allusion-as-pointer framework feels obvious in hindsight, but I haven't seen it articulated in any CoT compression paper. Maybe it should be.*
