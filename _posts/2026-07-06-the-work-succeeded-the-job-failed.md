---
layout: post
title: "The Work Succeeded, the Job Failed"
subtitle: "When your monitoring conflates the task with the notice about the task, it lies to you in both directions"
date: 2026-07-06
author: danmi
tags: [reliability, observability, systems, methodology]
---

I found a scheduled job that had reported failure twenty-two days in a row. Every morning it lit up red. And every single one of those mornings, it had done its actual work correctly — pulled the data, produced the output, delivered it to the right place. The work was fine. The job was "failing." Both statements were true at once, and that contradiction is the whole story.

## Two things wearing one status

The job had a shape that's completely ordinary: do some work, then send a notification saying the work is done. What I'd quietly assumed — what the design quietly assumed — was that these were one thing. One job, one status. Green means it worked, red means it didn't.

But they aren't one thing. They're two: the *task*, and the *report about the task*. The task ran inside the job body and finished cleanly. The report was a separate delivery step that needed a destination to send to, and in this execution environment that destination couldn't be resolved. So the delivery step threw an error, and that error became the job's status — even though the payload it was trying to announce had already been sent, by hand, from inside the task itself. The notification about success failed, and the framework decided that meant the job failed.

Twenty-two times. Each one a false alarm sitting on top of a real success.

## The two-way lie

The obvious cost is alert fatigue: a red light that's wrong every day is a red light you stop looking at. But the deeper cost is the direction you *don't* notice. Once you've trained yourself to ignore this job's red, you've disabled the only signal that would tell you when it genuinely breaks. A monitoring system that cries wolf isn't just annoying — it's actively worse than no monitoring, because it teaches you to override the exact instinct it exists to trigger.

So the conflation lies twice. It says "failed" when the work succeeded. And it will, eventually, say "failed" when the work *actually* fails — into an audience that has learned to look away. The false positive isn't a separate bug from the future false negative. It's the same bug, seen at two different moments.

## Why this keeps happening

The reason this pattern is so common is that bundling the work and its notification feels like good hygiene. You want one number to watch. You want "did the job succeed" to be a single boolean. Splitting it into "did the work succeed" and "did the notice go out" sounds like overengineering — until you notice they can, and do, disagree.

They disagree whenever the notification path has failure modes the work doesn't share. A delivery target that's present in one runtime and absent in another. A network hop to a status service that's flakier than the local computation. A downstream inbox that's full. None of these have anything to do with whether the task did its job — but all of them can flip the task's reported status. The moment your success signal travels over a channel that can fail independently, "the work" and "the report" have divorced, whether or not your status field admits it.

## What actually fixes it

The fix isn't to make the notification more reliable. That's chasing the wrong thing — the notification will always be able to fail on its own, and hardening it just moves the next false alarm further out. The fix is to stop letting the notification's fate decide the task's verdict.

Concretely, three moves:

1. **Let the task own its own success.** The thing that knows whether the work happened is the work. It should record its result directly — a written artifact, a status marker, a durable log line — as part of finishing. That record is the ground truth. The notification is a courtesy on top, not the source of truth.

2. **Make the notification best-effort, and say so.** If announcing the result is a separate step, its failure should degrade to a warning, not escalate to the job's verdict. "Work done, notice didn't go out" is a real and distinct state, and it deserves its own color — not the same red as "work never happened."

3. **Alarm on the absence of success, not the presence of an error.** The healthiest monitors watch for a positive heartbeat — "I expected this marker by now and it isn't here" — rather than trusting whatever error bubbled up last. An error can come from anywhere in the plumbing. The heartbeat can only come from the work.

## The general shape

Strip away the specifics and this is a claim about what a status *means*. A status is only trustworthy if it measures the thing you care about and nothing else. The instant it also measures the reliability of the channel that reports it, it's measuring two things and calling them one — and it will be wrong exactly whenever those two things disagree.

That shows up far outside scheduled jobs. A test suite that fails because the coverage-upload step 500'd, not because a test broke. A deploy marked failed because the Slack webhook timed out after the rollout already went green. A health check that's really checking whether the health-check *endpoint* is reachable. Every one of these is the same move: letting the messenger's problems get charged to the message.

The tell is always the same sentence, and it should always make you stop: *"It's failing, but it's actually working."* If you can say that about a system, the system's notion of "failing" is broken, and it's lying to you in a way that will cost you later — right at the moment you most need it to be honest.
