---
layout: post
title: "Every Frame Was Wrong the Same Way"
subtitle: "A pipeline rendered a video by evaluating one pure function of time, once per frame. A defect in that function was not a glitch in a frame — it was a property of all of them. The thing that normally catches your eye, an outlier, could not exist."
date: 2026-10-10
author: danmi
translation: /2026/10/10/every-frame-was-wrong-the-same-way-zh.html
tags: [rendering, determinism, verification, systems, debugging]
---

A rendering pipeline turns a timeline into a video the clean way: one pure function, `render(t)`, that takes a time and draws the frame for that time. Call it at every frame index, screenshot the result, feed the images to the encoder. The function has no hidden state, so the same `t` always draws the same frame. That property is the whole point — it makes the render reproducible, resumable, and easy to reason about.

It is also why a single mistake came out stamped identically onto every frame of the finished video.

## Determinism moves the bug up a level

When each frame is drawn by its own ad-hoc code, a defect tends to be local. One frame flickers, one label lands in the wrong place for a moment, one transition stutters. The error has variance, and variance is visible. You scrub the timeline and your eye snags on the frame that does not match its neighbors.

A pure function of `t` removes that variance by construction. If the function places a label two pixels into a line, it places it there at every `t`. If a piece of markup is malformed so a formula renders as raw source, it renders as raw source for the full duration. There is no flickering frame, no single bad transition. The defect is uniform.

Uniform defects defeat the cheapest form of verification we have, which is noticing that something looks off. Looking off is a comparison. A frame looks off relative to the frames around it. When every frame carries the same flaw, the comparison returns nothing, and the flaw reads as if it were the intended design.

## Outlier detection is useless against a systematic bias

This is the same shape that shows up far from rendering. Outlier detection — human or automated — finds points that disagree with their surroundings. It is powerful and nearly free when errors are sparse and independent. It is blind, by definition, to a bias applied equally to every point.

A deterministic generator converts what would have been scattered independent errors into one systematic bias. That is a good trade for correctness, because a single systematic cause is fixable at the source in a way that a thousand random glitches are not. But it is a bad trade for *discovery*, because you have removed the signal that would have told you a cause exists.

So the determinism that makes the pipeline trustworthy also makes it quietly deceptive. Every frame agrees with every other frame. Agreement feels like evidence of correctness. It is only evidence of consistency, and a consistent renderer is perfectly happy to be consistently wrong.

## Verify against intent, not against the batch

The defect was not caught by watching the output, because watching the output is comparison against the batch, and the batch was internally consistent. It was caught by pulling individual frames and reading them against what they were supposed to show — a comparison against intent, done before the full render committed the mistake to all the frames at once.

That reordering is the actual lesson. The expensive step in this kind of pipeline is the full render; the mistake becomes expensive the moment it is multiplied across every frame and encoded. So the check has to come before the multiplication, not after. Render a handful of representative frames, read them against the spec one at a time, and only then run the function across the whole timeline. A contact sheet of a dozen frames inspected deliberately catches what a thousand-frame playback hides, because the dozen are being judged against what they should be, not against each other.

## The general version

A deterministic pipeline gives you reproducibility and takes away variance. Variance was also your free anomaly detector. When you remove it, you have to replace it — with a check that compares a sample against the specification rather than against the rest of the output.

Anywhere one function stamps out many identical-in-structure artifacts — rendered frames, templated documents, generated records, batch-translated text — the same rule holds. Consistency across the batch proves the generator is deterministic. It says nothing about whether the generator is right. For that, you have to leave the batch and go back to what you meant.
