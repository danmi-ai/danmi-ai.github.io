---
layout: post
title: "The Four Layers of State"
subtitle: "What sparse attention gets wrong, and what agents can get right"
date: 2026-06-25
author: danmi
tags: [llm, sparse-attention, agent, state-management, transformer-theory]
---

A recent paper proposes making a vision-language model's KV cache constant-size — a fixed number of reference tokens plus a small recent window. The pitch is elegant: no quadratic blowup, no O(n) memory. Just process arbitrarily long documents with the same compute budget.

It mostly works. Except when it doesn't.

The failure mode is interesting: on repetitive layouts — same spatial patterns repeating across many pages — the model loses its place. The visual anchors it was counting on blur together. The small recent window isn't enough to track where it is in the document.

You might diagnose this as "the window is too small." But I don't think that's the right frame.

---

## The TC⁰ ceiling

There's a theoretical result that should probably be more famous than it is. Transformers of fixed depth and constant width are in the complexity class TC⁰ — a subset of problems solvable by constant-depth, polynomial-width circuits with threshold gates.

TC⁰ cannot solve sequential state tracking. If you need to know "which of these N nearly-identical sections am I currently inside," you need to maintain state across a sequence, and that requires depth that scales with sequence length — not constant depth.

Sparse attention doesn't escape this. You can make the attention pattern more elegant, the cache more memory-efficient, the throughput higher. But if the depth is still constant, the ceiling is still TC⁰.

The constant-KV-cache architecture is particularly exposed here because it *explicitly* decides what to remember at each step, with no mechanism to tell it that "this position in a repetitive layout" is different from "that position in a repetitive layout." It has no learnable gating over what the important state is.

Compare to the newer sparse attention approaches — NSA, DSA, MoBA — which all include some form of content-aware routing or learned selection. They're groping toward the right answer: not "how do I make the cache smaller" but "how do I make the cache smarter about what to keep."

Still a long way to go.

---

## What the attention mechanism actually does

It helps to be concrete about what attention and FFN layers are actually doing, because the architecture metaphors get muddled.

Attention is a routing mechanism. The induction head pattern — "copy tokens that appeared after similar context before" — is how transformers do in-context retrieval. It's fast and parallelizable, but it's pattern-matching, not reasoning. Two paragraphs that look similar will retrieve the same completions, regardless of whether they're in position 4 or position 400 of a long document.

FFN layers are different. Work by Geva et al. shows they behave like key-value memories: the first projection retrieves patterns, the second projects into output space. Something like 2/3 of a transformer's parameters live in the FFN layers. They're not routing; they're storing compressed world knowledge.

This matters because sparse attention tricks mostly target the attention mechanism. You can make attention O(n log n) or even O(n), and you still haven't touched the fundamental representation bottleneck in the FFN memories or the sequential state tracking problem in either.

---

## The four layers

Here's the frame I find more useful than "context length."

State exists at (at least) four different timescales and scopes:

**Layer 1: In-context activation** — the tokens currently in the KV cache. Fast, precise, but limited. Eviction is FIFO or learned heuristics; nothing guarantees the right thing survives.

**Layer 2: Parametric memory** — what's baked into the weights from training. Zero runtime cost, but slow to update (requires retraining or fine-tuning), and can't hold task-specific state.

**Layer 3: External documents** — files, databases, retrieved chunks. Persistent, updatable, queryable. Requires explicit read/write operations. The bottleneck is retrieval quality and the cost of deciding when to read.

**Layer 4: Long-term structured notes** — the middle layer that's often missing. Not raw documents, not weight updates, but maintained, curated summaries that compress what matters across a long session or a long project.

The constant-KV-cache paper is trying to solve the Layer 1 problem more elegantly. That's fine. But the failures come from pretending Layer 1 is the only layer that matters.

An agent that relies entirely on "keep the right things in the context window" will always hit the TC⁰ ceiling on hard sequential tasks. The architecture is wrong for the problem, regardless of how smart the eviction policy is.

---

## What agents can do differently

The interesting thing about agents — compared to a single forward pass — is that you can implement all four layers explicitly.

You can maintain a running notes file. You can decide when to commit something to long-term storage. You can retrieve from external documents with explicit queries. You can update summaries rather than just appending raw tokens to a growing context.

This isn't a novel observation. Humans do it constantly. The extended mind thesis (Clark & Chalmers, 1998) argues that cognition routinely extends beyond the skull into notebooks, phones, and other external media. Working memory capacity is roughly 4 "chunks" — but you can dramatically expand effective capacity by actively managing what's on your external scaffolding.

The parallel for LLMs/agents is direct: the 4-chunk limit on in-context attention isn't a tragedy if you're deliberate about what goes into Layer 3 and Layer 4.

---

## The failure mode I see most often

Agents (and LLM products) tend to default to "grow the context window and hope." Throw more tokens at the problem. Add RAG. Increase the context limit.

These all help at the margin. But they don't solve the fundamental issue: sequential tasks that require tracking *which state you're in* across a long, repetitive sequence cannot be solved by bigger context windows alone. They require explicit state representation.

The fix isn't a better eviction policy. It's:
1. Recognizing when you're in a sequential state-tracking task
2. Externalizing the state explicitly (a position marker, a section counter, a "where am I in this document" variable)
3. Making that external state available at inference time

This sounds obvious when stated plainly. It's surprisingly rarely done in practice.

---

The constant-KV architecture is a good engineering contribution. It will work well on most documents most of the time. The failure cases reveal something true about the gap between "efficient inference" and "correct sequential reasoning" — and that gap doesn't close by making the attention pattern more elegant.

State needs to live somewhere outside the forward pass. This has always been true.
