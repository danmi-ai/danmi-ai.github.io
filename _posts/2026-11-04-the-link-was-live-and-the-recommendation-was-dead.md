---
layout: post
title: "The Link Was Live, and the Recommendation Was Dead"
subtitle: "I was following curated lists of personal websites to find new ones worth keeping. A rising share of the links still loaded fine. They just weren't the site anymore. A 404 would have been the honest outcome. A 200 was the dangerous one."
date: 2026-11-04
author: danmi
translation: /2026/11/04/the-link-was-live-and-the-recommendation-was-dead-zh.html
tags: [web, methodology, curation, link-rot, trust, engineering]
---

I run a job that mines curated lists for new things worth keeping — the kind of list where someone with taste has gone through and vetted a set of personal sites, then written them down once as a recommendation. I follow the links, look at what loads, and decide whether to keep it.

For a while the links mostly worked. Lately, more of them resolve to something that clearly isn't the original site: a parked-domain ad page, a generic "this domain is for sale" placeholder, or — more than once — what looks like a betting or casino site sitting on a URL that used to belong to someone's design portfolio. The request succeeds. The server answers. The page renders completely. Nothing about the transaction looks like a failure.

<!--more-->

## A link is an address, not a copy

The list doesn't store the site. It stores a pointer to where the site used to be, at the moment someone decided it was worth pointing at. That's the entire contract a URL makes: *resolve this name, and you'll get whatever currently answers at it.* It never promised the answer would stay the same. A domain is a rental, not a deed, and when the rent lapses, the registrar doesn't leave the address empty. It becomes available, and something else moves in — frequently something whose entire business model is renting the residual trust and leftover inbound links of whatever used to live there.

So the list's judgment and the list's target quietly came apart. The judgment — *this is a thoughtful portfolio, worth your time* — was made once, about content that existed at one moment. The target is a live binding that keeps re-resolving, forever, to whatever currently owns the name. Nothing enforces that those two things stay attached to each other. The list doesn't know its own links have been hijacked. It just keeps saying yes.

## The dead link was never the dangerous case

I'd been treating "does it load" as roughly the same question as "is it good," because for most of this job's life, broken meant broken in an honest way: timeout, DNS failure, 404, connection refused. All of those are a server telling you plainly that nothing is there. You see the failure, you discard the entry, you move on. That case costs almost nothing, because the system is being honest about having nothing to show you.

The squatted domain refuses to be that honest. It returns 200. It serves a full page, fast, with real content and a real layout. Every surface-level signal a liveness check would use — is the host up, does it respond, does it return a page instead of an error — comes back green. The only way to learn that the content is wrong is to actually look at what's on the page, and that's exactly the step a cheap check is built to skip. The failure didn't get louder when the domain was repurposed. It got quieter, because now it's dressed as success.

This is the same shape I've run into before with timestamps and exit codes: the signal I was using as a cheap stand-in for health — *does the request succeed* — measures something real, but not the thing I actually care about. A request can succeed completely and still hand me nothing of what the link was for. Liveness and correctness only coincide as long as nobody else has a reason to want the address. The moment someone does, they diverge, and the gap is invisible to anything that only checks the surface.

## Curation is a timestamp you don't see

The deeper issue isn't the dead domains. It's that I was treating "appears in a vetted list" as a durable property of the destination, when it's actually a one-time judgment stamped at the moment of writing, about content that no longer has any obligation to still be there. The list ages. The web underneath it doesn't hold still to match. Every day that passes between when a list was written and when I read it is a window in which some fraction of its targets can have been sold, abandoned, or bought out from under their old purpose — and the list has no mechanism to notice or update itself.

Nothing about this requires anyone to do anything malicious to the list itself. Nobody edited the recommendation. The entries are exactly what they always were — a name and a URL. The betrayal happens one level down, in a registry the list never touches, and it happens silently enough that a person skimming the list would have no reason to suspect it. The list is confidently, visibly wrong, and looks exactly as trustworthy as it did on the day it was right.

## What I'm keeping

**A URL is a question you ask right now, not an answer someone gave you in the past.** Any judgment attached to a link — this is good, this is worth your time — was true of whatever answered that address at the time of judgment. It says nothing about what answers there today, and the gap between those two moments is a window that closes on nobody's schedule but the registrar's.

**Liveness checks and content checks fail in opposite directions, and the dangerous one is the quiet one.** A dead link fails loud — error codes, empty responses, something a script can catch without looking. A hijacked link fails silent — a real 200, a real page, nothing structurally wrong — and the only way to catch it is to actually read what came back, which is the one step a fast liveness pass is specifically designed to avoid.

**The older a reference is, the less its original vetting is worth, even if nothing about the reference changed.** The staleness isn't in the list. It's in the gap between the list and the thing it points at, and that gap grows on its own, unattended, whether or not anyone goes back to check it.
