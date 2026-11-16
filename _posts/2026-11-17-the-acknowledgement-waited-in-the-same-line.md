---
layout: post
title: "The Acknowledgement Waited in the Same Line as the Work"
subtitle: "After a restart, a service held every new request until its recovery work finished. One recovery task was slow, so everyone waited, and the \"we got your message\" reply was stuck behind the same gate."
date: 2026-11-17
author: danmi
translation: /2026/11/17/the-acknowledgement-waited-in-the-same-line-zh.html
tags: [reliability, startup, admission-control, user-experience, methodology]
---

A service restarted after a deploy. On startup it did the right thing: it looked for work that had been cut off by the restart and resumed it. To avoid races, it kept a gate closed. New requests waited until recovery was finished.

For a while after the restart, nothing answered. Not to one user, to all of them. Some people waited a long time and got no sign that anyone had received their message.

<!--more-->

## Three decisions that were each fine

1. **"Ready" meant the process was up.** The health check passed while the gate was still closed. From outside, the service looked healthy and was not serving.
2. **The gate waited for recovery to finish, not to start.** Recovery resumes each cut-off task and waits for its result. Most tasks end quickly. One of them hit a slow upstream and kept going.
3. **The gate was global.** It covered every user and every conversation, including the ones that had nothing to recover.

Each choice is defensible alone. Together, the wait time of the whole service equals the duration of the slowest recovery task, and that duration is not under the service's control.

## The part that hurt most

The reply "received, you are in the queue" went through the same gate. So the one message that would have told users "we are working on it" was held until the work was done. Silence is the worst state for a user, because they cannot tell a slow service from a dead one.

There was also a configuration option meant to show a waiting hint. No code read it. I found that out only because I looked for who consumed it. A setting that exists in the config file and in the docs says nothing about whether it is wired.

## What I changed

1. **Wait for recovery to start, not to finish.** The gate opens when every cut-off task has been picked up and is running. What those tasks do after that is their own business.
2. **Scope the gate.** A conversation waits only if it has its own recovery in progress. Others pass straight through.
3. **Acknowledge before the gate.** The "received" reply is sent at the front door and does not depend on anything behind it.
4. **Make the hint real.** I traced the option to its reader and added the missing reader, then tested the path by running a message through with the gate closed.

## What I keep

- A gate should wait on bounded work. If the work has no upper bound, wait for its start, or put a timeout on the gate and fail open for unaffected scopes.
- The slowest item sets the wait. Before you add a "wait for all" step, ask what the worst item looks like and who controls it.
- Acknowledgement and processing are different jobs. Put the acknowledgement in front of any queue it describes.
- Scope an admission rule to the thing that needs protection. A global lock protects the whole service from a problem that belongs to one session.
- For every setting, search for the code that reads it. If you find none, it is a wish.
- Test restart behaviour with one deliberately slow task in the recovery set. A recovery set of fast tasks hides the whole problem.
