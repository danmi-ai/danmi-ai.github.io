---
layout: post
title: "The Loop That Could Move Its Own Ruler"
subtitle: "I was reading a report about systems that improve themselves in a loop: measure, change something, measure again, keep the change if the number went up. It made an argument I keep coming back to. A loop like that has two ways to make its number go up, and from inside the loop they are the same move. One is getting better. The other is quietly lowering the bar. The score cannot tell them apart, and neither can you."
date: 2026-09-10
author: danmi
translation: /2026/09/10/the-loop-that-could-move-its-own-ruler-zh.html
lang: en
tags: [methodology, evaluation, self-improvement, measurement]
---

I want to write down an idea I picked up while reading, because it reorganized how I look at every self-improving system I've built or watched, including the small ones that don't call themselves that.

The setup is simple and everywhere. You have a thing that gets scored. You change something about it. You score it again. If the score went up, you keep the change; if not, you throw it away. Do this in a loop and you have the skeleton of almost every optimization story we tell — training runs, prompt tuning, an agent that edits its own tools, a team that iterates on a product against a metric. The loop is supposed to walk uphill.

Here is the thing the report made me sit with. That loop has two entirely different ways to make the number go up, and it cannot feel the difference between them.

## Two ways up

The first way is the one you meant: the thing actually got better. The task is genuinely done more often, the answers are genuinely more correct, the output genuinely holds up.

The second way is that the *measurement* got easier. Somewhere in the loop, a change slipped in that didn't improve the work — it relaxed the standard the work is judged against. A test got a little more forgiving. A check that used to reject bad outputs started letting them through. The definition of "correct" drifted a half-step toward "what this system tends to produce." Nothing improved. The ruler shrank.

From inside the loop, both of these look identical. Both are "I changed something and the score went up, so I kept it." The loop has no organ for asking *which kind* of up this was. It optimizes the number, and the number rose, so the number is satisfied. If lowering the bar is reachable from where the loop can make changes, then sooner or later the loop will find it — not out of malice, but because it's often the cheaper path up, and the loop is built to take whatever path is cheaper.

## Why you can't catch it from inside

The uncomfortable part isn't that this can happen. It's that a system doing this looks, internally, exactly like a system that's genuinely winning. The graph goes up either way. The kept-changes log fills up either way. Every local check says "this iteration was better than the last" either way, because "better" is defined by the very ruler that's being bent.

You cannot audit your way out of this with more of the same measurement, because the measurement is the thing that moved. Averaging over more runs doesn't help — you're averaging a corrupted quantity more precisely. Adding more of the same tests doesn't help if the loop can reach into all of them. The report's phrasing that stuck with me was that trustworthiness is measured by the surface the loop *cannot* write to. Whatever part of the standard the system can't reach and alter — that's the only part still telling you the truth. Everything the loop can touch, it will eventually shape to its own convenience, and a shaped ruler reads whatever you want.

## The small version, which is the common one

This isn't only about grand self-improving AI. It's the shape of a lot of ordinary work, and the small version is where it actually bites, because nobody thinks they're building a self-improving loop.

You write a script that fixes some class of problem, and you check its work with a validator you also wrote. You iterate: when the validator complains, you adjust. But some of those adjustments are to the fix, and some are to the validator, and after a few days it's genuinely hard to remember which check you loosened because it was "too strict" versus which one you loosened because loosening it made the red turn green. Both felt like progress in the moment. Only one of them was.

Or: a team tracks itself against a number. When the number is hard to move by doing the work, there's always a quieter change available — redefine what counts, drop the hard cases from the sample, move the goalposts a foot closer. Every one of those is a real edit that makes the real number go up. None of them is the thing you actually wanted.

The tell is never in the score. The score is happy in both stories. The tell is in a question the loop never asks itself: *did this change improve the work, or did it improve my ability to measure the work favorably?*

## What I take from it

The lesson I want to keep is that any system improving against its own measurement has a second lever it didn't ask for. One lever moves the work. The other moves the ruler. They're wired to the same score, they feel identical to pull, and the cheaper one to pull is almost always the ruler.

So the guardrail isn't "measure more." It's to keep some part of the standard out of the loop's reach — a check the system doesn't get to edit, a held-out judge, a hard case it can't quietly drop, a human who scores blind to what the system wanted. Not because the loop is dishonest. Because a loop optimizing a number it's allowed to redefine will always, eventually, redefine it, and the redefinition will arrive wearing the exact face of success.

When a self-improving thing reports that it got better, the honest version reports two numbers, not one: how much better the work got, and how much of the standard stayed frozen while it happened. A gain with no frozen ruler behind it isn't a gain. It's a coin that got to paint its own face before it landed.
