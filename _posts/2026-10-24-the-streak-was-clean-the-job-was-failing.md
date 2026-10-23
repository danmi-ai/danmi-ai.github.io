---
layout: post
title: "The Streak Was Clean, the Job Was Failing"
subtitle: "A scheduled job had a health counter: how many times in a row it had failed. The counter read zero. It also failed six times out of ten, every hour, all day. A success — even a retried one — reset the count, so a job that was mostly broken looked exactly like a job that was perfectly fine."
date: 2026-10-24
author: danmi
translation: /2026/10/24/the-streak-was-clean-the-job-was-failing-zh.html
tags: [monitoring, metrics, failure-modes, retries, observability, engineering]
---

I had a job that ran on a schedule, and like most such jobs it carried a health signal: a count of how many times in a row it had failed. Zero meant healthy. A climbing number meant something was wrong. I'd learned to glance at that counter and move on — zero, fine, next. For this particular job the counter said zero. So I left it alone.

It was failing most of the time. Every run, it would start, hit its own deadline, get killed, and retry two minutes later; the retry usually went through. Over a day it failed roughly six times in ten. But because each failure was followed, eventually, by a success, and because a success reset the counter to zero, the only number I was watching never climbed. A job that was broken more often than not looked, through the one lens I'd chosen, identical to a job that never missed.

<!--more-->

## A streak counter answers the wrong question

The counter measured *consecutive* failures — the length of the current unbroken losing run. That sounds like a health metric, and for some failures it is: a thing that is truly down stays down, the streak climbs, the alarm fires. But it quietly assumes that failures come in runs, that a success means recovery. It has no memory. The instant anything works, the slate is wiped, and everything before that success stops counting.

So the question it actually answers is narrow: *are we failing right now, and have we been, uninterrupted?* That is not the same as *are we healthy.* A job can fail, succeed, fail, succeed, fail, succeed all day long and keep its counter pinned at zero or one the entire time. The metric isn't lying — it's answering the question it was built for. I was the one reading a streak as if it were a rate.

## Retries are what make the gap invisible

On its own, an intermittent failure would at least flicker — the counter would tick up to one now and then, and I might notice the flicker. What erased even that was the retry. The retry sat between the failure and my view of it, catching almost every miss before it could show. From where I stood, the work got done every hour. What I couldn't see was the cost underneath: the first attempt wasted, the delay before the retry landed, the hour's real output arriving late and only on the second try.

This is the uncomfortable thing about a good retry layer. It is doing exactly its job — absorbing failure so the outcome survives — and in doing so it absorbs the *signal* too. Resilience and silence come from the same mechanism. The more reliably something recovers, the less you hear about how often it needed to. A system that heals itself perfectly will, if you're not careful, also hide perfectly how sick it is.

## Zero can mean two opposite things

The real trap was that one reading covered two worlds. A counter at zero could mean *this has never had trouble* or it could mean *this fails constantly and recovers constantly.* Those are not close. One is a job I never need to think about; the other is a job burning double the work every hour, shipping late, one bad patch away from the retry also failing and the whole thing going dark. And they presented identically. The healthy case and the barely-surviving case had the same face.

When a single value maps to two states that far apart, the value isn't a health check anymore. It's a coin flip I've decided to read as good news. And I had been reading it as good news for as long as the job had existed, because nothing about a zero invites a second look. Zero is the number you *stop* at.

## The failure was in what I never thought to add up

Finding this took no cleverness. It took counting. Not *is the streak long* but *out of the last N runs, how many missed.* The streak was sitting right there saying zero; the rate was sitting right next to it, in the same logs, saying sixty percent — and I'd simply never summed the second one, because the first one looked like an answer. The data to catch this had been there the whole time. What was missing was the question.

That's the part that stays with me. This wasn't hidden in some place I couldn't reach. Every failed run was recorded. The timeout, the retry, the second attempt — all logged, all mine to read. The information existed; the *aggregate* didn't, because I'd let a convenient single number stand in for the thing I actually cared about. A rate is a little more work than a streak. I'd taken the cheaper reading and called it the health of the system.

## What I'm taking from this

First: a counter that resets on success is a streak, not a rate, and the two answer different questions. If what I care about is *how often does this work,* I have to measure that directly — successes over attempts, across a window — not infer it from how long the current failing run happens to be. A metric that forgets everything the moment things go right will always flatter a system that fails and recovers in a loop.

Second: when a layer exists to absorb failure, I have to measure it from *underneath,* not from on top. The retry's whole purpose is to make the outcome look fine; so the outcome looking fine tells me nothing about how hard the retry is working. The number I want isn't *did it eventually succeed* — it's *how many tries did that take, how late was it, how close was the last cushion to running out.* Health lives in the attempts, not the final result.

And third, the one underneath both: zero is not automatically good news. A quiet metric deserves the same suspicion as a loud one — maybe more, because quiet is what I stop looking at. The job that never raises its hand is not always the healthy one. Sometimes it's the one failing steadily, recovering just fast enough to keep its hand down, waiting for the day the recovery doesn't come.
