---
layout: post
title: "The Fallback That Had No Warning"
subtitle: "Someone claimed a normalization routine was silently mixing things that should have stayed separate. I read the code to check. The bug was real — but the branch they pointed at wasn't the scary part. The scary part was the branch with no comment, no fallback, and no way to tell it had gone wrong."
date: 2026-09-05
author: danmi
translation: /2026/09/05/the-fallback-that-had-no-warning-zh.html
tags: [engineering, debugging, correctness, code-review, systems]
---

Someone told me a piece of code was quietly doing the wrong thing — pooling together numbers that were supposed to be kept in separate groups, so that a per-group baseline came out as a single global average instead. I didn't take it on faith. I pulled the source, found the routine, and read it line by line to see if the claim held.

It held. The claim was right. But reading it closely taught me something the claim didn't say, and it's the part I keep thinking about: the branch that was easy to point at was not the branch that should scare you.

## The shape of the code

Strip away the specifics and the routine looked like this. It received a flat array of numbers and needed to reshape it into groups before computing a per-group statistic. There was a size check:

- **If** the total count equaled *(number of groups) × (items per group)*, reshape into that grid. Clean, positional, correct — every group its own row.
- **Else** — with a little comment saying, roughly, *when the groups aren't all the same size* — fall back to treating the entire array as one big group.

Then it computed the mean over the last axis and subtracted it. In the fallback branch, "the last axis" was everything. One mean, over all of it, subtracted from every element. The per-group structure the whole routine existed to preserve was gone, silently, in the branch that was supposed to handle the awkward case.

## Why the fallback is the wrong kind of defensive

At a glance the `else` looks responsible. The author clearly thought about the ragged case — the groups aren't always equal, so here's a branch for it. A comment even names the situation. It has the *appearance* of handling an edge case.

But look at what it actually does when it fires. It doesn't refuse. It doesn't warn. It doesn't fall back to a slower-but-correct grouping. It falls back to a *different, wrong answer that has the same shape as the right one*. The output is still an array of the correct length, still full of plausible numbers, still flows downstream without complaint. Everything that consumes it keeps working. Nothing catches fire. The only thing wrong is the meaning, and meaning doesn't throw exceptions.

That's the trap. A fallback that fails loudly — throws, returns an error, produces obviously-broken output — is a fallback that protects you, because you find out. A fallback that produces confident, well-formed, wrong output is worse than no fallback at all, because it converts a crash you'd have noticed into a silent corruption you won't. The comment saying "when the groups aren't equal" reads like a safeguard. It's actually a note explaining *how the code chooses to be wrong*.

## The branch nobody was looking at

Here's the part that wasn't in the original claim, the part I only saw by reading instead of trusting. The person had focused on the `else`, the ragged-groups fallback, because that's the branch that's obviously suspicious. But think about the `if`.

The `if` triggers when the total count *exactly equals* groups × items-per-group. When the groups really are all equal, that's correct. But when the groups are ragged — different sizes — you'd expect the total never to match that product, so you'd expect the `else` to catch it. Except: with variable group sizes, the total is just a sum, and a sum can land on that product by coincidence. Different-sized groups whose counts happen to add up to the same number as the equal-sized case would pass the `if` check, take the positional-reshape path, and get silently carved into the *wrong* groups — with no fallback, no comment, no signal of any kind.

So the branch everyone worried about at least announces itself with a comment. The branch nobody was worried about is the genuinely dangerous one: it does the wrong thing precisely when its guard condition is satisfied by accident, and it has nothing — no log, no assertion, no ugly output — to tell you it happened. The fallback is a bad answer you can find. The coincidental match is a bad answer wearing the exact costume of the good one.

## What made it findable at all

I want to be honest about how this got caught, because it wasn't caught by the code. It was caught because a human downstream noticed a result that didn't smell right and traced it upward — and then I read the source to confirm, rather than assuming either the accuser or the code was correct. Nothing in the system raised its hand. The size check was the only guard, and the size check is exactly the thing that fails on coincidence.

The lesson isn't "add more branches." Branches are how this happened. The lesson is about what a guard is allowed to do when it's unsure. A guard that resolves ambiguity by silently picking an interpretation and producing shaped output has abdicated. If the routine can't be certain how the array should be grouped, the correct behavior isn't to guess and reshape — it's to carry the grouping information explicitly so the question never arises, or to refuse and say why. A size that happens to match is not evidence that the structure matches.

## The rule I took from it

When you review code that reshapes, buckets, or groups data by inferring structure from a count, ask two questions in this order. First, the obvious one: what does the fallback do when the counts don't line up — and does it fail loudly or fail quietly? Second, the one people skip: can the counts line up *by accident*, and if they do, does the "normal" path silently do the wrong thing with no fallback at all?

The second question is the one that matters, because the first branch — the one with the comment, the one that looks suspicious — is at least visible. It's the confident path, the one guarded only by an arithmetic coincidence, that produces a wrong answer indistinguishable from a right one. Inferring structure from a count is fine right up until the count lies to you, and a sum will lie to you the moment two different shapes add up to the same total. Don't guard grouping with a number. Carry the grouping.
