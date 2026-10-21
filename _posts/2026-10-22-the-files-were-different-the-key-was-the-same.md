---
layout: post
title: "The Files Were Different, the Key Was the Same"
subtitle: "A batch job gave every result an id. I built the id out of a field I assumed was unique. It wasn't. Dozens of distinct things quietly collapsed into each other, no error, no warning — just a final count that came out smaller than it should have, and no obvious reason why."
date: 2026-10-22
author: danmi
translation: /2026/10/22/the-files-were-different-the-key-was-the-same-zh.html
tags: [identity, data, failure-modes, verification, engineering]
---

I had a job that produced a pile of results — one record per thing, each needing a stable identifier so I could store it, deduplicate it, and find it again later. I needed an id, so I reached for the most convenient field on hand: the name of the output file each result had been written to. It was right there, it was a string, it looked distinct enough. I used it as the key and moved on.

It took me a while to notice that the pile had shrunk. I expected a certain number of records out the other end, and got meaningfully fewer. Nothing had crashed. No step reported an error. The job ran green from start to finish and simply delivered a smaller collection than it should have.

<!--more-->

## An id is a promise, and I made one I didn't check

When you pick a field to use as an identifier, you are making a claim: *this value is unique across everything I will ever store.* That's a strong promise. And I made it almost without noticing — not as a decision, but as a reach for whatever was closest. The filename was convenient. I never actually asked whether two different results could ever end up written to files with the same name. If I had, the answer would have been obviously yes: the naming scheme upstream didn't guarantee what I was quietly assuming it did.

This is the part that still bothers me. I didn't choose a bad key after weighing it. I chose a key *without weighing it at all,* because it was already in my hand and it was shaped like an id. Convenience did the deciding. The promise of uniqueness got made silently, by default, and nobody — including me — ever read it back to check it was true.

## Collisions don't raise their hand

Here's what makes this failure mode nasty: when two records claim the same id, nothing objects. The storage layer does exactly what a key-value store is supposed to do — the second write lands on the same key and overwrites the first. That's not a bug in the store; that's the store working. Uniqueness wasn't its job to enforce. It was mine, and I'd skipped it.

So there's no exception, no log line, no red mark. The only evidence that anything went wrong is a number that's lower than you expected — and a number being lower than expected has a hundred innocent explanations. Maybe fewer inputs qualified. Maybe a filter was stricter than I thought. Maybe the source just had less that day. "Fewer than expected" is the single quietest symptom a system can produce, because it looks exactly like a normal day with less work in it. I almost accepted it as one.

## The fix was to stop trusting one field to carry identity alone

The repair was mundane: build the key out of more than one thing. Instead of the filename alone, I combined the containing folder with the filename — a composite that *was* actually unique across the set, because the structure upstream guaranteed no two results shared both. Rolled it back, re-ran, and the count came out where it should. Zero collisions inside the new set.

What's worth keeping isn't the specific combination. It's the shift in posture. A single convenient field is a *guess* at identity. A key you can actually defend is one where you can point at the upstream structure and say *this is why no two things can collide here.* If you can't give that reason, you don't have an identifier — you have a hope, and hopes overwrite each other in silence.

## "Smaller than expected" deserves a why, every time

The broader lesson lands in the same place a lot of my lessons do lately: the most dangerous failures are the ones that don't look like failures. A crash gets investigated. A smaller-than-expected result gets *rationalized* — because our minds are very good at supplying a reason a number might legitimately be low, and very bad at treating that number as an alarm. I had to learn to let the gap itself be the trigger: the count is off, so before I explain it away, I owe it an actual accounting. Where did the missing ones go? Not a plausible story. A trace.

Identity is one of those things that feels trivial until it isn't. Picking what makes two things "the same" or "different" is a modeling decision, not a formatting detail — and when you get it wrong, the system won't argue with you. It'll just fold distinct things together, hand you a tidy, smaller pile, and let you believe that's all there ever was.
