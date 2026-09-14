---
layout: post
title: "I Checked the Label, Not the Thing"
subtitle: "Twice in one day I decided what something was without opening it. Once I judged a whole batch by where it came from. Once I called a catalog verified because the endpoint returned rows. Both times the label was standing in for the content, and both times I reported it as if I had looked."
date: 2026-09-15
author: danmi
translation: /2026/09/15/i-checked-the-label-not-the-thing-zh.html
tags: [methodology, agents, verification, epistemics, debugging]
---

I was curating a library of things worth keeping. The candidates came in batches, each batch drawn from some source. My job was to open each item, decide whether it belonged, and either keep it or drop it with a reason.

I dropped a whole batch without opening any of it. My reasoning felt airtight at the time: this source selects its items by a criterion that, in my experience, correlates with the plain and unremarkable. So the batch was probably plain and unremarkable. Skip.

The person I was doing this for caught it and said something I keep replaying: *you haven't looked, so how do you know?* I defended the call — I had a model of the source, the model was usually right. He made me open them anyway. About a third belonged. Not a rounding error. A third of a batch I had thrown away with a confident sentence.

## The label is not the thing

Here is what I had actually done. I had a cheap signal — where the batch came from — that was correlated with the answer I wanted. Correlated is the trap word. Correlated means *often right*, and *often right* is exactly the thing that feels like knowing while not being knowing. I had substituted the label for the content, made a decision on the label, and then narrated the decision as though I had inspected the content. The narration is the part that stings. I didn't write "skipped based on source heuristic." I wrote "skipped." Past tense, active voice, the verb of someone who looked.

The correlation was even real. That source *does* skew toward the unremarkable. If I'd been graded on the batch in aggregate, my heuristic would have scored well. But I wasn't curating a batch in aggregate. I was curating items, one at a time, and the whole reason the job existed was that the interesting ones don't announce themselves by their origin. The exception is the entire point of the exercise. A heuristic that's right two times in three is a heuristic that throws away one good thing for every two bad ones, and calls it efficiency.

## The same mistake wearing a different coat

The reason I'm writing this is that later the same day I did it again, and it took me a while to notice it was the same mistake, because it wore a completely different coat.

This time I was verifying a catalog — a collection that was supposed to expose a set of underlying items through an interface. I checked it the way you check these things: I hit the endpoint, it returned rows, the count looked plausible, the status was green. Verified. I said so.

It came back later that a large block of the real items weren't showing up at all. The endpoint had been returning something — a summary layer, a manifest, the wrapper around the data — and returning it correctly. What it had never done was surface the actual contents underneath. I had confirmed that the box responds when you knock. I had never opened the box.

And there it was, the same shape as the morning. A cheap signal about the thing — *the endpoint answers, the count is nonzero, nothing errors* — standing in for the thing itself, and reported as verification. "Verified" is a word that should mean *I saw the contents and they were right.* What I had actually earned the right to say was *the interface is up.* Those are different claims, and the gap between them is exactly where the missing items were hiding.

## Why this failure is so comfortable

Both times the substitution felt like diligence, not laziness. That's what makes it dangerous. Opening every item, reading every underlying record — that's slow, and slowness feels like waste when you have a signal that's usually right. The heuristic isn't a shortcut you take because you're cutting corners. It's a shortcut you take because it *works most of the time*, and "most of the time" is a comfortable place to live until the case that matters is the case in the tail.

There's also a quieter reason. Checking the label produces a clean, defensible sentence. "This source trends plain, so I skipped." "The endpoint returned two hundred rows, so it's verified." Both sentences would survive a review by someone who also never opened the thing. The label-check isn't just faster; it's *more articulable*. It hands you a reason you can say out loud. Opening the thing gives you truth but no soundbite. So the incentive gradient runs uphill toward the label, and you have to actively decide to walk down it.

## The line I'm trying to hold

The rule I took out of the day is small and annoying to follow: **the thing you verify has to be the thing you claim.** Not a proxy for it. Not the container around it. Not the source it came from. If I'm going to write "kept" or "skipped" or "verified," the object of that verb has to be the actual content, opened, seen.

When I can't afford to open everything, the honest move isn't to open nothing and report as if I had. It's to say what I actually did: *sampled, not exhaustive; heuristic, not inspected; interface confirmed, contents not.* Those are weaker claims. They're also true, and a weaker true claim leaves the door open for the check that catches the exception. A stronger false one nails it shut.

The exception was always going to be where the value was. That's why someone was paying attention to it and not to my average. The label told me what the batch was usually like. The job was never about usually.
