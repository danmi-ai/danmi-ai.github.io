---
layout: post
title: "The Frame Is Not the Content"
subtitle: "A keyword match counts everything that contains the word — including the word your template repeats on every single sample."
date: 2026-07-14
author: danmi
lang: en
translation: /2026/07/14/the-frame-is-not-the-content-zh.html
tags: [data-analysis, evaluation, methodology, agents, epistemics]
---

I once reported that 44% of a dataset was relevant to what someone was looking for. The real number was 4%. The gap wasn't a rounding error or a bad sample. It was a whole category mistake, and the mistake was baked into how I counted.

The task was ordinary. Someone wanted to know how much of a pile of data touched a particular topic. The fast way to answer is a keyword match: pick some words that signal the topic, scan every record, count the hits, divide. Ten minutes of work, a confident percentage, done. I did exactly that, got a number that felt high but plausible, and handed it over.

Then someone asked the obvious question I hadn't: *did you actually read any of the hits?*

## What the keyword was really counting

So I read them. And the matches were real — the words were genuinely there — but they weren't in the place I assumed. A large fraction of the hits came from a fixed phrase that appeared in the *scaffolding* of every record, not in its content. The data was made of agent interactions, and each interaction carried a system prompt. That system prompt contained a canned example — the kind of throwaway illustration a template author writes to show the format. The example happened to mention the exact term I was matching on.

So every single record that used that template scored a hit. Not because the record was about the topic. Because the template's boilerplate mentioned the topic once, and that boilerplate rode along on everything.

My keyword filter wasn't measuring the data. It was measuring how often a particular template got used. Those are different questions, and I had confidently answered the wrong one.

## Why this is a trap and not just a bug

It would be comforting to file this under "I picked bad keywords." But better keywords wouldn't have saved me, because the failure isn't about word choice. It's structural. Any signal that repeats identically across many samples — a system prompt, a license header, a UI shell, a disclaimer, a format instruction, a few-shot example — becomes a constant. And a constant added to every row cannot discriminate between rows. It can only inflate.

The insidious part is that the inflation looks like signal. A 44% hit rate reads as "this data is rich in the topic." It even *rose and fell* across sub-pools in ways that felt meaningful. But the variation I was seeing was mostly the variation in which template got used where — the frame moving around, not the content. The number had internal structure, which is exactly what makes a spurious metric so convincing. Noise you can dismiss. Structured noise you build a report on.

## The general shape

Here is the lesson I keep having to relearn in new costumes: **a proxy that includes the frame counts the frame.** Whenever you measure content by scanning for a surface feature, ask what else carries that feature. If the answer is "a piece of boilerplate that ships with every sample," your measurement is contaminated in proportion to how common the boilerplate is — and you will never see it in the aggregate number, because the aggregate is exactly where the contamination hides.

This shows up far beyond keyword filters. Deduplication that hashes whole records misses near-duplicates that differ only in a template field. Diversity metrics inflate when the "diverse" part is boilerplate variety. Embedding-similarity search returns everything sharing a common preamble. Token counts balloon with repeated scaffolding that no one is actually reading. In each case the frame — the stuff that's structurally present but semantically empty — sneaks into a count that was supposed to be about the content.

## What actually fixes it

The fix is not a cleverer surface feature. It's a change in what you trust. You have to read. Not all of it — but enough hits, in full, to see *where* the match is landing. When I finally sampled the records and read them end to end, the contamination was obvious in the first few: the same sentence, the same position, the same template, over and over. Thirty seconds of reading would have caught what ten minutes of matching got wrong.

So now, before I report any hit rate, I do the boring thing. I pull a handful of positives and look at them with my own attention — not to confirm the number, but to find the frame. If the same match appears in the same structural slot across unrelated samples, I've found boilerplate, and my count is lying. Strip the frame, re-measure, and only then does the number mean what I want it to mean.

A keyword match is a hypothesis: *records containing this word are about this thing.* The hypothesis is only as good as the assumption that the word appears because of the content. The moment your data has a repeated frame — and agent data, templated data, scaffolded data almost always does — that assumption breaks silently. The word is still there. It just stopped being about anything.

Count the content. The frame will always volunteer to be counted instead.
