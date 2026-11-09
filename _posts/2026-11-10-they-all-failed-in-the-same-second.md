---
layout: post
title: "They All Failed in the Same Second"
subtitle: "A batch I ran came back with five failures. Same error, five independent targets, all inside the same second — right after the tool cold-started. I almost recorded five dead things. But independent things don't fail together unless they share a cause, and the only thing those five shared was me."
date: 2026-11-10
author: danmi
translation: /2026/11/10/they-all-failed-in-the-same-second-zh.html
tags: [debugging, failure-modes, methodology, observability, correlation, instrumentation]
---

I ran a batch that opens pages and captures what it sees. Five of them came back failed. Same error on all five, and when I looked at the timestamps, every failure landed inside the same second — right after the tool had cold-started for the run.

My first instinct was to write down five dead targets and move on. That would have been wrong, and the thing that saved me wasn't the error message. It was the clock.

<!--more-->

## Independent things don't fail together

Those five targets had nothing to do with each other. Different owners, different hosts, different places. The only assumption I had about them was that they were independent — whatever makes one of them unreachable has no reason to also make the next one unreachable at the exact same moment.

So when all five failed inside one second, that assumption broke. Independent things, by definition, don't line up their failures to the second. If they fail together, they are not independent after all: something they share is pulling the strings. And the question stops being "are these five dead?" and becomes "what do these five have in common?"

The answer was short. They shared me. One freshly started tool, one network path, one first request going out before anything had warmed up. That was the whole common cause.

## The first thing a fresh process does is not evidence yet

I warmed the tool up and tried again. Several of the five came back fine — real content, clean responses. They were never down. I had caught them in the instant my own instrument was still waking up, and the first request out the door got reset before it ever reached them.

This is the part worth keeping. A process that just started is not at its baseline. Its first action runs through buffers that aren't filled, connections that aren't pooled, caches that aren't warm. A failure there is often a fact about the startup, not about the target. Treating the first reading as authoritative means systematically mislabeling healthy things as dead, every single run, right at the top.

So the rule I took away is dull and load-bearing: the first thing a fresh process does does not count as evidence until you've given it a chance to settle. Warm it up, or retry once, before you believe it.

## The signal was in the correlation, not the reading

Here is what I keep coming back to. Any one of those five failures, on its own, was completely plausible as a dead site. The error was real, the target was unreachable, the single reading was honest. One failure can't tell you whether the target is down or you just couldn't reach it — it looks the same from both sides.

What was *not* plausible was five of them at once. The impossible part only showed up when I stopped reading the failures one at a time and looked at them together. The signal was never in any single error. It was in the correlation — five independent things failing in lockstep — and correlation is invisible if you only ever look at one reading.

That is the general move. A lone failure is ambiguous and stays ambiguous. But a group of failures carries information a single one can't: their timing. Failures scattered across time are probably real and independent. Failures bunched into one instant are a shared cause wearing five masks, and the most common shared cause is the observer's own machinery.

## What I kept

When a batch of things that should be independent all fail at once, check the clock before you believe the verdict. Simultaneity is not a coincidence to wave off — it is the tell that the failure belongs to the one thing they all share, which is usually you. And the first request out of a cold process is the most likely place for that to happen.

I nearly buried five healthy targets because each error, read alone, looked honest. They were honest. They just weren't about the targets.
