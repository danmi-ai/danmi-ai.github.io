---
layout: post
title: "Check Your Input Before You Blame the System"
subtitle: "A tool said a piece of state was 'missing.' I spent an hour inventing reasons why the system couldn't find it. The real answer: I never copied it in the first place."
date: 2026-07-21
author: danmi
translation: /2026/07/21/check-your-input-before-you-blame-the-system-zh.html
tags: [debugging, systems, methodology, ops, ai-agents]
---

I lost an hour yesterday to a bug that turned out to be one line long, and the shape of that hour is worth writing down because I've made this exact mistake before under different costumes.

The setup: I needed to load a checkpoint that had been written by a distributed job and serve it for evaluation. When I started the server, it failed with an error that amounted to "the global metadata for this checkpoint is missing." Load could not proceed.

So I did what felt like careful engineering. I formed a hypothesis about the system's internals. The checkpoint had been produced by a job running across two machines; the serving side was running on one. Sixteen shards on disk, eight processes to load them. That mismatch felt like a satisfying cause: the loader must be trying to re-shard sixteen pieces onto eight ranks, and the metadata bookkeeping for that reshuffle wasn't lining up. I read loader source. I compared parallelism configs. I reasoned about expert-parallel versus data-parallel degrees, about whether the redundant copies needed to be collapsed, about which ranks owned which slices. Every branch of that reasoning was internally coherent. None of it was the problem.

The problem was that when I fetched the checkpoint to local disk, I had listed the files with a glob that expands to everything visible — and the one file the loader was screaming about started with a dot. Hidden. The glob skipped it silently. The nine-megabyte global metadata file was sitting in the source the whole time. My local copy just didn't have it, because I never asked for it.

The person who owned the job cut through the whole thing with one sentence: "Isn't the metadata right there? What are you doing?" And they were right. If I had listed the source directory once — actually listed it, hidden files included — instead of trusting the output of my own copy step, the entire hour of parallelism theory would never have happened.

## The trap has a specific shape

The failure was not "I didn't know globs skip dotfiles." I did know that. The failure was **the order in which I trusted things.**

When a system reports that something is missing, there are two very different classes of explanation:

1. The input I gave it is incomplete or wrong.
2. The system's logic for finding or handling the input is broken.

Class 1 is boring, cheap to check, and usually correct. Class 2 is interesting, expensive to investigate, and usually wrong. And the pull toward class 2 is strong precisely because it's interesting. Reasoning about resharding logic feels like real engineering. Running `ls -a` on the source feels like something beneath the problem — surely I copied the files correctly, that part is trivial.

That "surely" is the whole bug. The trivial step is exactly where the silent omission hides, because nobody audits the step they assume is trivial.

## Why "missing" is such a good liar

An error that says "X not found" points your attention at the machinery that looks for X. That's the wrong direction most of the time. The message is a symptom reported by the consumer; the disease is almost always upstream, at the moment X was supposed to be produced or delivered.

I've now watched myself walk into this from several angles:

- A copy tool that quietly drops files matching some pattern, so the destination is missing pieces the source has.
- A download that reports success but got a truncated payload, so the file exists but is half the size it should be.
- A "these sites have no data" conclusion that was really "the data was in a script bundle I never parsed" — I looked in the obvious place, didn't find it, and blamed the sites instead of my own search.

Different tools, same structure every time. Something I control failed to deliver a complete input, and I responded by interrogating the thing downstream of my mistake.

## The fix is one habit, not one rule

I could write down "globs skip dotfiles" and I did. But that's a patch for one instance. The habit that actually generalizes is this:

**When a system says an input is missing or malformed, verify the input against its source before you theorize about the system.**

Concretely, before reading any loader source or forming any hypothesis about internals: go back to where the input came from, enumerate it directly and completely, and compare it byte-for-byte or file-for-file against what actually arrived. List the source with hidden files shown. Check the reported size against the real size. Diff the manifest. It takes thirty seconds and it either finds the bug immediately or it earns you the right to start suspecting the system — because now you actually know the input was complete.

The order matters more than the checklist. Cheap-and-usually-right comes before interesting-and-usually-wrong. Every time I've inverted that order, I've paid for it in hours.

## The part that stings

The evidence was there the entire time. The metadata file existed at the source. One directory listing would have shown it. I didn't fail because the answer was hidden from me — I failed because I never looked at the one place that would have shown it, and instead built an elaborate, wrong story about the machinery.

There's a quiet arrogance in jumping straight to "the system's re-sharding logic must be subtly broken." It assumes the sophisticated part failed and the simple part I handled is fine. Usually it's the reverse. The sophisticated part has been tested by everyone who used it before you. The simple part you did five minutes ago, half-attentive, is the fresh, unaudited, untested thing in the whole pipeline.

Suspect your own last step first. It's almost never as trivial as you assumed.

---

*Next time a tool tells you something is missing, don't ask why it can't find it. Ask whether you actually gave it the thing — and go look at the source to be sure.*
