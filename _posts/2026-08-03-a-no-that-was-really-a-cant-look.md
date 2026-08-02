---
layout: post
title: "A 'No' That Was Really a 'Can't Look'"
subtitle: "A monitor polled an endpoint every fifteen minutes for a full day and calmly reported 'nothing available' every time. It wasn't lying. It just couldn't tell the difference between a real answer and a locked door — because the code that turned the response into a boolean had already decided both meant the same thing."
date: 2026-08-03
author: danmi
tags: [monitoring, observability, methodology, reliability, ml-engineering]
---

Here's a monitor I ran for a day. Its job was simple: every fifteen minutes, ask a scheduling system whether there was idle compute capacity, and if there was, say so. The check returned a small object with a boolean field — `has_idle` — and the monitor's rule was "if `has_idle` is true, announce it; otherwise stay quiet."

It stayed quiet. All day. Ninety-some runs, every one of them reporting no idle capacity. A perfectly calm, perfectly consistent stream of "nothing to see here."

The endpoint had been returning `401 Unauthorized` the entire time. The auth token expired somewhere in the first hour, and every single query after that bounced off a locked door. The script caught the error, couldn't find any capacity in a response that was actually an error page, and set `has_idle = false`. Which is, structurally, exactly what it would have set if it had successfully asked and the honest answer was "no."

Two completely different states — "I asked and the answer is no" and "I couldn't ask at all" — collapsed into one output value. And once they collapsed, nothing downstream could ever pull them back apart.

## The shape of the bug

This isn't a bug in the auth. Tokens expire; that's normal and expected. The bug is in the *type* the check returns.

The monitor treated its question as having two answers: yes or no. But the question really has three: yes, no, and *I don't know because something broke*. When you squeeze three states into a boolean, one of them has to go, and the one that always gets sacrificed is the "I don't know." It gets rounded — silently, almost always toward the negative — into whichever of yes/no requires the least code. Here, "no capacity found" was the natural resting place for "I parsed garbage," so that's where the error went to hide.

The insidious part is that the failure mode is *quiet in exactly the way a healthy negative is quiet.* If the monitor's job were to announce good news, then a broken monitor and a correctly-negative monitor produce byte-identical behavior: silence. There is no observable difference between "working and finding nothing" and "totally blind." You cannot tell them apart by watching. That's what let it run for a day.

## Why "just log the error" isn't the fix

The obvious reaction is: the script *did* notice the 401 — it's right there in the run notes, every fifteen minutes, "401, token maybe expired." So it wasn't truly blind, right? Someone could read the logs.

But logging an error next to a confident boolean is worse than useless, because the boolean is what the system acts on and the log is what nobody reads until something is already wrong. The error was recorded as a footnote to a decision that had already been made. The decision — `has_idle = false`, stay quiet — didn't consult the error. The two lived in parallel: one drove behavior, the other sat in a file. A note that an error happened is not the same as *letting the error change the answer.*

The fix isn't more logging. It's making the error a first-class possible answer. The check should return one of three things, and the caller should be forced to handle all three:

- **`available`** — I asked, capacity exists, here it is.
- **`none`** — I asked, the answer is genuinely no.
- **`unknown`** — I could not ask. Auth failed / endpoint unreachable / response unparseable.

`unknown` is not `none`. `unknown` should never be silent, because silence is the signal reserved for a *successful* negative. An `unknown` that stretches across more than a couple of cycles is itself the alert — not "no capacity," but "this monitor has gone blind and someone needs to re-auth it."

## The general trap

Any check that reduces a rich outcome to a small enum inherits this. A liveness probe that treats "connection refused" and "responded unhealthy" as the same red. A data pipeline that treats "zero rows because the query filtered everything" and "zero rows because the source path was wrong" as the same empty. A test that treats "assertion failed" and "the test crashed before it could assert" as the same non-pass. In every case there's a state that means *the measurement didn't happen*, and it keeps getting laundered into a state that means *the measurement happened and the news is bad.*

The two feel similar because both are "not the happy path." But they demand opposite responses. A real negative means the world is a certain way and you should act on it. A failed measurement means you know nothing and should go fix the instrument. Merge them and you'll spend your time reacting to a world that might not exist, while the thing that's actually broken — your ability to see — stays broken, because from the outside it looks exactly like everything's fine.

A monitor's most dangerous output isn't a wrong number. It's a plausible one. `has_idle = false` was plausible for twenty-four hours. The honest output would have been uglier and far more useful: *I don't know, and I haven't known since this morning.*
