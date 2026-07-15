---
layout: post
title: "You Fixed the Test, Not the Bug"
subtitle: "When you patch exactly the cases your test named, the test can no longer tell you whether you solved the problem or memorized the answers. You need a sample the fix has never seen."
date: 2026-07-16
author: danmi
lang: en
translation: /2026/07/16/you-fixed-the-test-not-the-bug-zh.html
tags: [testing, overfitting, methodology, evaluation, engineering]
---

I spent a day tightening a classifier that kept letting the wrong things through. There was a review that had named the failures: a list of items the classifier accepted but shouldn't have. I read the list, understood each miss, wrote rules that caught each one, and reran the review. The pass rate jumped from the low seventies to the mid eighties. Every named failure was now caught. Zero good items were wrongly rejected. It looked like a clean win.

Then I ran it against a fresh batch the fix had never seen, and six new failures fell out immediately — the same *kind* of mistake, on items nobody had written down. The classifier hadn't learned to reject the bad class. It had learned to reject the exact things on my list.

## The list is a sample, not the problem

This is train/test contamination, and every ML person nods along when you say those words about datasets. But it sneaks back in the moment you're doing ordinary engineering, because a bug report doesn't *feel* like a training set. It feels like the truth. Someone found five things that are broken; you fix those five things; the five things are no longer broken; you're done.

Except the five things were never the problem. They were a sample drawn from the problem. The problem is the whole class of inputs that should have been rejected and weren't, and your five examples are whatever happened to get noticed. When you write a rule per example, you are fitting to the sample. When you then measure yourself on that same sample, you're grading a student on the exact questions they were allowed to study, and calling the A a measure of understanding.

The tell is a fix whose shape mirrors the failure list too closely. If the list had five misses and your patch has five special cases, each one aimed at one miss, you didn't find the rule that separates good from bad. You found five patches that happen to cover five points. The gaps between the points are still open, and the next input lands in a gap.

## Why the good score is worse than no score

A failing test is honest. It tells you there's a problem and roughly where. The dangerous state is a *passing* test that passes because you taught to it. Now the instrument that was supposed to warn you has been quietly recalibrated to agree with you, and you've lost the one signal that could have caught the overfit.

This is what makes it worse than just being wrong. Being wrong with a red test keeps you working. Being wrong with a green test sends you home. The mid-eighties number felt like permission to ship. It was actually a number I had manufactured by fitting to the very cases it was computed from. Held-out, the real generalization was much lower, and I only knew that because I bothered to hold something out.

## The discipline: a fresh sample, drawn after the fix

The rule I keep relearning is boring and I keep skipping it anyway: **the data that judges a fix must be different from the data that motivated it.** Not "more of the same list." Different — sampled independently, ideally after the fix is written so you can't peek. If you patched against the failures a review named, you have not measured anything until you draw a new batch the patch has never touched and see whether the same class of mistake survives.

In my case the new batch did more than score me. It named the six new misses, which told me my rules were still too specific — several of them keyed on surface features (a particular top-level domain, a particular phrasing) rather than the property that actually distinguished the class. Folding those six in and generalizing the rules got the held-out number up to where the original had merely pretended to be. But the honest version required a second, unseen sample, and then treating *that* one as spent the moment I fit to it too.

There's a small infinite regress here and it's fine. Every sample you fit to is burned as an evaluator. The answer isn't to find one magic held-out set; it's to keep drawing fresh ones and to internalize that the moment a set has informed your fix, it can no longer certify it.

## How to catch yourself

A few signs you've fixed the test instead of the bug, none of which require ML vocabulary to notice:

- Your patch has about as many special cases as the report had examples, and they line up one to one.
- Your rules mention specific surface features of the failing items — an exact string, an exact domain, an exact id — rather than the property those items share.
- Your only evidence is the same list that motivated the work, rerun.
- The score jumped a lot, all at once, right after you addressed the named cases.

And the one habit that dissolves all of them: before you believe a fix, draw a sample it has never seen, and let that sample tell you whether you solved a class or memorized a list. A green light you built by studying the answer key is not a green light. It's a mirror.
