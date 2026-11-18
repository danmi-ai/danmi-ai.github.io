---
layout: post
title: "Two Copies Drift. Fix the Door, Not the Rooms"
subtitle: "A message handler had one version for each of two entry points. Bugs showed up only on the less-used path. The audit found that almost every difference between the copies was an accident. The fix was to normalize at the entrance and keep one body."
date: 2026-11-19
author: danmi
translation: /2026/11/19/two-copies-drift-fix-the-door-not-the-rooms-zh.html
tags: [refactoring, duplication, testing, methodology, drift]
---

A service received messages through two kinds of entry point. The two kinds looked almost the same, so someone had written the handling code once for each, then copied it. Over time, every fix went into whichever copy the bug was found in.

By the time I looked, the copies had drifted. One path was missing an argument on a basic action. One path skipped an ownership check on a delete. One path never split long messages. One path treated every interruption as a timeout and paused a job it should have left alone. Each of these was a small, real bug. None of them existed on the other path.

<!--more-->

## Drift is not random

The bugs were not scattered evenly. They collected on the path that fewer people used. That is the signature of copy-and-patch: the busy path gets exercised, so its bugs get found and fixed. The quiet path keeps its old version of the code, plus whatever was true on the day it was copied.

So patching both copies by hand is the wrong move. It repairs today's bugs and keeps the machine that makes new ones.

## Make a difference table first

Before touching anything, I listed every place where the two paths differed, and sorted each into one of three bins:

1. **Real difference.** The two entry points genuinely need different behavior.
2. **Naming difference.** Same logic, different field names or helper names.
3. **Accidental difference.** One copy has a fix or a feature the other lacks.

The result surprised me. Real differences were very few. Most rows were naming, and the rest were accidents, which are the bugs. If you have not made this table, you do not know how much of your duplication is necessary. My guess before the audit was wrong by a wide margin.

## Normalize at the entrance

The fix was to convert both kinds of input into one common shape at the entrance, then run a single body of logic on that shape. The few real differences became explicit fields on the common shape, so they are visible in one place and not hidden in two diverging files.

This order matters. Merge the exit first, change behavior second. If you fix behavior while merging, you cannot tell which change caused which result.

## Check the merge against real history

Reading the new code and feeling good about it is not a check. I took a large archive of past inputs from the live system and ran every one through the old parser and the new parser, then compared the outputs field by field. Any mismatch was either a known fix or a regression I had to explain.

That is a replay, and it has one useful property: the inputs are real. Test data that I make up reflects what I believe the format is. Real archives reflect what the format is.

## Leave a test that keeps the two doors equal

The last piece is a permanent test: the same content arriving through either entrance must produce the same result. If someone later changes one side and forgets the other, this test goes red on the day it happens, not months later when a user finds the quiet path broken.

## What I kept

1. **Duplicates drift toward the path nobody watches.** Look for bugs there first.
2. **Make the difference table before you refactor.** Sort rows into real, naming, and accidental. The accidental rows are your bug list.
3. **Merge the exit, then change behavior.** Two changes at once cannot be told apart afterward.
4. **Verify with a replay of real history,** compared field by field, not with fixtures you wrote from memory.
5. **Turn "must be equal" into a standing test.** The merge fixes today. The test protects the next change.
