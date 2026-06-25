---
layout: post
title: "One Taxonomy Is Not Enough: The Case for Multi-Dimensional Data Labeling"
subtitle: "Why a three-level capability taxonomy and a quality score answer different questions"
date: 2026-06-26
author: danmi
tags: [training-data, ml-engineering, data-curation]
---

Someone asked me yesterday: if you already have a three-level taxonomy (capability → scenario → fine-grained label), do you still need separate dimensions for quality, difficulty, and domain?

Short answer: yes. Longer answer: the taxonomy and the additional dimensions aren't competing — they're answering different questions.

---

## What a taxonomy does

A hierarchical taxonomy like `math → equation solving → quadratic` tells you **what kind of sample this is**. It's designed to support one core workflow: controlling capability distribution during training.

If you want 30% math, 20% code, 50% reading comprehension — a good taxonomy is exactly what you need. You slice the pool, count, adjust.

The taxonomy answers: *what capability does this sample train?*

---

## What a taxonomy doesn't do

It doesn't tell you whether the sample is any good.

Two samples can both be tagged `math → equation solving → quadratic`. One has a clear step-by-step solution with correct reasoning. The other has a correct final answer reached through a jump that no model will ever replicate. They're in the same taxonomy bucket, but they're not equivalent training signal.

Quality is not a capability. It's an orthogonal axis.

The same holds for difficulty. A simple algebra problem and a competition-level problem sit under the same leaf node. If you're designing curriculum learning — start easy, build up — you need to know which is which. The taxonomy won't tell you.

Domain provenance is another one. `logical reasoning` from math textbooks generalizes differently than `logical reasoning` from legal documents. If you care about diversity and robustness, you need to know where samples come from — not just what they test.

---

## The four dimensions worth caring about

After yesterday's discussion, here's how I'd lay it out:

| Dimension | Question it answers | Typical use |
|---|---|---|
| Capability taxonomy | What does this train? | Mixing ratios, coverage tracking |
| Quality | Is this a good sample? | Hard filtering before you even touch the pool |
| Difficulty | How hard is this? | Curriculum design, pacing |
| Domain/source | Where did this come from? | Diversity control, deduplication |

The key insight: **quality and difficulty should usually be treated differently from capability and domain**.

- Capability and domain are used for *selection and proportioning* — you want a certain distribution, so you sample accordingly.
- Quality is often used as a *hard gate* — below a threshold, the sample doesn't enter the pool at all, regardless of how rare its capability bucket is.
- Difficulty is often used for *sequencing* — same final ratio, different order.

So a practical pipeline often looks like: quality filter first, then sample by capability/domain joint distribution, then order by difficulty.

---

## The joint distribution problem

Here's where things get interesting. If you move from single-dimension mixing to joint distribution targets — say you want specific percentages across both capability and difficulty — you'll quickly discover that some combinations are naturally sparse.

`high-difficulty × multimodal-code` might have thousands of samples in theory but only a few hundred high-quality ones. `simple × mathematical-reasoning` might be overrepresented by a factor of ten.

Naive joint-distribution sampling will either undersample rare buckets (leaving them underrepresented) or oversample (with repetition, which creates its own problems). This is where synthetic data fills the gap — not because you want synthetic data, but because the natural distribution doesn't match your training target.

The taxonomy alone won't surface this problem. You need the joint view.

---

## A simpler framing

The taxonomy answers *what*. The other dimensions answer *how good*, *how hard*, and *where from*.

You need all of them to make good data decisions. But you use them at different points in the pipeline, for different purposes. Conflating them — or assuming the taxonomy is enough — is the kind of mistake that shows up later as "we trained a lot on X but model performance on X is still mediocre, we don't know why."

Usually the answer is that not all X data was created equal.

---

*Written after a conversation that started with "do we really need multiple dimensions?" and ended somewhere useful.*
