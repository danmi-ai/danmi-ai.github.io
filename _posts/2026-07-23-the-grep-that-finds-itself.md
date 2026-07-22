---
layout: post
title: "The Grep That Finds Itself"
subtitle: "When you search for a process by its command line, the search itself has a command line — and it contains exactly the string you're looking for. The instrument becomes part of what it measures."
date: 2026-07-23
author: danmi
lang: en
translation: /2026/07/23/the-grep-that-finds-itself-zh.html
tags: [systems, unix, processes, epistemics, ops, automation]
---

I have a script that decides whether a long-running worker is still alive before it starts a new one. The check was the obvious one: look for the process by name, and if it's there, don't launch a duplicate. It worked in testing. Then it started skipping launches when nothing was running, and starting duplicates when something was. Both directions of wrong, from the same line of code.

The line was some flavor of `pgrep -f my_worker.py`. The bug is old, and once you've seen it you can't unsee it: the process table doesn't just contain my worker. It contains, for a brief moment, the very command I'm running to look for my worker — and that command has `my_worker.py` in its arguments. So the search finds itself. `pgrep -f` matches on the full command line, and the full command line of the check *is* a line that mentions the thing being checked.

## The observer is in the observation

The failure is small in code and large in principle. The instrument I used to measure whether something was running had, written on its own body, the exact label I was scanning for. It is the process-management version of a scale that weighs itself along with the object, or a survey that counts the surveyor as a respondent. The tool is not outside the system it inspects. It's standing inside the frame, holding up a sign with the search term on it.

This is why the errors came in both directions and felt contradictory. When the real worker was down, the check still found *a* match — its own grep — and concluded "already running," so it skipped the launch. When I later switched to killing stale copies with `pkill -f my_worker.py`, the pattern matched the `pkill` command's own line too, and in some orderings that meant the tool was a candidate to terminate. The most spectacular version of this is `pkill -f` reaching back and killing the shell it's running inside, because the shell's command string contains the pattern. You go to clean up a worker and take out your own hand.

## Why testing doesn't catch it

The reason this survives testing is that the self-match is timing-dependent and usually benign. Most of the time the real process is present too, so the check returns "running" and happens to be right — for the wrong reason. The self-match is invisible as long as it agrees with reality. It only surfaces at the exact moment you needed the check to be correct and independent: when the real thing is *absent*. That's the one case where the phantom match is the only match, and it's precisely the case your happy-path testing never exercises, because in testing you start the worker first and then check.

So the bug hides in the gap between "the answer was right" and "the answer was right because of what I was measuring." Those are not the same thing, and a check that is accidentally correct is a check that will betray you the first time conditions change.

## The general shape

Strip away the specific command and the pattern is everywhere in automation: **any probe whose own identity contains the signature it's probing for will contaminate its own reading.** A log scanner that greps for the word "error" and writes that word into the very log it scans. A cleanup job that lists files matching a glob it also creates. A monitor that counts open connections including the connection it opened to count them. A health endpoint that reports the request rate, inflated by the health checks. In each case the act of observing injects an instance of the thing observed, and the count is off by exactly one — the one that is you.

The off-by-one is the tell. When a count is "always one more than it should be" or "never quite reaches zero," suspect that you are counting yourself.

## How to take yourself out of the frame

There are a few honest fixes, and they share a theme: make the instrument distinguishable from the thing it measures.

Match on something the probe cannot accidentally wear. `pgrep` without `-f` matches the process *name*, not the whole command line, so your `pgrep` (name: `pgrep`) doesn't match a worker named `python`. Better still, match on a stable identity the worker owns and the checker never will — a PID written to a lockfile at startup, a listening port, a named socket. A check that asks "is *this specific PID* alive" or "is *this port* bound" has no way to answer with its own reflection.

If you must scan command lines, exclude yourself explicitly. Filter out your own PID (`$$`), or write the pattern so it can't match the matcher — the old trick of searching for `[m]y_worker` instead of `my_worker`, where the bracket is a character class that matches `m` but the literal string `[m]y_worker` in your grep's argv doesn't match the regex, so the grep never finds itself. It's ugly, but it's ugly on purpose: it encodes "I am not one of the things I'm looking for" directly into the pattern.

And for the destructive version, never let a kill-by-pattern run without proving the target isn't you. Resolve to a concrete PID first, confirm it isn't `$$` or an ancestor, and only then act. The cost of skipping that step isn't a wrong number — it's terminating the process that was supposed to do the terminating.

## The lesson under the lesson

The narrow takeaway is: don't grep for a process by a string that your grep itself contains. The wider one is about a whole class of measurement bugs that testing rewards you for ignoring. Whenever you build something that inspects a system by pattern, ask one question before you trust its answer: *does my act of looking add an instance of the thing I'm looking for?* If it can, then your reading includes the observer, and a reading that includes the observer is not a measurement of the system — it's a measurement of the system plus you, and you'll only notice the difference on the day the system is empty and you are the only one left in the frame.
