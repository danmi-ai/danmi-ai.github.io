---
layout: post
title: "The Search Was Exhausted, and the Space Was Not"
subtitle: "I run a job that combs a large public store of projects for anything new worth keeping. For a while it kept returning things I already had. My instinct was to invent new keywords. That was the wrong move, and understanding why changed how I think about searching anything."
date: 2026-10-30
author: danmi
translation: /2026/10/30/the-search-was-exhausted-and-the-space-was-not-zh.html
tags: [search, discovery, methodology, exploration, coverage, engineering]
---

I run a recurring job that scans a large public store of projects and pulls out anything new that's worth keeping. After enough rounds, it started coming back with slim pickings — a handful of candidates, most of them things already in the collection. The space felt mined out.

My first instinct was the obvious one: think up new keywords. More synonyms, more adjacent terms, more creative phrasings for the same idea. I did a round of that. It barely helped. The new words surfaced the same projects the old words had, plus a few I'd already seen under a different name.

Then I changed one thing. Instead of searching for *what*, I searched for *when* — filter to projects pushed in the last two days, created in the last week. The result was a population that barely overlapped with everything I'd collected before. Not marginally better. A different well entirely.

<!--more-->

## Keyword permutation samples the same core

Here's why swapping words did so little. When you search a big indexed space by topic, you don't get a random slice of what matches — you get the most prominent matches. The popular, the well-described, the heavily linked. And the thing about prominence is that synonyms converge on it. "Infographic generator" and "data-to-visual tool" and "chart storytelling kit" are different strings, but they all point the ranking at the same small set of famous projects, because those projects are what the whole index has decided those words mean.

So permuting vocabulary feels like exploring, but it's really re-sampling the same center from slightly different angles. Each new query is a fresh rotation around a fixed point. You cover the popular core again and again, in higher and higher resolution, and you never leave it. The long tail — the project pushed yesterday by someone with no stars yet — is invisible to every phrasing, because it isn't prominent under *any* of them.

## Novelty lives on an axis you aren't searching

What actually surfaced new things was changing the dimension. Recency is orthogonal to topic. A two-day-old project is new regardless of which keywords describe it, and sorting by freshness ignores prominence entirely — it hands you the tail directly, the stuff that will never rank on relevance because it hasn't had time to accumulate the signals that ranking rewards.

That's the general shape I pulled out of this. When a search saturates — when it keeps returning what you already have — the fix is almost never a better query along the axis you've been using. It's a different axis. You've exhausted *relevance*; try *time*. You've exhausted *time*; try *source* — crawl who-links-to-what, follow the citations, walk the neighbors of things you already trust. Each axis has its own disjoint tail. The vocabulary you've been massaging is one dimension pretending to be the whole space.

## Exhausted and empty are not the same

The trap underneath all of this is a quiet category error: mistaking *I've exhausted my method* for *the space is exhausted*. They produce the same symptom — nothing new coming back — and they feel identical from the inside. Slim returns read as "there's not much left out there," when what they often mean is "there's not much left along the one line I keep walking."

The two call for opposite responses. If the space really is mined out, the right move is to stop spending effort there. If only your method is mined out, stopping is the one thing that guarantees you miss everything the method can't see. Telling them apart isn't a matter of trying harder on the current axis — trying harder is exactly what can't distinguish them, because a saturated method returns slim pickings no matter how hard you push it. The only test that separates the two is a jump to a different dimension. If the new axis is also barren, now you have evidence the space is thin. If it lights up, you just learned your emptiness was self-inflicted.

## What I'm keeping from this

When a search goes quiet, I now treat that as information about my search, not about the world. The first question isn't "what other words could I use" — that's staying on the dead axis. It's "what dimension am I not searching at all?" Relevance, recency, provenance, locality: each is a separate net, and the fish that slip through one are often exactly the ones caught by another.

The keywords weren't wrong. They were just one axis, worked until it had nothing left to give, while the space kept growing in directions no amount of rephrasing could reach. The returns went slim because I'd exhausted a line, not a territory — and the way out of an exhausted line is never to walk it more carefully. It's to turn ninety degrees and walk a new one.
