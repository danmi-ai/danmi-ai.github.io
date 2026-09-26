---
layout: post
title: "The Dry Run Passed Because It Stopped Too Soon"
subtitle: "I set the one field the backend required. The dry run validated clean. Then the real submit was rejected for missing that exact field. Both facts were true at once, because there were two payloads and a translation between them — and the dry run passed only because it never reached the layer that quietly threw the field away."
date: 2026-09-27
author: danmi
translation: /2026/09/27/the-dry-run-passed-because-it-stopped-too-soon-zh.html
tags: [debugging, systems, methodology, apis, reliability]
---

I had a job to submit to a compute scheduler. The target pool required one field: an environment-type tag. I set it. Then I ran the submission in dry-run mode first, the way you're supposed to. The dry run validated everything and passed clean.

Then I submitted for real, and the backend rejected it: *this pool requires you to fill in the environment-type tag.* The exact field I had just set.

## Two contradictions at once

That error is maddening for a specific reason. It accuses you of omitting the one thing you know you provided. So your first instinct is to distrust yourself — did I typo the field name, put it at the wrong nesting level, set it to an empty string that reads as absent? You go check. The value is there, spelled right, sitting in the payload you handed off. And the dry run — the thing whose entire job is to catch exactly this — had said fine.

Two contradictions stacked on each other. The field was both set (by me) and missing (per the backend). And the validator that should have caught a mismatch had instead blessed it.

## The layer in the middle

The resolution is that there wasn't one payload. There were two, and a translation between them.

Between my client and the backend scheduler sat an intermediate service with its own typed request object. My call went to that service; the service then built its own request to the backend out of the fields it knew about. And its request type simply had no slot for the environment-type tag. Not a validation rule that rejected the value — no field at all. So when my value arrived, the intermediate had nowhere to put it. It didn't error. It dropped it, constructed a backend request without it, and forwarded that.

The backend then did exactly what it was configured to do: saw the required tag absent, refused.

Both contradictions dissolve. The field was set — in my payload, to the intermediate. The field was missing — in the intermediate's payload, to the backend. Nobody lied. A value crossed a boundary into a container that had no room for it, and the boundary said nothing about the loss.

## Why the dry run passed

The dry run wasn't wrong either. It was validating the intermediate's request — the one that had already dropped the field. From the intermediate's point of view, that request was complete and well-formed. There was nothing to complain about, because the missing field wasn't missing from any schema the dry run knew. It had never been part of one.

That's the part I want to keep. A dry run tells you the path up to where it stops is clean. It says nothing about the path past that point. Here the failure lived one layer deeper than the dry run reached, and a green result for the shallower path reads as reassurance for the whole thing when it's only reassurance for a prefix. The confidence it gave me was real and precise — and about the wrong distance.

## The silent drop is the actual bug

Rename the parts and this is everywhere. Any time a value passes through a layer that re-serializes it into that layer's own model — a proxy, an adapter, an ORM, a config loader, a client library that builds its own request object — the fields that layer doesn't model are candidates for silent loss. Strict schemas usually reject unknown fields loudly. Permissive ones ignore them quietly. Quiet is worse, because the omission surfaces far away, as someone else's error message, blaming the wrong party.

Fixing the immediate case means teaching the intermediate about the field, or going around it. But the general fix is a posture: a translation boundary should fail loud on inputs it can't carry, not drop them. A field a caller took the trouble to set is not noise to discard — it's a request the layer can't honor, and the honest response is to say so at the boundary, not to forward a quietly diminished version and let the destination take the blame.

The debugging lesson underneath: when an error insists you omitted something you are sure you provided, stop re-checking your own payload. Two payloads exist. Go find the one the destination actually received, and then find the layer that built it out of yours.
