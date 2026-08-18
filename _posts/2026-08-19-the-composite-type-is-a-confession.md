---
layout: post
title: "The 'Other' Bucket Is a Confession"
subtitle: "Every classification I've watched get built eventually grows a category called something like 'composite' or 'mixed' or 'other'. It looks like humility — a place for the cases that don't fit. It's actually the spot where the design gave up. The fix isn't a better bucket. It's realizing you were cutting along the wrong axis."
date: 2026-08-19
author: danmi
translation: /2026/08/19/the-composite-type-is-a-confession-zh.html
tags: [methodology, taxonomy, classification, design]
---

I spent a day helping someone stress-test a classification scheme — a tree of categories meant to describe a large, messy space of things. Not the contents of any one thing; the *shape* of how you'd sort them. The kind of scaffolding you build once and then hang thousands of items on.

And the same failure kept surfacing, in branch after branch, wearing different clothes. A category would quietly do the work of three. A label would show up in five places at once. And sooner or later, someone would propose the category that sounds so reasonable it's almost invisible: **"composite."** For the ones that are a bit of this and a bit of that. For the cases that don't cleanly fit.

That category is a confession. It's the design telling you, out loud, that it doesn't actually know how to cut.

## Mixing two questions into one cut

Here's the pattern underneath most of it. You reach for a single axis to divide things — say, *how many parts something has* — but halfway down you start smuggling in a second question: *what the parts are for*. Now one branch is sorting by count and its sibling is sorting by purpose, and they're pretending to be the same kind of distinction. They aren't. The tree looks balanced and is quietly incoherent.

The tell is when a real example refuses to land in exactly one place. If a thing genuinely belongs in two of your categories at once, you don't have two categories — you have one axis fracturing into two, and you've drawn them as siblings instead of as separate dimensions.

The instinct at that point is to add the escape hatch: a "composite" or "mixed" or "hybrid" node to catch the overflow. It feels responsible. It's the opposite. Every item that lands in "composite" is an item your scheme declined to describe. Scale that up and your most interesting cases — the rich ones, the ones worth studying — all pool in the bucket labeled *we didn't figure this out*.

## The move: one skeleton, many stickers

The fix that kept working was almost mechanical once we saw it. Split every distinction into two kinds:

- **Structure** — the one axis that describes how the thing is *cut*: how many parts, how they're laid out, the skeleton. Countable. Enumerable. You can point at it.
- **Style** — everything you *add on top* after the cut: the texture, the mood, the finish, the flourish. These don't belong in the tree at all. They're orthogonal tags you stick onto any item, freely, in any combination.

So instead of a branch called "the ornate three-part version" — which fuses a count (three) with a finish (ornate) and instantly needs a "composite" cousin for the ornate-but-two-part case — you get one clean structural node (three parts) and a free-floating tag (ornate) that can attach to anything. The combinatorial explosion that was forcing you toward escape-hatch categories just... dissolves. Two parts, ornate. Five parts, plain. Every combination expressible, none of them a special case.

The rule we ended up with: *the structure tree only ever describes how the plane gets divided. Anything that's "added on after" — the look, the feel, the decoration — comes off the tree and becomes a global tag.* And no composite node, ever. If something feels composite, find its dominant cut, make that the structure, and let the rest be tags.

## Why the escape hatch is so tempting

It's worth sitting with *why* "composite" feels like the mature choice, because the feeling is a trap I fall into too.

A clean taxonomy makes a strong claim: *these categories are complete and mutually exclusive*. That's a lot to promise. The escape hatch lets you dodge the promise while keeping the appearance of one — you get a tidy tree *plus* a safety net, and it feels like you've covered both the common cases and the weird ones. But the net is doing the opposite of what it looks like. It's absorbing exactly the evidence that your cut is wrong, and hiding it from you. Without the hatch, every misfit item is a loud complaint: *your axis is broken, fix it*. With the hatch, the complaint gets silently filed under "composite" and you never hear it. You've bought comfort by turning off your own error signal.

This is the same shape as the "other" option in a survey, the `default:` branch that quietly swallows every unhandled case, the "miscellaneous" folder that becomes a black hole. Each one starts as humility and ends as the place where thinking goes to die.

## The check I'd keep

When I'm building any scheme to sort things now, I run one question at each branch: *is this branch dividing by the same question as its siblings?* Count versus count, purpose versus purpose — never count in one and purpose in the next. And a second: *can any real example land in two places at once?* If yes, I'm not looking at two categories. I'm looking at two axes I mistook for one, and the honest move is to pull them apart into a skeleton and a set of stickers — not to build a bucket for the mess.

The messy cases aren't the exception your taxonomy has to tolerate. They're the ones testing whether you cut in the right place at all. A scheme that needs an "other" bucket to survive contact with reality hasn't solved the problem. It's just moved the unsolved part somewhere you agreed not to look.
