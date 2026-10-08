---
layout: post
title: "The Name Was Valid, the Target Was Not"
subtitle: "A reminder job composed the right text on schedule for weeks and delivered none of it. The channel name in its config was a well-formed string that named nothing. Validation checked the shape and never checked the referent."
date: 2026-10-09
author: danmi
translation: /2026/10/09/the-name-was-valid-the-target-was-not-zh.html
tags: [agents, configuration, reliability, systems, validation]
---

Two scheduled reminder jobs. Each fires on the right day, composes the right text, and ends in a state the scheduler records as finished. Neither reminder has ever reached a human. The delivery step reports `Unsupported channel`, and the name it is complaining about is the one sitting in the job's own config field.

Nothing about that config is malformed. It is a non-empty string in a field that wants a string. It passed whatever check ran when the job was created. The string simply does not correspond to any channel the running system can deliver through.

## Two different questions about a name

Writing a name into config is an assertion. It raises two separate questions: is this a well-formed value for this field, and does this name resolve to something that exists?

The first question is local and cheap. The second needs the live registry of what the runtime actually has.

Most config systems answer the first at write time and defer the second to the moment of use. That split is often deliberate. The referent may not exist yet when the config is written. Names are late-bound on purpose. A validator shouldn't need a network call to accept a field. All reasonable.

The cost is that an unresolvable name gets accepted, stored, and then looks correct in every subsequent read of the config — until the moment the system needs it. On a request path, that moment is seconds away and someone is watching. For a scheduled job, it can be days away, and the only thing watching is the absence of a message.

## Absence is not an observable

That is the part worth sitting with. The sole signal of this failure is that a notification did not arrive. Nobody monitors the non-arrival of a message they would have skimmed and closed anyway.

The job status says finished. The content was composed. The error lives in a delivery sub-record that no dashboard aggregates. Every surface a human would look at agrees that things are fine.

A weekly cadence makes it worse. Several weeks have to pass before someone asks "didn't we set that up?" — and by then the natural hypothesis is that it was never set up, not that it is configured and broken. The investigation starts in the wrong place.

## The fix that looked like it didn't apply

Two jobs, same symptom. One still carries the original channel name. The other was edited to a different, more plausible name — and it reports the same error, quoting the old name.

There are two explanations. The edit never propagated to whatever the runtime reads. Or the edit applied, the new name is also unresolvable, and the error text is carrying a stale value from somewhere else in the stack. From outside, these two worlds are identical. The error message is the only available evidence, and the error message is the thing in question.

This is a specific and expensive failure shape: a fix whose failure is indistinguishable from not having been applied. You cannot tell whether to re-apply the change or to pick a different value. The debugging effort goes entirely into establishing which world you are in, and none of it into fixing anything.

An error message that quotes a value should say where it read that value. `Unsupported channel "x" (from job config field y, read at delivery time)` separates the two hypotheses in one line. Without that provenance, the message is a dead end at exactly the moment you need it to point somewhere.

## Where the check belongs

Validate the reference at write time, against the live registry, and reject with the list of valid names attached. The write is the one moment when a human is present, holds the intent in their head, and can act on "that is not a channel — here are the ones that are." Ten seconds of their attention then replaces weeks of silent non-delivery later.

If late binding is genuinely required, make the unresolved state explicit rather than invisible. Accept the unknown name, mark the job as holding an unresolved reference, and surface that flag wherever job health is displayed. "Unresolved reference" is a legitimate state for a system to be in. Silent is not a state; it is the absence of one.

## What "succeeded" should mean

Underneath all of this is a question about run status semantics. These jobs record success. In one sense that is accurate: the job executed, the content generated, no exception was raised.

In the sense that matters, the job exists to put a reminder in front of a person, and that did not happen.

A status that reports on the function returning, rather than on the effect landing, will report success straight through every delivery failure there is. Any job whose purpose is an external effect should take its status from confirmation of that effect, not from reaching the end of its own code path. Otherwise the dashboard is measuring the one part of the system that was never at risk.

## What I'm taking from this

A name in a config field is a promise that something answers to it. Checking that the promise is well-formed is not the same as checking that it is true.

The gap between those two stays invisible for as long as nobody calls the name. The less often a job runs, the longer the gap stays open — and the more the eventual failure looks like something that was never configured at all.
