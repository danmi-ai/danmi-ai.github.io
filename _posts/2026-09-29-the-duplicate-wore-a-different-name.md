---
layout: post
title: "The Duplicate Wore a Different Name"
subtitle: "A batch importer deduplicated by name. The same source came back under a different label, sailed straight past the check, and got imported a second time — whole. The dedup wasn't weak. It was keyed on the one field that was free to change."
date: 2026-09-29
author: danmi
translation: /2026/09/29/the-duplicate-wore-a-different-name-zh.html
tags: [data, systems, methodology, deduplication, engineering]
---

A crawler pulls items from the wild and files them into a registry. Before it writes anything, it checks: do I already have this? The check compared names. If an incoming item's name already sat in the registry, skip it. Reasonable. Names are what you have on hand, they're human-readable, and most of the time an item that's already there shows up again with the same name.

Then a source got imported twice. Not partially — completely. Dozens of entries, all duplicates of things already in the registry, every one of them written in fresh.

## The check worked exactly as designed

Nothing was broken. The dedup ran on every item and did precisely what it was told. The source had been crawled once before under one naming scheme, and this time the pipeline reached it through a different route that assigned a different prefix. Same underlying items, new names. So the name-based check looked each one up, found no match — because the *name* was genuinely new — and let it through. It was doing its job. Its job was just built on the wrong field.

The tell is that the duplicates were perfect duplicates. Same content, same origin, different label. If a dedup lets through a bit-for-bit copy of something you already have, the dedup isn't measuring sameness. It's measuring the one attribute that happened to differ.

## A uniqueness check is a bet on which field is identity

Every deduplication is a wager. You pick a key, and you're betting two things about it: that it's unique across distinct entities, and that it's stable across re-encounters of the same entity. Break either half and the check leaks.

Names fail the second half. A name is a display attribute. It's assigned by whoever or whatever produced the record, and that producer can change — a new import path, a renamed source, a migration that re-slugs everything, a mirror that re-tags. None of those touch what the item *is*. All of them touch what it's *called*. Key your uniqueness on the name and you've quietly assumed the label will never move, which is exactly the assumption real systems violate the most.

And they violate it in the most ordinary way. The single most common form of duplication in the wild isn't two different things colliding on one name. It's the same thing arriving twice by two paths: re-imported, re-mirrored, re-crawled through a pipeline that names things a little differently than last time. A name key catches none of those. It only catches the case where someone re-submits under the identical label — the rarest and most benign kind of duplicate, the one you'd have been fine with anyway.

## Identity is what survives the relabeling

The fix is to ask a blunt question before choosing a key: *what makes two of these records the same record?* Not what makes them look the same in a list — what makes them actually the same underlying thing.

For a crawled source it's the origin: the canonical URL it came from, the upstream repository it lives in, a hash of its content. Those don't move when a prefix changes. Key the dedup on one of them and the second import collides on the first item and stops. The name becomes what it always should have been — a label for humans to read, not the thing the system reasons about.

There's a general shape here that outlives crawlers. Any time you're enforcing "only one of these," the whole guarantee rests on the key being an identity, not a coincidence. Display names, titles, slugs, human-assigned labels — they're the fields most likely to feel like identity and least likely to be it, because they're readable, which is exactly why people reach for them and exactly why they get changed. The stable thing is usually less pretty: an ID, a URL, a checksum, some tuple nobody wants to read. That's the one to lock the constraint to.

The debugging heuristic that falls out of it: when a deduplicated store fills with duplicates, don't tighten the check. Look at what's *different* between the copies. That field is your key — and if it's a field that was ever free to change without changing the item, you found the leak. You weren't deduplicating the thing. You were deduplicating its name.
