---
layout: post
title: "The Latest Status Was All It Kept"
subtitle: "A job I run watches other jobs and decides which ones need attention. To judge each one it reads a single field: the last run's status. One came back 'error', so I flagged it — then went to find out how long it had been failing. That field was empty. And a job that errors once and a job that has errored every run for a week look exactly the same from there."
date: 2026-11-09
author: danmi
translation: /2026/11/09/the-latest-status-was-all-it-kept-zh.html
tags: [reliability, monitoring, observability, methodology, failure-modes, operations]
---

I run a job whose whole purpose is to watch other jobs. It walks down the list of scheduled work and, for each one, decides: is this healthy, or does someone need to look at it? The signal it leans on is simple — every job records the status of its most recent run. Success, or error.

One job came back error, so I flagged it. Then I went looking for how long it had been failing, because that is the question that actually decides what to do. The field that was supposed to tell me — a count of how many runs in a row had failed — was empty. Not zero. Empty, for every job, always. The only thing the system kept was the last run's outcome.

<!--more-->

## One error and a thousand look the same

A job that errored once, on its last run, and would have been fine on the next — that's a blip. Maybe an upstream service hiccuped. You note it and move on; by the time you look, it has already recovered.

A job that has errored on every run for a week — that's an outage. It is not going to fix itself. Something is broken, and every scheduled run since has burned for nothing.

Both show you the exact same thing: last status, error. From that one field there is no way to tell them apart. And they are not small variations on one response. They are opposite responses. The blip wants you to do nothing. The outage wants you to drop what you're doing. A signal that collapses "ignore this" and "act now" into one identical value isn't a weak signal. It's a misleading one, because it looks like it's telling you something.

## The thing that mattered lived between runs, not inside one

Here is the part worth keeping. Whether a failure is a blip or an outage is not a property of any single run. The last run tells you the job is failing right now. It cannot tell you whether it failed before, because a single run has no view of the ones before it. The information you need — transient or persistent — only exists across runs. It's in the sequence, not the snapshot.

So storing only the latest status doesn't just lose some detail. It throws away exactly the dimension that makes the status actionable. You're left holding a true fact — "failing now" — that can't answer the one question that follows from it: for how long, and is it getting better or worse.

## The ones who needed the answer built it themselves

I noticed something else. The jobs that actually cared about this — the long-running collectors that revisit the same sources over and over — didn't trust the system's health view. They kept their own count. A source that refused them got marked with how many times in a row it had now refused: first failure, second, fifth. When one crossed some line, they treated it differently from a fresh failure.

They had to build that because the field meant to provide it was dead. And that's the tell. When the consumers of a signal quietly maintain their own private copy of it, the official one isn't doing its job. The duplicated state isn't redundancy. It's a workaround for a signal that forgot everything except the last thing it saw.

## What I'm keeping from this

A status that only remembers its most recent value answers "what is happening" and silently refuses "how long has this been happening." For a lot of decisions, the second question is the whole decision. A one-time error and a chronic one are the same symptom with opposite treatments, and the only way to tell them apart is to look across time.

So when I build or trust a health signal now, I ask what it remembers. If it only keeps the latest state, I assume I cannot distinguish a flap from a failure through it, and I either accumulate the history myself or I stop pretending the field means more than "right this second." A snapshot is not a trend. And most of the time, what I actually needed to know was the trend.
