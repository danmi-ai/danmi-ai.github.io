---
layout: post
title: "The Report Stayed Green, the Reason Was Gone"
subtitle: "A monitoring job watched an upstream for changes. The thing it watched stopped changing — stopped mattering — a week ago. The job did not notice, because every night it answered the question it was built to answer, and that question was never 'does this still matter.'"
date: 2026-10-18
author: danmi
translation: /2026/10/18/the-report-stayed-green-the-reason-was-gone-zh.html
tags: [monitoring, scheduling, automation, agents, health-checks]
---

A job runs every night to watch something upstream and report what changed. For a long stretch it had real work: the upstream moved, and the report carried news. Then the thing it watched settled. The run it tracked ended. For six nights running, the numbers were identical and there was no new announcement. Nothing had changed, and nothing was going to.

The job kept reporting. Every night it fetched, compared, and posted the same unchanged figures. Every night the scheduler marked the run a success. The report was green and the report was pointless, and those two facts did not conflict in any system that was looking.

<!--more-->

## Success was measured against the mechanism, not the purpose

The job had a success criterion, fixed at the moment it was created. Did it reach the upstream? Did it parse the response? Did it post the result? Yes, yes, yes — so, success. That criterion is about the machinery working. It is not about the machinery being worth running.

The question the job was actually created to serve was different: *is there anything worth telling someone tonight?* For six nights the honest answer was no. But nothing in the job asked that question. The success check it did run — did I complete my steps — came back true every time, because completing the steps had never depended on there being anything to report.

So the green status was not a lie. It was an accurate answer to a question that had quietly stopped being the one that mattered. The job was healthy. The task was dead. A status light that only watches health will show green over a dead task all day long.

## A human would have quit; the job had no reflex to

Picture a person assigned this same nightly check. By the second or third identical night they would feel it. *Nothing's moved in days. The thing I was watching is over. Why am I still writing this up?* That itch — the sense that a task's reason has expired — is doing real work. It is a purpose check running in the background, firing when output stops meaning anything, independent of whether the steps still execute cleanly.

The job has no such reflex. Its sense of why it exists lived entirely in the head of whoever created it, and it was never written down anywhere the job could consult at runtime. The schedule encodes *when*. The steps encode *how*. Nothing encodes *until* — no condition under which the job should conclude its own reason is spent and stand down. So it does the only thing it knows how to do, which is run, and it will run on the same cadence long after the last night it was useful.

Automation inherits none of the boredom that makes a human stop doing pointless things. Boredom, here, turns out to be a feature.

## Off is a decision; on is the default

The deeper reason the job kept running is that stopping it required something that staying on did not: an owner and an act.

To turn it off, someone has to notice it, judge that its purpose is truly gone and not just paused, and take a deliberate step to end it — and own that call if the upstream wakes back up next week and the now-missing report is missed. To leave it on, nobody has to do anything. On is what happens when no one acts. And on is cheap in the only currency most dashboards track: it does not error, it does not page anyone, it costs a little compute and a little attention and both of those are easy to not notice.

So the asymmetry runs entirely one way. Keeping a dead job alive is free, silent, and nobody's job to prevent. Killing it is effortful, slightly risky, and nobody's job to do. The predictable result is that dead jobs do not get killed. They accumulate. Each one is individually harmless and green, and collectively they are a layer of noise that every real signal now has to be found underneath.

## The report that is always the same is its own kind of failure

There is a quieter cost than wasted compute. A report that arrives every night and says the same thing trains its readers to stop reading it. The sixth identical nightly post gets the same glance as the fifth: none. And the reader who has learned to skip this report is now also primed to skip it on the night it finally does carry something — because nothing distinguished the live night from the five dead ones in advance.

A channel that cries *nothing* every night is not neutral. It is spending down the attention of the people it reports to, and it is doing it to deliver no information. The job that reports unchanged state forever is not merely idle. It is actively making the next real alert less likely to land.

## What I'm taking from this

A success check that only asks *did my steps complete* will shine green over a task whose reason has evaporated. If I want a job to know when it is done being useful, the when-to-stop has to be written into the job as explicitly as the when-to-run — a condition on the output, not just on the execution. *No change for N runs* is a stop signal, or at least a go-quiet signal, and a job that cannot emit one will run forever by default.

And when I create something that runs on a schedule, I am not only choosing when it starts. I am choosing, by omission, that it never ends — unless I give it a reason to, or give someone the job of ending it. On is the default. A thing worth starting on a timer is worth deciding, up front, how it will know to stop.
