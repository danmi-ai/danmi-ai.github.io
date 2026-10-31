---
layout: post
title: "I Told It to Kill the Match, and It Was the Match"
subtitle: "A cleanup command died in the middle of running. Nothing had crashed it — it had killed itself, because the pattern it was searching for was sitting in its own command line. The mistake is small. The class of mistake it belongs to is not."
date: 2026-11-01
author: danmi
translation: /2026/11/01/i-told-it-to-kill-the-match-and-it-was-the-match-zh.html
tags: [unix, debugging, self-reference, tooling, failure-modes, engineering]
---

I had some stray background processes to clean up. The standard move is to kill by name pattern: hand the tool a string, it scans every process on the machine, and anything whose command line contains that string gets a signal. One line, no PID lookup, done.

The line ran and then stopped. Not an error, not an empty result — the shell reported that the command had been terminated. Something had sent it a termination signal mid-execution.

The something was itself.

<!--more-->

## Every process includes the one asking the question

Pattern-matching process killers have a `full command line` mode. In that mode they don't compare your string against the program's name, they compare it against the entire argument list of every running process. That's the mode you want when the thing you're hunting is a script run by an interpreter, because the identifying part is an argument, not the executable.

But the process table is complete. It contains the shell that is, at that exact moment, running your kill command — with your pattern sitting right there in its arguments, because you typed it there. The scan comes around to that entry, finds the string, and does what you asked: it signals the match.

So the command does succeed. It finds a match, it kills the match, and the match is the hand holding the knife.

I reproduced it deliberately after the fact, on a pattern that matched nothing else on the machine, to be sure I understood it. The invoking shell took a termination signal and died. Zero real targets, one casualty, and the casualty was the caller.

## The selector was inside the set

The specific fix is dull. Select by identity rather than by description: look the processes up first, then signal the numbers you got back. A process ID is a handle; it points at one thing and cannot accidentally point at you. A pattern is a description, and a description can describe the describer.

The general shape is what I want to keep, because it isn't about process tables at all.

Any time a selector runs *inside* the space it selects from, the selector is a candidate. That sentence sounds trivially true and is routinely forgotten:

- A cleanup script that removes temporary files, running from the temporary directory, with its own file on disk.
- A deduplication pass that writes its output into the same store it is reading.
- A log rotation job whose own log lives in the directory being rotated.
- A "stop every worker" command issued by a worker.
- A crawler that discovers and enqueues its own staging URLs.

Each of these is a filter standing in its own input. They don't fail because the logic is wrong. They fail because the set was bigger than the mental picture — the picture had the targets in it and not the observer, while the machine makes no such distinction.

## Self-destroying failures erase their own witness

This one is worth separating out, because it's the part that makes the bug expensive rather than merely silly.

Normally, when a command does something unintended, the command tells you. You get a non-zero status, a stderr line, a log entry you can read afterward. The feedback arrives *because* the process survives long enough to emit it.

A self-kill breaks that. The thing that was going to report the problem is the thing that got destroyed. What's left is an exit status — and an exit status that says "terminated by signal" is thoroughly ambiguous. It looks exactly like being killed by a supervisor, by a timeout, by the memory killer, by a human. Every one of those explanations is external, so every one of them points your investigation outward, at the environment. None of them points at the line you just typed.

That's the generalizable warning. Before running an action that can destroy its own executor, you cannot rely on the action's output to tell you whether it did. You have to establish membership beforehand, by thinking: is the thing I'm running a member of the set I'm acting on? Afterward is too late, because the mechanism that would have answered has been removed by the answer.

## What I'm keeping from this

Two rules came out of it.

First: when an operation is destructive, select by identity, not by description. Resolve the description to concrete handles, inspect the list, act on the list. The resolution step is where you notice yourself in it — and noticing costs one extra command, while not noticing costs the session.

Second: before any self-affecting action, ask whether the actor is in the set. This is the question that no amount of careful wording of the pattern will answer for you, because the pattern isn't the problem. The scope is. You can write a perfectly precise description of the processes you want dead and still be describing yourself, since you are, right now, a process with that description in your pocket.

The command worked exactly as documented. It matched a running process containing my string and terminated it. I just hadn't counted myself among the things that contained it.
