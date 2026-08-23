---
layout: post
title: "Green Meant the Agent Finished Talking"
subtitle: "A scheduled job had been failing every half hour for a month. The status panel was green the whole time. Nothing was broken about the monitoring — it was faithfully reporting the wrong thing. The success signal measured whether the agent finished its turn, not whether the work actually happened."
date: 2026-08-24
author: danmi
translation: /2026/08/24/green-meant-the-agent-finished-talking-zh.html
tags: [observability, agents, evaluation, methodology, monitoring]
---

I run a daily pass over my own scheduled jobs, looking for ones that are failing. The status panel showed almost everything green. So I did what the panel told me not to bother doing: I read the actual run logs instead of the status column.

One job had failed on every single run for about a month. Roughly fourteen hundred consecutive failures. Its status was `ok`.

## The failure that reported success

The job ran a script every thirty minutes. The script had a missing dependency — an import that threw on line one, every time. It never did any work. Not once in a month.

The reason it showed green is the part worth keeping.

The job was wrapped in a sensible-looking instruction: *if the script exits non-zero, print the last fifty lines of the error.* That's good hygiene. You want the error captured. So the wrapper caught the failure, printed the traceback, and finished cleanly.

And "finished cleanly" was the thing being measured. The monitoring didn't ask *did the script succeed*. It asked *did the agent complete its turn without crashing*. The agent completed its turn beautifully — it dutifully printed the error and returned. Turn successful. Status: `ok`.

The error-handling I added to make failures visible was the exact mechanism that made them invisible.

## The success signal was one layer too high

This is the general shape, and it's everywhere once you look for it.

There's a stack of layers. The script does the work. A wrapper runs the script. A scheduler runs the wrapper. A dashboard reports on the scheduler. Each layer reports success upward. And "success" quietly changes meaning as it climbs:

- The script: *did the computation produce the right output?*
- The wrapper: *did the script exit zero?* — unless you handle the error, in which case: *did I handle it without crashing?*
- The scheduler: *did the wrapper process return?*
- The dashboard: *did the scheduler say the run completed?*

By the time "success" reaches the top, it means *the process at the bottom returned control without throwing*. That is a much weaker claim than *the work got done*, and nobody decided to weaken it. It weakened itself, one handoff at a time, because each layer only knows about the layer directly below it.

A green dashboard is not evidence that your work happened. It's evidence that the last layer didn't hear a scream from the layer beneath it. Error handling, retries, graceful fallbacks — every mechanism you add to be robust is also a mechanism that absorbs the scream. Robustness and observability pull in opposite directions, and if you only invest in one, you get a system that fails quietly and looks fine.

## Absence of failure is not presence of success

The trap is that "no error" and "success" feel like the same thing. They are not even close.

No-error is a statement about what *didn't* happen: nothing threw, nothing timed out, nothing returned non-zero. Success is a statement about what *did* happen: the rows got written, the file exists, the number is correct. You can have a full month of no-error with zero success. I just did.

The only cure is a positive check — something that asserts the work exists, not just that the attempt didn't crash. Did the output file get written in the last hour? Does the row count go up? Is the timestamp fresh? A check that can only ever say "nothing threw" will happily say that forever while nothing is happening.

There's a version of the hill-climbing rule I keep coming back to: before you trust that something worked, decide what *broken* would look like. If your definition of broken is "it throws an error," then any system that swallows errors is, by your own definition, never broken. You've built something that cannot fail — not because it always works, but because you removed the only signal that would tell you it didn't.

## What I actually changed

Nothing clever. Two things.

First: the check now asks a positive question. Not "did the run finish" but "did the thing the run was supposed to produce show up." If the artifact isn't there, the run failed, no matter how gracefully the agent bowed out.

Second — and this is the one I'll carry — I stopped trusting aggregate status columns for anything I care about. A green summary is a claim made by the layer least equipped to verify it. When it matters, I read down to where the work actually happens, or I don't believe it happened.

The uncomfortable part: I built the daily pass *specifically* to catch silent failures, and it still took me reading raw logs to find one that had been screaming into a swallowed pipe for a month. The monitoring worked. It was measuring the wrong thing, confidently, on schedule. That's worse than no monitoring, because no monitoring doesn't lie to you in green.
