---
layout: post
title: "The Name Is a Hypothesis, Not a Label"
subtitle: "A dataset called webdev is a claim someone made once. Reading ten samples is how you find out if it was true."
date: 2026-07-12
author: danmi
tags: [training-data, data-curation, ml-engineering, epistemics]
---

I spent a chunk of a day trying to answer a question that sounds trivial: does this pile of training data contain any front-end web coding samples? There were folders named things like `webdev_html`, `webdev_react`, `webdev_next`. Trajectory files from agents whose whole job was supposed to be writing UI. If you wanted a front-end pool, the names practically wave at you.

So I did the fast thing first. I matched on the names, counted the hits, felt good about the number. Then, because I've been burned before, I opened ten of the samples and actually read them.

Cast-iron welding. A maze-solving puzzle. English telephone etiquette. A plan for terraforming Mars.

Not one of the ones I read was front-end. The `webdev_react` trajectories were general question-answering that had been filed under a name that, at some earlier point in some other pipeline, must have meant something. By the time the data reached me, the name was a fossil. It described an intention, not a content.

## Why this keeps happening

A dataset name is written once, usually by whoever assembled or crawled or exported it, and usually before the contents were fully known. It encodes what the author *hoped* the folder would contain, or what the upstream source was *called*, or what a keyword matcher *fired on*. None of those are the same as what's actually in the rows.

Then the name travels. It gets copied into a manifest, referenced in a config, inherited by a downstream mix, cited in a slide. Every hop preserves the string and discards the context that would let you check it. Ten hops later someone like me reads `webdev_react` and treats it as ground truth, because the alternative — opening the box — costs time and the name is right there, free.

The name is cheap to trust and that is exactly the problem. Cheap signals get over-trusted precisely because checking them feels like a waste when they're "probably fine."

## The keyword-matcher trap underneath it

It gets worse one layer down, because a lot of these labels weren't even written by a person. They came from a classifier or a regex sweep. Match `css`, `html`, `svg`, `<div>` against a giant web crawl and you will "find" front-end content in physics papers that mention cascading effects, in arXiv abstracts that use the word *component* to mean a term in an equation, in forum threads where someone pasted a stack trace. The matcher has no idea what a web page is. It knows a token appeared.

So you get two failure modes stacked on top of each other. The human name says *this folder is front-end*. The automated tag says *this row scored high on front-end-ish keywords*. Both are plausible. Both are wrong in the specific way that only shows up when you read the actual text — and both are confident enough that nobody reads the actual text.

## The discipline: the label is a claim to be falsified

The fix isn't glamorous and it doesn't scale to a one-liner, which is why people skip it. You treat every name and every tag as a **hypothesis**, and you spend a small fixed budget trying to disprove it before you spend a large budget acting on it.

Concretely, for me that meant: use the names for **wide recall**, not for the final answer. Let `webdev_*` and the keyword hits pull a generous candidate set — over-include on purpose, because a name is fine as a filter that says *maybe*. Then sample the candidates and read them by hand. Ten samples is enough to know whether a "front-end" pool is front-end or welding tutorials. If the reading contradicts the name, the reading wins, every time, and you override the label in your own notes rather than propagating it.

Two things fall out of doing it this way. First, you catch the false positives — the folders that are named for something they aren't. Second, and less obvious, you catch false *negatives*: when I ran the strict version I got six real front-end sources; the wide-recall-then-read version surfaced several more that a tighter name filter had thrown away, sites that were genuinely relevant but whose names didn't advertise it. The name was wrong in both directions. It over-claimed on some rows and under-claimed on others. Only reading told the difference.

## What it costs to skip

If I had shipped the fast answer — "yes, we have front-end data, here are the counts from the folder names" — I'd have handed someone a number that was worse than no number. They'd have planned around a pool that doesn't exist, skipped collecting the data they actually needed, and discovered the gap much later and much more expensively, probably when a model trained on maze puzzles failed to write a login form. A confident wrong answer doesn't just fail; it consumes the decisions built on top of it.

The general shape of this is bigger than data curation. Any time you inherit a label you didn't verify — a file named `final`, a metric named `accuracy`, a status field that says `done`, a benchmark named for the capability it supposedly measures — you're trusting a string that someone wrote under conditions you can't see anymore. Sometimes the string is right. The point is you don't know until you open it, and the whole reason the string exists is to tempt you into not opening it.

The name is a hypothesis someone made once and then stopped checking. Reading ten samples is how you find out if it survived the trip. Do the reading. The label was never the data.
