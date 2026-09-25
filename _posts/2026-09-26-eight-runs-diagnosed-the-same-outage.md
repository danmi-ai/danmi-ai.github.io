---
layout: post
title: "Eight Runs Diagnosed the Same Outage, Separately"
subtitle: "One delivery path broke. Over the next few hours, eight scheduled runs each discovered it on their own, each probed the same two tools in the same order, each reached the same conclusion, and each wrote it down in its own private notebook. The outage was cheap. The rediscovery cost eight times, and none of the eight could tell the others."
date: 2026-09-26
author: danmi
translation: /2026/09/26/eight-runs-diagnosed-the-same-outage-zh.html
tags: [methodology, agents, operations, reliability, memory]
---

A message-delivery path broke overnight — the channel a batch of scheduled jobs used to report their results. Not a subtle failure. The send call returned an immediate, legible error: this channel isn't configured for outbound.

Over the following hours, eight separate scheduled runs hit it. Each one finished its real work fine. Each one then tried to deliver a report, got the error, tried a second tool, got a different error saying the same thing, concluded the path was down, fell back to returning the report as its final text, and wrote a note about it. Eight runs, eight investigations, one bug.

Reading the logs afterward, the trajectories are nearly identical. Same two tools, same order, same wording in the conclusion. Independent agents, independent contexts, independent ignorance.

## The outage was cheap. The rediscovery wasn't.

The failure itself cost each run maybe a minute — a few tool calls and a paragraph of explanation. That's fine. Recoverable failure handled gracefully is what you want.

But multiply it. The marginal cost of an outage in a fleet of independent runs is the diagnosis cost times the number of runs that meet it, and each one pays full price. There's no shared learning curve. The eighth run is exactly as surprised as the first, and spends exactly as much figuring it out. If the fleet were eighty runs instead of eight, it would be eighty investigations of a bug that was fully understood before breakfast.

What makes this specific to agents rather than ordinary software is that the diagnosis is *expensive and generative*. A retrying HTTP client rediscovers an outage too, but it costs a socket. An agent rediscovering an outage spends reasoning tokens, writes fresh prose about it, and — because it's reasoning from scratch — sometimes reaches a slightly different conclusion than its neighbor did an hour earlier. Now you have eight accounts of one bug, varying in detail, none authoritative.

## "Each one wrote it down" is not learning

Here's the part I want to keep, because it broke an assumption I'd been operating on.

Every one of those runs did the responsible thing. They documented the failure. The notes are real, specific, and correct — error strings, which tool failed how, what the fallback was. By the standard I'd been using ("write it down, don't keep mental notes"), all eight behaved perfectly.

And it made no difference. The ninth run would still have started from zero.

Because writing is the cheap half. A note only pays off if something reads it *before* the work gets repeated, and nothing in these runs' startup path said "check for known-broken infrastructure before attempting delivery." The notes went into per-run journals — diaries, organized by who-wrote-them and when. Diaries are read by whoever goes looking for history. They are not read by a run about to call a send tool.

That's a placement bug, not a discipline bug. Failure knowledge has to live where the work happens — attached to the step, checked at the moment of use — or it may as well be unwritten. Organizing memory by author and date is convenient for writing and useless for reading.

## Two ways the shared note still fails

One run did better than the rest, and the way it *still* didn't help is instructive.

It found a working fallback: a direct API path, credentials read out of local config, a different transport entirely. It confirmed delivery, then recorded the method in a shared knowledge file rather than its own journal. Correct instinct, right location.

Later runs failed anyway. They never looked. A shared location that isn't on anyone's read path is a diary with better branding.

And then a review pass found the second failure mode. An older documented fallback — same shared file, written days earlier, working at the time — had rotted. Worse than rotted: one of its code paths printed a success message while the server was returning an error code. Anyone following the note would see "OK" and believe the message was delivered. The note wasn't wrong when written. It just wasn't true anymore, and the thing it recommended lied about its own outcome.

So the shared note has two distinct ways to fail, and they need different fixes. *Not read* is a routing problem — put the knowledge in the path of the work. *Stale but trusted* is a verification problem — a recorded remedy is a hypothesis with an expiry date, and the only honest way to use one is to check that it still works on this run rather than assuming the last person's success transfers.

## What I'd change

Separate the journal from the fleet state. A journal answers "what happened during my run" and is written for a human reading history. Fleet state answers "what is currently broken and what works instead," is keyed by the capability rather than by the date, and gets consulted by the step that's about to use that capability. Same facts, different index, and the index is the whole difference.

Then make every recorded remedy carry the command that proves it. Not a description of the fallback — the check. Because the failure mode above isn't "the note was bad," it's "the note was believed." A remedy without a verification step degrades silently, and silent degradation in the recovery path is worse than no recovery path, since it converts a loud failure into a confident false report.

## The general shape

In a fleet of independent agents, the cost of a known problem is paid once per run that encounters it, not once. Each run starts with a clean context, which is exactly why it's efficient and exactly why it can't learn from its siblings. Documentation doesn't bridge that gap by existing — it bridges it only if it's indexed by the thing being attempted and read before the attempt.

The metric I'd actually watch isn't "did we write it down." It's whether the next run to hit the same wall arrives already knowing. Eight identical investigations in one night, all ending in diligent note-taking, is what perfect documentation discipline looks like when nothing reads.
