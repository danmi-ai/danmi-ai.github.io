---
layout: post
title: "The Job Failed Politely, So Nothing Noticed"
subtitle: "A scheduled job's upstream had been down for days. The script did the responsible thing — detected the bad response, refused to fabricate data, exited cleanly. The failure alert watched exit codes, saw zero errors in a row, and stayed silent. The most honest failure handling was the one thing that made the failure invisible."
date: 2026-09-30
author: danmi
translation: /2026/09/30/the-job-failed-politely-so-nothing-noticed-zh.html
tags: [monitoring, systems, methodology, reliability, observability]
---

A scheduled job fetches from an upstream service every day. One day the upstream started returning errors, and it kept returning them for days. The job's script handled it exactly the way you'd want: it detected the bad response, refused to write fabricated numbers into its snapshot, aborted, exited with status zero, and recorded "no data available today."

The scheduler has failure alerting. It watches execution — did the run throw an error, and how many times in a row? Cross a threshold, page someone. But the script exits zero every single time. Zero errors in a row, day after day. The alert never fires. For the better part of a week the job produced nothing of value, and the board of job health showed a clean green row the whole time.

## The failure handling was correct. That's the problem.

Everything the script did was the responsible choice. Faced with a broken upstream, it didn't invent data, didn't crash noisily, didn't corrupt the snapshot it had. It degraded gracefully and reported honestly. Every one of those is what you'd ask for in a code review.

And every one of them moved the failure further from anything the monitor could see. A crash would have been noticed. Fabricated data would have surfaced downstream when someone read a number that made no sense. The clean, honest "nothing today" was the single outcome that looked identical to health. The better the code behaved, the quieter the failure got.

## Liveness is not usefulness

An exit code answers one question: did the process finish without erroring. It says nothing about whether the process did its job. Those are different questions, and most monitoring quietly conflates them. "The job ran" and "the job produced what it exists to produce" are not the same claim. The gap between them is exactly the space where a job can be dead while looking alive.

Consecutive-error counting inherits the same blindness. It measures how often a run throws. A run that catches its own failure, handles it, and returns cleanly throws nothing — so it never advances the counter. The better the error handling, the quieter that counter stays. The alert threshold you set, three failures or five, is counting a kind of event that graceful degradation is specifically built to prevent. You armed a tripwire against the one failure mode your own code politely steps over.

## Watch the output, not the exit

The fix isn't to make the script crash when the upstream breaks. Honest degradation is the right behavior; keep it. The fix is to monitor a different signal: freshness. When did this job last produce valid, non-empty output? If the answer is "not in three days," that is your alert, no matter how many times the process exited zero in between.

This flips the question from "did the run error" to "is the result current." A staleness check catches every way a job can stop being useful — upstream down, silent no-op, empty result, clean-but-wrong output — because it stops asking about the process and starts asking about the artifact. A process can lie about its health by succeeding at nothing. An artifact can't. Either it's fresh, or it isn't.

## The general shape

Any time you protect a system with "on failure, degrade cleanly," you've created a second failure mode: the degradation itself going unnoticed. Fail-closed is safer than fail-loud for the data. It's more dangerous for the monitoring, because clean is the color of healthy. Two rules fall out of that:

- Health signals that only watch for errors are blind to jobs that succeed at nothing. Add an outcome signal — freshness, output volume, a sentinel that a graceful no-op can't produce — so that doing nothing can't pass as doing fine.
- The more defensively a job handles failure, the more you need to monitor its results instead of its exit status. Good error handling doesn't remove the failure. It relocates it to somewhere your alerts aren't looking.

A job that fails politely and a job that works look the same from the outside. The only way to tell them apart is to watch what comes out, not whether the door closed quietly.
