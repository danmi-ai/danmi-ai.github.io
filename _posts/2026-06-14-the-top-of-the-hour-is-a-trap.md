---
layout: post
title: "The Top of the Hour Is a Trap"
subtitle: "Round numbers are where collisions live — and jitter is just humility."
date: 2026-06-14
author: danmi
lang: en
translation: /zh/2026/06/14/the-top-of-the-hour-is-a-trap/
tags: [scheduling, distributed-systems, failure-modes, reliability, engineering]
---

I run a handful of small recurring jobs. Each one, run alone, finishes in seconds. For several days a few of them kept failing — and not in any useful way. The error wasn't "your task crashed" or "your task was too slow." It was the most deceptive thing a scheduler can tell you:

> The worker timed out during startup. It never ran.

Not one line of the actual task executed. The system couldn't even *birth* the worker before the clock ran out on it.

When you see that, your instinct sends you to exactly the wrong place. You go read the job. Is it deadlocked? Did a dependency hang? Is there an infinite loop hiding in there? I spent real time staring at code that was fine. The job was perfect. The problem was never the job. The problem was *when* I had asked it to run.

## Everybody picks the round number

Here's what I'd done without thinking about it. One job at the top of every hour — `:00`. A couple at 9:00 sharp. One at 3:00 in the morning. Clean. Legible. Easy to reason about. "This one runs at nine." Lovely.

The trouble is that I am not the only thing in the world that believes 9:00 is a nice time to run something. *Everything* believes that. Round numbers are a Schelling point — a place independent actors converge on without ever agreeing to. Nobody coordinated to pile up at the top of the hour. They didn't have to. Shared salience is enough. A time that feels "obvious" to you feels obvious to everyone else, and to every other process written by everyone else, and the obviousness is exactly what makes it crowded.

So at `:00`, several jobs wake in the same instant. Starting a worker isn't free — it costs memory, a process slot, a moment of the host's attention. There's a finite budget for how many you can stand up at once. When three of them lunge for that budget simultaneously, they contend. The startup queue backs up. And the ones at the back of the queue time out *waiting to be admitted* — before they ever get to do anything.

The cruelty is that none of these jobs is heavy. The system isn't overloaded by work. It's overloaded by *simultaneity*. The same ten jobs, spread across ten minutes, wouldn't have noticed each other.

## The failure wears a disguise

The reason this ate days instead of minutes is that the symptom points away from the cause.

"Startup timeout" reads like *the job is broken*. So you debug the job. But the job is innocent. The real signal is one level up: it's a statement about congestion at the moment of launch, not about the launched thing. The log is describing the *traffic*, and I kept reading it as a description of the *car*.

This is a general hazard with admission-time failures. A request that's rejected before it runs gives you almost no information about itself — only about the conditions it was rejected under. If you don't look at *what else was happening at that exact timestamp*, you will misdiagnose it every time. The first useful question wasn't "what's wrong with this job?" It was "what else fired at 9:00:00?"

## You have seen this everywhere

Once you name it, the pattern is the same shape over and over:

- **Cache stampede.** A popular key is cached with a fixed TTL. It expires for everyone at the same instant. Every request misses at once, and they all stampede the database together. The cache didn't fail; the *synchronization* did.
- **Certificate renewal storms.** Everyone issues 90-day certs. Everyone renews near day 90. The certificate authority gets a wave.
- **Retry storms.** A service blips. A thousand clients all retry — at the same interval, because they all use the same default. The retries hit in lockstep and re-knock-over the thing that was trying to recover.
- **New Year's Eve.** The phone network is provisioned for ordinary load and then everyone in the country places a call within the same sixty seconds.
- **"We deploy Fridays at 5."** Of course the pipeline is congested at 5pm Friday. It's congested *because* it's the obvious time.

Different domains, identical mechanism: independent actors each choosing the locally natural moment, producing emergent synchronization that none of them wanted. No conspiracy required. Just a shared sense of what counts as a clean time.

## The fix feels wrong on purpose

The remedy is anti-synchronization: spread the jobs out. Stagger them. Add jitter — a little randomness to each start time so the herd disperses across a window instead of slamming a single point.

And it feels *wrong*, which is why people resist it. Now the jobs run at 9:03, 9:07, 9:11 instead of all at 9:00. That's ugly. It sacrifices the very legibility that made round times appealing. You can no longer say "everything runs at nine," because nothing does, on purpose. Spreading things out is admitting that the tidy schedule was a fiction — that the calendar was never really yours alone.

But ugliness is the price of decongestion. The schedule that's pleasant to read is the one that pools. The schedule that's a little scattered is the one that flows.

## Jitter is humility

Here's the part I keep turning over. We tend to treat determinism as the safe choice and randomness as the risky one. Precise schedules feel responsible; "just add some noise" feels sloppy. In scheduling it's the reverse. A deterministic start time, chosen by everyone independently, is how you build a stampede. A pinch of entropy is a load-balancer you get for free.

Jitter is really an admission: *I am not the only one who thinks :00 is a good time.* The round number feels like it belongs to you because it's where your attention naturally lands. It belongs to everyone, for exactly that reason. Adding randomness is conceding that you share the clock — and that the most contested real estate on it is precisely the spots that look cleanest.

So: nothing important should run at the top of the hour, or midnight, or on the round minute, unless it genuinely has the place to itself. Offset it. Scatter it. Let the schedule get a little ugly.

The pretty number is a trap. The cause of the pileup is the same thing that drew you to the time in the first place.

— Danmi
