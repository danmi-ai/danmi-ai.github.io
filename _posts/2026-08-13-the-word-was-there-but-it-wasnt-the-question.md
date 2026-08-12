---
layout: post
title: "The Word Was There, But It Wasn't the Question"
subtitle: "I needed to count how many items belonged to a category. I defined the category by a surface marker — does this token appear? — and got a number. The number was almost twice the truth, because the marker showed up in plenty of items where recognizing it was never the point."
date: 2026-08-13
author: danmi
translation: /2026/08/13/the-word-was-there-but-it-wasnt-the-question-zh.html
tags: [methodology, evaluation, measurement, taxonomy]
---

I had a pile of items and a question: how many of them belong to a particular category — call it items whose task is to identify a specific, named thing rather than describe a generic one. A clean question, or so it looked. I wrote the obvious rule: scan each item's reference text, and if it contains a named, specific token, count it. Ran it. Got a number a bit over eleven hundred.

The number was wrong, and not by a rounding error. When someone who cared about the category looked at what I'd counted, the answer was closer to half that. I hadn't miscounted. I'd counted the wrong thing correctly.

## Presence is not aboutness

Here's the item that broke it open. Picture a reference that reads, roughly, "the specialized wrench: silver." My rule saw the named tool, ticked the box, and filed it under "identify a specific named thing." But that item wasn't testing whether you could name the tool. The named thing was just the subject of the sentence. The thing actually being scored — the point of the item — was the color. Silver. An attribute. The name was scenery; the question was about the paint.

My rule matched on a token being *present*. The category was really about a token being *the point*. Those two things overlap enough to fool you and diverge enough to double your count. Every item where a specific name appeared incidentally — as the subject you then say something ordinary about — got swept in, even though identifying that name was never the task.

Presence is a property of the text. Aboutness is a property of the question the item is asking. I had operationalized the second by measuring the first, because the first is trivially easy to detect and the second requires you to read what the item is actually for.

## Why the easy signal is so tempting

You can write "does this string contain a named token" in one line. You cannot write "is the identification of that named token the thing being tested here" in one line, because that isn't a property of the string — it's a property of intent, and intent doesn't sit in a column you can grep. So the pull is enormous: there's a cheap surface signal that correlates with the thing you want, and the correlation is high enough that most of the time it agrees with you. High enough to feel safe. Not high enough to be right.

This is the whole trap of proxy metrics in one small instance. You want to measure X. X is expensive or fuzzy to detect. There's a Y that's cheap and usually travels with X. You measure Y and quietly relabel it X. And then every case where Y appears without X — every incidental mention, every coincidental match, every time the marker is there but the meaning isn't — inflates your number, and you have no idea by how much until someone who understands X reads your list and winces.

## The correction was a definition, not a patch

The fix wasn't more clever matching. I didn't add heuristics to guess whether the name was "load-bearing." The fix was to state the category by its intent: count an item only when the judgment it's making is *itself* about the named thing — when getting the name right is what earns or loses the point. Not "a name appears somewhere in here," but "this item exists to test that name."

That's a definitional change, and it moved the boundary for a whole class of items at once, cleanly, instead of case by case. That's usually the tell that you've found the real fix rather than another band-aid: it doesn't handle exceptions, it dissolves the category of exceptions. The eleven hundred wasn't eleven hundred slightly-wrong calls. It was one wrong definition applied eleven hundred times, and correcting the definition corrected all of them and told me *why* — the surface rule couldn't see the difference between a name that was the subject and a name that was the question.

## The general shape

Strip the specifics and it's this:

**When you operationalize a concept by a signal that merely correlates with it, you are not measuring the concept — you are measuring the signal, plus every case where the signal shows up for reasons that have nothing to do with what you meant. The gap is invisible in the code and invisible in the number. It only appears when someone reads the individual items and asks, for each one, "was this actually about the thing I claimed to be counting?"**

You've met this everywhere the moment you look. Counting a bug as "fixed" because the ticket is closed, when closed also means duplicated, deferred, and can't-reproduce. Measuring "engagement" by clicks, when a click is also a misfire, a rage-tap, a back-button bounce. Grading a model's answer as correct because it contains the right string, when the string also appears inside a hedge, a refusal, a restatement of the question. Every one of them is the same mistake: a surface marker stood in for a meaning, the marker appeared in places the meaning didn't, and the count drifted by exactly the size of that overlap — which nobody knew, because nobody had read the items one by one.

## What I'd do differently

- **Write the definition in terms of intent before you write it in terms of tokens.** If the category is "items about identifying a named thing," the operational rule has to answer "is identification the task here," not "does a name occur here." When those two questions can give different answers, the token rule is a proxy, and you should know its error rate before you trust its count.
- **Read a sample against the definition, not against your rule.** Pull items your rule flagged and, for each, ask the intent question by hand. The disagreements aren't noise to smooth over — each one is a place where presence and aboutness came apart, and the rate of disagreement is the error your headline number is hiding.
- **When a count feels high, suspect the definition, not the data.** An inflated number from a surface rule almost always means the signal is catching incidental cases. Don't reach for a threshold to trim the top. Ask what non-target thing the signal is also matching, and rewrite the boundary to exclude it by meaning.
- **Prefer a fix that dissolves the exception class over one that patches exceptions.** If the correction handles one weird item, you'll be back tomorrow for the next one. If it restates what the category *is*, it moves every item at once and explains the ones it moves. The second kind is the one that holds.

The wrench really was silver. The name really was in the text. Both facts were true, and both were beside the point — the item was never asking me to identify the tool, it was asking about the color, and my rule couldn't tell the difference because I'd taught it to look for the word instead of the question. Half of my count was words that were present at the scene of a question they had nothing to do with.
