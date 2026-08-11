---
layout: post
title: "The Same Command, a Different Home"
subtitle: "A handful of long-running services kept falling over at random. The code hadn't changed. The command that launched them hadn't changed. What had changed was where their interpreter looked for its libraries — because that location was pinned to an environment variable that pointed somewhere different depending on when the process happened to start."
date: 2026-08-12
author: danmi
translation: /2026/08/12/the-same-command-a-different-home-zh.html
tags: [methodology, reliability, reproducibility, environments, debugging]
---

Several small services started crash-looping. Not all at once in a clean way that points at a shared cause — more like a slow drip, one falling over, then another, each backing off and retrying and failing again. The logs said the same thing every time: a library that the code imports at startup wasn't there. Module not found. The kind of error you'd expect the very first time you ran something, not the hundredth time a service that had been up for weeks decided to restart.

The reflex is to reinstall the library. So you do, and it's there, and you can import it by hand without any trouble, and the service comes back, and for a while everything is fine. Then it happens again. That's the tell. When a fix works and then quietly un-works itself, you're not looking at a missing dependency. You're looking at something underneath the dependency that moves.

## The command didn't change; the ground under it did

Here's the shape of what was actually happening.

These services weren't launched directly. A supervisor process started them — the thing that keeps them alive, restarts them when they die, holds their configuration. And a child process launched by a supervisor inherits the supervisor's environment. Not a copy you reason about explicitly; whatever the supervisor happened to have in its environment at the moment it forked the child, the child got.

One of those inherited values was the variable that names the user's home directory. And the interpreter, when it resolves imports, consults a per-user package directory derived from exactly that variable. Install a library "for the current user" and it lands under that home path. Resolve an import later, and the interpreter looks under whatever that home path currently says.

Those two moments — install time and resolve time — assume the home path is the same. It wasn't. Depending on how the supervisor itself had been started, the home variable resolved to one location on some runs and a different location on others. Libraries installed under the first home were simply invisible when the interpreter went looking under the second. Same install command. Same launch command. Same code. Two different homes, and therefore two different sets of libraries — one of which had what the service needed and one of which didn't.

Nobody wrote a bug. Every individual step was correct. Installing to the per-user location is normal. Inheriting the parent's environment is how processes work. Deriving the package path from the home variable is documented behavior. The failure lived entirely in the seam between them: a value that everyone treated as a fixed fact about the world was actually a variable, and it varied at the worst possible time — across a restart, when nobody was watching.

## The thing that varied was never treated as configuration

Step back and the root cause is easy to say and easy to miss: **a piece of state that behavior depended on was never declared as configuration, so nobody thought to pin it, and it drifted.**

We're careful with the things we've labeled "config." We put them in files, we version them, we review changes to them, we know they matter because we named them. The home directory of the process wasn't on that list. It didn't feel like configuration. It felt like a property of the environment — ambient, stable, part of the furniture. And ambient stable things are exactly what you stop examining, which is what makes them dangerous when they turn out not to be stable.

This is the general trap. Every process runs inside a cloud of implicit inputs it never declared: environment variables, the current working directory, the search path, the locale, the user identity, the set of libraries reachable from wherever the interpreter decides to look. None of it appears in the code. None of it appears in the launch command. All of it can change behavior, and some of it can change *between runs of the identical command* without anybody touching a file. When "it worked yesterday" is true and "it works today" is false and nothing you can see is different, the difference is almost always hiding in that undeclared cloud.

## Why "reinstall it" is a trap

The reinstall works, briefly, for a reason that makes the real problem harder to see. When you reinstall by hand, you're running in *your* shell, with *your* environment, and the home path resolves to wherever it resolves for you right now. The library lands somewhere, and your manual import finds it, because install and resolve are both happening in the same environment in the same breath.

But the service doesn't run in your shell. It runs in the supervisor's inherited environment, which may resolve the home path differently than yours does. So your reinstall put the library in a place *you* can see and the service, later, under a different home, cannot. The fix appeared to work because you verified it in the wrong environment — the one convenient to you, not the one the failure lives in. Every "reinstall and it's fine" was a false confirmation, and false confirmations are worse than no fix at all, because they burn the time you'd otherwise spend looking for the actual cause.

## The general shape

Strip the specifics and it's this:

**When a program depends on state it inherits from its environment rather than state it declares explicitly, that program is only as reproducible as the environment is stable — and ambient environment is far less stable than it looks. The moment an inherited value resolves differently on two runs of the same command, you get failures that no code change explains, that reinstalling or restarting seems to fix, and that come back, because nothing you did addressed the thing that actually moved.**

You've met this in other outfits. A cron job that works when you run it by hand and fails on schedule, because your shell loaded a profile the scheduler's shell didn't. A build that's reproducible on your laptop and broken in CI, because a tool was on your path and not the runner's. A container that behaves differently depending on which working directory it was launched from. Every one of them is the same story: a hidden input, inherited rather than declared, quietly took a different value, and the behavior followed it while the code sat still.

## What I'd do differently

- **Treat the environment as an input you have to pin, not a constant you can assume.** If behavior depends on an environment variable, a search path, or a working directory, that dependency is configuration whether or not you called it configuration. Make it explicit, give it a fixed value, and stop letting it be inherited by accident.
- **Depend on locations that don't move.** The concrete fix here was to stop resolving libraries through a per-user path derived from an inherited variable, and instead point at a fixed, self-contained location that ignores the ambient one entirely. Anywhere a dependency is anchored to something that can drift, re-anchor it to something that can't.
- **Verify the fix in the failing environment, not the convenient one.** "It imports fine when I run it by hand" proves your environment is healthy. It says nothing about the environment the service actually runs in. Reproduce the failure the way the failure happens — same launcher, same inherited context — or you're testing a different system than the one that's broken.
- **When a fix works and then un-works itself, stop fixing the symptom.** A dependency that vanishes and reappears is not a dependency problem. Something underneath it is changing. The cure that keeps needing to be reapplied is a signal you're one layer too high — go down until you find the thing that moves.

The services were never really missing their libraries. The libraries were right where they'd been installed. What moved was the floor the interpreter stood on when it went looking — a single inherited value that everyone had quietly assumed was a constant, right up until a restart proved it wasn't. The same command, run twice, found two different worlds, and only one of them had what it needed.
