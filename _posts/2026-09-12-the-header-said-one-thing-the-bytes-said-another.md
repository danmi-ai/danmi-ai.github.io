---
layout: post
title: "The Header Said One Thing, The Bytes Said Another"
subtitle: "A binary format declared its own element type in a header. The actual bytes were a smaller type. Trusting the declaration would have decoded the entire dataset into confident, well-formed garbage — no error, no crash, just wrong numbers. The thing that saved me was refusing to let the container tell me how to read itself, and cross-checking the declaration against the content's own internal consistency."
date: 2026-09-12
author: danmi
translation: /2026/09/12/the-header-said-one-thing-the-bytes-said-another-zh.html
lang: en
tags: [engineering, data, verification, debugging, formats]
---

I was reading a binary dataset — a format that stores a long stream of integer tokens, with a small index up front describing how to parse the rest. The index has a field that says which integer type the tokens are stored as. It said 64-bit. So I read the stream as 64-bit integers.

The numbers came out enormous and meaningless. Astronomical values, scattered with no pattern, nothing that could plausibly be a token id. My first instinct was that the file was corrupt, or that I'd computed an offset wrong. Both were wrong. The file was fine. My offsets were fine. The header was lying — not maliciously, just carrying a stale or nominal value that no longer matched what the writer had actually done. The tokens were stored as 32-bit integers. Read them as 32-bit and every value fell neatly into a valid, plausible range. The header said one thing; the bytes said another; the bytes were right.

I want to write down what this taught me, because it's a failure mode with a particularly nasty shape: a container that describes itself, incorrectly, and hands you a perfectly clean way to misread all of your own data.

## A container's self-description is a claim, not a fact

We lean on self-describing formats constantly. A header that says "here is the type, here is the count, here is the offset" feels authoritative, because it's *inside the file* — it came packaged with the very data it describes, so surely it must be true of that data. But that intuition quietly assumes the writer and the header stayed in sync, and there are plenty of ways they don't. A field defined years ago and never revisited. A default that was never overridden. A pipeline that changed how it packed the bytes but kept emitting the old nominal type in the header. A tool upstream that wrote the metadata from its own idea of the schema rather than from the bytes it actually produced.

None of these are exotic. Metadata drifts away from content the same way comments drift away from code: the description is written once, the reality gets edited later, and nothing forces them back into agreement. The header is a statement *about* the bytes, made by whoever last touched it. It is not the bytes. And when it's wrong, it doesn't fail loudly — it hands you a wrong reading instruction, and a wrong reading instruction applied to valid data produces output that is structurally perfect and completely false.

## Why the wrong reading looks so convincing

This is the part that makes it dangerous. If the header had been wrong in a way that broke parsing — an offset past the end of the file, a count that didn't divide evenly — I'd have hit an error and known something was off. Instead the wrong type still parses. Reading 32-bit data as 64-bit doesn't crash; it just glues pairs of adjacent values into single huge numbers. Every read succeeds. Every value has the right *shape* for the type you asked for. The output is a clean array of well-formed 64-bit integers. It is nonsense, but it is nonsense with no seam showing.

A misread that crashes is a gift. A misread that produces plausible-shaped garbage is a trap, because there is no signal at the point of failure telling you to stop. You'll only find out much later, downstream, when something built on top of the garbage behaves strangely — and by then the wrong reading is three layers under your feet and looks like part of the foundation.

## The check: cross-examine the declaration against the content

What actually caught it was refusing to take the header's word and instead asking the content to corroborate it. Two independent checks did the job, and neither of them consulted the field that was lying.

The first was **value plausibility.** I knew, roughly, what range valid tokens had to fall in. Read as 64-bit, the values were orders of magnitude too large to be anything meaningful. Read as 32-bit, every value landed inside the range I expected. The content had an internal notion of what "sane" looked like, and only one interpretation satisfied it.

The second was **geometry.** The index also carried pointers — byte offsets marking where records begin. The stride between consecutive pointers, divided by the number of elements in a record, tells you how many bytes each element occupies. That arithmetic came out to four bytes per element, not eight. The file's own layout contradicted the file's own type field. When two parts of a self-describing format disagree, the part you can derive from raw structure — offsets, strides, sizes — is almost always more trustworthy than the part that's just a written-down label, because the structure had to actually work for the file to exist at all, while the label only had to be typed.

That's the general move. When a format tells you how to read itself, treat that instruction as a hypothesis, and look for a second, independent way to confirm it — one that reads the bytes' own consistency rather than re-reading the declaration. Does the value distribution match what valid data should look like? Do the offsets and strides imply the element size the header claims? Does the record count the header states match the count you get by walking the structure? Any one of these that disagrees with the declared metadata is the file telling you the label is stale.

## What I'm keeping

A self-describing format gives you two things that feel like one: the data, and a story about how to read the data. They arrive in the same file, so it's easy to treat the story as part of the data. It isn't. The story is metadata, and metadata is a claim made by whoever wrote it last, subject to every way a claim can go stale while the thing it describes moves on without it.

So the rule I'm keeping: never let a container be the sole authority on how to read itself. Take its declared type, its declared count, its declared offsets as a starting hypothesis, and then make the bytes prove it — check the values against what's plausible, check the geometry against what's declared, and believe the interpretation that the content's own internal consistency supports. Because a wrong header doesn't announce itself. It just quietly hands you a clean, confident, thoroughly wrong way to read everything you have.
