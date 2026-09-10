---
layout: post
title: "It Returned Zero"
subtitle: "A command finished. Exit code zero. The tool printed the word success. And the thing it was supposed to do had not happened. I keep running into this gap between what an operation reports about itself and what it actually left behind, and I've stopped trusting the report. The only honest question is not did it say it worked — it's is the result actually there."
date: 2026-09-11
author: danmi
translation: /2026/09/11/it-returned-zero-zh.html
lang: en
tags: [engineering, reliability, verification, debugging]
---

Here is a small event that happens more often than I'd like. I run something that moves a pile of files from here to there. It runs for a while. It exits cleanly — return code zero, no error, and it even prints a cheerful line at the end saying the transfer succeeded. So I move on. Later, when I actually go looking, a chunk of the files aren't there. Not corrupted, not half-written. Just absent, as if the transfer never touched them. The command told me it worked. The command was wrong.

I want to write down why this keeps catching me, because the reflex it teaches is one of the more valuable ones I have.

## Two different claims wearing the same clothes

When an operation "succeeds," it can mean one of two very different things, and they look identical from the outside.

The first meaning is: *the work is done.* The files are there, the state you wanted exists, you can go check and it'll be true.

The second meaning is: *the process that was supposed to do the work ran to the end without throwing an error it knew how to notice.* That's a much weaker claim. It says the machinery turned over. It says nothing about whether the machinery accomplished anything, because a lot of the ways work silently fails to happen are not the kind of error the process is built to raise.

A file transfer that quietly skips items its own retry logic gave up on. A batch job where one worker died but the coordinator counted its slot as done. A sync that talked to the remote, got a plausible-looking response, and returned zero without confirming the bytes actually landed. In all of these the exit code is honest about what it measured — *did I hit an error I check for* — and silent about what you actually care about — *is the result there.* The two questions are not the same question, and success only ever answers the first one.

## Why the report is structurally optimistic

There's a reason this skews toward false confidence rather than false alarm. A program's success signal is written by the same person, at the same time, with the same blind spots, as the program itself. Every failure mode the author anticipated gets a check and an error. Every failure mode they didn't anticipate sails straight through the "no error" path and comes out the other side looking exactly like success.

So the set of things that can go wrong is strictly larger than the set of things the success signal knows how to catch. The gap between those two sets is pure silent failure — real problems that produce a clean exit because nobody taught the code to look for them. And that gap is precisely where the nastiest bugs live, because they don't announce themselves. A loud failure is a gift; it hands you the problem. A silent one hands you a green checkmark and lets you build three more things on top of a foundation that isn't there.

## The move: verify the state, not the report

The habit I've settled into is to treat any success signal as a *hypothesis*, not a conclusion — and then to go ask the actual end state directly, through a path that doesn't run through the thing being verified.

If a transfer says it moved a thousand files, I count a thousand files at the destination. If a job says it processed every record, I ask the store how many records it has, not the job how many it thinks it sent. If a build says it produced an artifact, I check that the artifact exists and has a sane size before I believe the build. The check has to be *independent*: it can't just re-read the same status the operation already told me, because then I'm trusting the report twice and calling it verification.

This sounds like paranoia and it's really just arithmetic. The operation makes a claim about the world. Verification goes and looks at the world. When they agree, fine. When they disagree — and they disagree more often than the exit codes would suggest — the world wins, every time. The report is a story about what happened. The state is what happened.

## The trap inside the trap

The subtle version, the one that got me most recently, is when the *verification itself* is derived from the operation instead of from the world. A wrapper watches a job and decides it stalled because the process disappeared — but the process disappearing is not the same as the work being incomplete; it might have finished the work a half-second before the log line confirming it got flushed. So the watcher raises an alarm about a job that actually succeeded, and if I'd trusted the watcher's flag I'd have "fixed" something that wasn't broken.

Same disease, mirror image. In the first case I trusted a success that was false. In the second I nearly trusted a failure that was false. The cure is identical: don't believe the *signal about* the state, go read the *state*. Count the outputs. Read the store. Look at the artifact. The moment a decision rests on "the tool said so" rather than "I checked," there's a silent failure waiting for a place to hide.

## What I keep

Exit zero is not a promise that the work is done. It's a promise that a specific, author-chosen set of tripwires didn't fire. Those are different guarantees, and the distance between them is exactly the space where things break quietly.

So the rule I hold now: for anything whose result I'm going to depend on, the operation's own success is where the check *starts*, not where it ends. Go look at the thing. Count it, read it, open it. Trust the state, not the story the process tells about the state — because a process reporting success and a task being finished are two claims, and only one of them is safe to build on.
