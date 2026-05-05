---
layout: post
title: "Context-Aware Hashing: A Better Primitive for Text Deduplication"
subtitle: "When one parameter does the work of two"
date: 2026-05-06
author: danmi
tags: [deduplication, bloom-filter, algorithm-design, data-engineering]
---

Most text deduplication pipelines for large-scale corpora use some variant of the same idea: hash text units, store them in a space-efficient structure (usually a Bloom filter), and flag collisions as duplicates. The devil is in how you define "text unit."

## The Naive Approach: Per-Sentence Hashing

The simplest scheme (call it **Scheme A**) hashes each sentence independently:

```python
for sentence in document:
    if sentence in bloom:
        mark_duplicate(sentence)
    else:
        bloom.add(sentence)
```

This works. It catches exact sentence-level duplicates across a corpus of billions of documents. But it has a known failure mode: **short-sentence false positives**.

Common phrases like "Thank you", "See below", or "Chapter 1" appear in millions of documents. They're not duplicated *content*—they're just common language. Scheme A can't distinguish "this sentence is duplicated because two documents copied the same paragraph" from "this is just a frequently-occurring phrase."

The standard fix: add a `min_length` parameter. Skip sentences shorter than, say, 10 characters.

```python
for sentence in document:
    if len(sentence) < min_length:
        continue  # skip short sentences entirely
    if sentence in bloom:
        mark_duplicate(sentence)
    else:
        bloom.add(sentence)
```

This introduces a tradeoff. Set `min_length` too high and you miss real duplicates that happen to be short. Set it too low and you get false positives on common phrases. Two parameters to tune (`min_length` + Bloom size), each pulling in different directions.

## The Greedy Merge Approach: Alignment-Dependent Keys

A more sophisticated scheme (call it **Scheme B**) tries to build longer keys by merging consecutive sentences until hitting a character threshold:

```python
idx = 0
while idx < len(sentences):
    fragment = sentences[idx]
    while len(fragment) < threshold and more_sentences:
        idx += 1
        fragment += sentences[idx]
    check_and_store(fragment, bloom)
    idx += 1
```

The motivation is sound: longer keys have lower collision probability, so false positives drop. But this design has a **structural flaw**: keys are alignment-dependent.

Consider two documents that share the same four paragraphs, but Document B has one extra sentence at the beginning. Because fragment boundaries are determined by iterating from position 0, that one extra sentence shifts *every subsequent fragment boundary*. The same content gets merged into different keys. **Zero hits.** Not an edge case—any difference in preceding context cascades into total misalignment.

In real corpora, over half of duplicate pairs differ in their opening (different headers, source attributions, navigation text, timestamps). A scheme that depends on identical alignment from the start of the document will systematically miss these.

## The Sliding Window: Context-Aware Hashing

Here's the better primitive (**Scheme C**): generate a key starting from *every* sentence position, merging forward until hitting the threshold.

```python
for i in range(len(sentences)):
    fragment = sentences[i]
    j = i
    while len(fragment) < threshold and j + 1 < len(sentences):
        j += 1
        fragment += sentences[j]
    
    if fragment in bloom:
        mark_duplicate(sentences[i:j+1])
    else:
        bloom.add(fragment)
```

What makes this design elegant is that **one parameter (threshold) simultaneously serves two purposes**:

1. **Controls key length** → longer keys have exponentially lower false-positive probability in the Bloom filter
2. **Implicitly enforces minimum length** → a 2-character sentence like "OK" is never stored alone; it's always merged with its following context before being hashed

A short sentence in different contexts produces different keys:
- "OK" + "I'll handle it right away." → key₁
- "OK" + "The design looks good to me." → key₂

Same sentence, different keys—no false positive. But if the same short sentence appears with the same following context in two documents, the keys match—correct detection.

**Scheme C eliminates the min_length/threshold tradeoff entirely.** You don't need to decide "should I skip short sentences or risk false positives?" The sliding window answers both questions with a single threshold value.

## The Tradeoff Table

| Property | A (per-sentence) | B (greedy merge) | C (sliding window) |
|----------|:-:|:-:|:-:|
| False positive rate | Higher (short keys) | Lower | Lower |
| Recall on misaligned duplicates | ✓ High | ✗ Breaks on offset | ✓ High |
| Parameters to tune | 2 (min_length + bloom size) | 1 (threshold) | 1 (threshold) |
| Short-sentence handling | Needs explicit filter | Built-in (merge) | Built-in (merge) |
| Bloom entries | ~N sentences | ~N/k fragments | ~N entries |
| Implementation complexity | Trivial | Medium | Trivial |

## The Meta-Lesson

This is a recurring pattern in algorithm design: **a well-chosen representation can collapse multiple parameters into one.**

Scheme B tried to solve the false-positive problem by making keys longer, but introduced alignment-dependency as a side effect. Scheme C achieves the same key-length benefit while preserving position-independence—because it generates keys from every possible starting position, not just from where the previous fragment ended.

The insight isn't that sliding windows are novel (they're not). It's that in this specific problem, the sliding window approach lets a single `threshold` parameter do double duty as both "minimum information content" and "key length for collision resistance." Whenever you find yourself tuning two knobs that fight each other, look for a reformulation where one knob naturally handles both.

---

*This post was prompted by thinking through deduplication strategies for training data. The specific schemes are simplified for clarity—real systems add content-defined chunking, MinHash for fuzzy matching, and various optimizations. But the core design choice between per-unit hashing, greedy merging, and sliding-window generation applies at every scale.*
