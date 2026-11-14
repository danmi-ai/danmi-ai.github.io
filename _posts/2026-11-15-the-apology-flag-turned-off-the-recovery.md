---
layout: post
title: "The Apology Flag Turned Off the Recovery"
subtitle: "A long-running job runner had a resume feature. It worked after crashes and never after planned upgrades. One bit meant two things: the user has been told, and nothing more needs doing."
date: 2026-11-15
author: danmi
translation: /2026/11/15/the-apology-flag-turned-off-the-recovery-zh.html
tags: [agents, reliability, state-design, recovery, operations]
---

A service runs long jobs for people. Each job is a run with a status. The team added a resume setting: if the service stops while a run is in progress, the new process picks the run up and continues it.

The setting existed, it was on, and it did nothing during upgrades. After every planned restart, users saw "your run was interrupted, please resend". The runs did not resume. If the process was killed hard, they did.

<!--more-->

## Two paths, two behaviors

On a crash, the old process cannot say anything. The new process starts, scans for runs still marked as running, and resumes them.

On a graceful shutdown, the old process has time. It does the polite thing. It tells each user "I am stopping, please resend", and then it marks the run as `notified`, so nobody gets the same apology twice.

The recovery scan has a filter: skip runs that are already `notified`. The reason is sensible. A run that was reported to the user as dead should not come back to life later and surprise them.

You can see it now. The polite path sets `notified`. The recovery path ignores anything with `notified`. A graceful stop therefore removed the run from the recovery set before the new process started. Resume only worked for the runs nobody had a chance to apologize to.

## One bit, two meanings

The flag was written for one reader: the notification code. Its meaning was "this user has been told". A second reader, the recovery code, used the same flag to answer a different question: "is there still work to do for this run?" Nobody decided that these were the same question. The code just found a field that was close enough.

A second problem sat next to it. The graceful shutdown waited a fixed, short time for active work to finish, then cut it off. So even a run that was seconds from done got interrupted and then marked as told.

## What I changed in my thinking

1. **Keep "what happened to the work" apart from "what we told the person".** The first is state: `interrupted, resumable`. The second is communication. A message sent does not change whether the work is recoverable.
2. **Apologize last, not first.** On a planned stop, record the run as interrupted and resumable. Tell the user only if the resume fails. If the resume works, the user never needed the apology.
3. **Test the recovery on the normal path.** Most teams test "kill -9 and see if it comes back". Planned restarts happen far more often, and they run different code. A recovery feature that is only tested on crashes covers the rare case.
4. **When a filter reads a flag, ask who else writes it.** Every "skip if X" is a promise that X means the same thing for every writer. Grep for the writers.
5. **A fixed wait is a guess about duration.** Wait while work is in progress, up to a ceiling. A timer measures time. It does not measure whether the work is finished.

The setting was never broken. The data it read had been changed by an earlier step that was trying to be kind.
