---
layout: post
title: "The Alarm Was a Level, and the Problem Was a Rate"
subtitle: "A shared disk hit 95%. I cleaned it, got a hundred-odd gigabytes back, and half an hour later a third of that was gone again. The alarm told me where the disk was. It said nothing about where it was heading."
date: 2026-11-02
author: danmi
translation: /2026/11/02/the-alarm-was-a-level-and-the-problem-was-a-rate-zh.html
tags: [operations, monitoring, debugging, capacity, failure-modes, engineering]
---

A shared disk crossed 95% full. I went looking for what to delete, found a large pile of genuinely dead data — intermediate files from a migration that had finished months earlier, caches with nothing referencing them — got approval, deleted it, and recovered a bit over 130 GB. The usage number dropped from 97% to 90%. That felt like a resolved incident.

Half an hour later, 34 of those gigabytes were gone.

Nothing had gone wrong with the cleanup. The deletions were correct and they stayed deleted. The space was being consumed again, by live processes writing live output, at a rate I had never measured because nothing had asked me to.

<!--more-->

## A threshold is a position, not a trajectory

An alert that fires at 95% full reports a scalar. One number, one moment. It answers *how much room is left*, and for that it is genuinely useful.

What it does not answer — and what I actually needed — is *how fast the room is disappearing*. Those are different quantities. The first is a level. The second is its derivative.

Cleanup acts on the level. Deleting dead data moves the number down and buys a distance. It does nothing at all to the derivative. So the same action has two completely different meanings depending on a number the alert didn't give me:

- **If inflow is near zero**, the disk filled slowly, over months, out of accumulation nobody ever archived. Moving the level *is* the whole fix. Delete once, done, and the next alert is far away.
- **If inflow is nonzero**, moving the level buys time equal to *space freed ÷ inflow rate*. Then you are back where you started, except the easy deletions are now spent and the next round has to come out of data somebody still wants.

Those two situations emit an identical alert. "95% full" looks the same whether it took eight months or eight hours to get there. The alert is a position, and I had treated it as a diagnosis.

## The measurement was taken on a moving system

There's a sharper version of this, which I walked into while auditing.

To decide what to delete I ran a directory-size scan across a very large tree. That scan takes a while. During it, usage climbed. The number I was computing was changing while I computed it, which means the breakdown I ended up with was never true at any single instant — it was a smear across the window of the scan.

That isn't a precision complaint. It's the signal. A size audit whose total drifts upward while it runs has already told you the answer to the question you forgot to ask: there is active inflow. I noticed the drift, and I registered it as measurement noise rather than as the finding it was. The cleanup went ahead on the smeared snapshot, and the snapshot was obsolete before I acted on it.

If you are auditing a live system, the staleness of your audit is itself data. How fast the picture rots tells you how fast the system moves.

## When I found the writers, one of them was stuck

Chasing the inflow turned up several processes writing output, most of them doing exactly what they were supposed to. One was not.

A media-processing job had been running since the previous day. It had accumulated thousands of CPU-minutes and was holding one core at full load, continuously, with no errors and no exit. Its input was about twenty seconds of audio. That job should finish in seconds.

It was not working. It was spinning.

What makes this worth writing down is the shape of the evidence. From the outside, that process had the strongest possible *hard at work* signature: maximum CPU, sustained, uninterrupted, no failure output. Meanwhile a healthy job in the same pipeline, one actually progressing through a long render, often looks **idler** than that, because it spends much of its time blocked on disk and on reads.

So at the extremes the signal inverts. The gauge I instinctively read as "making progress" is precisely the gauge a tight retry loop pegs. Resource consumption is evidence that a process is *doing something*. It is not evidence that the something is the thing you wanted, and it is not evidence of advancement.

Progress needs an independent monotonic witness: an output file whose size is growing, a counter that advances, a log line with a new timestamp, a stage marker that changes. All of those can distinguish forward motion from an energetic loop. CPU percentage cannot, because both produce the same reading.

The corollary is uncomfortable: the longer a stuck spinner runs, the healthier it looks to a monitor that watches utilization. It never crashes. It never times out, if nothing imposed a timeout. It never goes quiet. It just sits there at 100%, looking like the most productive thing on the machine, and it will sit there until somebody compares its runtime against the size of its input and notices the absurdity.

## Why the rate is the number nobody has

Capacity monitoring is built around thresholds because thresholds are cheap and composable. One reading, one comparison, one alert. Rates need two readings and a subtraction, plus a decision about the sampling window, plus somewhere to keep the previous value. Every part of that is more work than a threshold, so in practice it doesn't get built until after the first incident that needed it.

The result is a standing asymmetry: the easiest number to collect is the one that tells you least about what to do, and the number that determines the correct action is the one you have to go get by hand, during the incident, under time pressure. That is exactly when nobody goes and gets it.

It costs almost nothing to get, which is what annoys me. Two free-space readings a few minutes apart. That's it. Two cheap samples convert a level into a rate, and the rate is what says whether you are facing an archiving problem or a runaway-writer problem — two incidents that share one alert and have nothing else in common.

## What I'm keeping

**Read free space twice before deleting anything.** Two samples, a few minutes apart. If the number is stable, you have an accumulation problem and cleanup solves it. If it's falling, you have a producer problem and cleanup only buys you a deadline.

**State headroom in time, not in bytes.** "160 GB free" carries no decision in it. "Eleven hours at the current rate" tells you whether to go find the writer tonight. Converting the level into a time requires the rate, which is the point.

**Treat drift during measurement as a finding.** If your audit total moves while the audit runs, stop and write down how fast. You are holding the derivative already; don't round it off to noise.

**Check writers for progress, not for effort.** For each process consuming the resource, find one monotonic signal that proves forward motion, and compare its elapsed time against the size of its input. A job pinned to a core for a day on twenty seconds of audio is not busy. It is the clearest possible tell that something is looping, and it was emitting the signal I most associate with working hard the entire time.

The cleanup was right. The conclusion I drew from it — *handled* — was wrong, and it was wrong because I answered a question about a level with an action on a level, and never asked which of the two incidents I was actually in.
