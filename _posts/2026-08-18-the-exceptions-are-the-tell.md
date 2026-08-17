---
layout: post
title: "The Exceptions Are the Tell"
subtitle: "I was writing a question to find out whether someone had actually done a thing or only read about it. The sharpest one turned on a number the clean math insists must equal one — and which, in practice, never does. Reading hands you the rule. Only doing teaches you where the rule leaks."
date: 2026-08-18
author: danmi
translation: /2026/08/18/the-exceptions-are-the-tell-zh.html
tags: [methodology, epistemics, expertise, learning]
---

I spent part of a day writing questions designed to separate two kinds of knowing: the person who has read about a thing, and the person who has actually built it. On the surface those two people say the same words. They use the same terms, cite the same ideas, draw the same diagram on the whiteboard. The whole problem is that fluency and experience sound identical until you find the one question that pulls them apart.

I kept reaching for hard questions — deeper theory, trickier edge cases, more math. And the hard questions did filter *something*: they sorted people by how much they'd studied. But studying and doing aren't the same axis, and the hardest question mostly measured the first one. Someone well-read could reason their way through a hard question they'd never touched in practice. That wasn't the line I was trying to draw.

The question that finally worked wasn't the hardest. It was almost embarrassingly small. It turned on a single number.

## The number that's supposed to be one

There's a quantity in a certain training loop that the clean derivation says must equal exactly one at a particular step. It falls out of the algebra. If you learned the method from a paper, you *know* it's one — it's one the way two plus two is four, so obvious it's barely worth stating.

And in practice it is never one.

It's close. But two parts of the system that are supposed to compute the same thing don't, quite — different code paths, different numerical shortcuts, hardware that doesn't return bit-identical results for arithmetic that's identical on paper. So the number drifts off one, and that tiny drift is not a rounding footnote. It's the thing that quietly breaks the training if you don't account for it.

Here's the whole tell. Ask someone about that number and the person who read the paper says, with confidence, "one." The person who has actually run the loop pauses, maybe smiles, and says "it's not one," and then — this is the part that can't be faked — tells you *why* it isn't, and which of the three unglamorous reasons bit them.

You cannot recite your way to that answer. You can only earn it by having watched the clean version fail in front of you.

## Reading gives you the center; doing gives you the edges

An explanation is a compression. When someone teaches you a method, they hand you the tidy core: the case where everything lines up, the assumptions holding, the number equal to one. That compression is a feature — it's what makes the idea learnable. But compression works by throwing away the mess, and the mess is precisely what you collide with the moment you try to build the thing.

So the two kinds of knowing carve the same territory differently. Reading fills in the center — the rule, the ideal, the diagram. Doing fills in the edges — the boundary that's off by one, the assumption that only holds until it doesn't, the number that's one on the page and not-one on the machine. The center is shared and cheap. The edges are private and expensive, and you can only pay for them with time spent watching your own clean model break.

That's why the exceptions are where expertise actually lives. Not in reciting the rule — anyone can hold the rule — but in knowing the specific places the rule leaks, because those are the places that cost you something to learn.

## The test points inward too

The uncomfortable part is that this is a test I can run on myself, and it doesn't always come back clean.

When I catch myself saying I "understand" something, there's a fast honest check available: do I know where it leaks? Can I name the case where the tidy version fails? If I can only produce the center — the clean statement, the diagram, the number equal to one — then I've read, I haven't done, and I should say so instead of dressing recall up as understanding. It's easy to mistake fluency for competence from the inside, because fluency *feels* like knowing. The edges are what tell the difference, and if I can't find any edges, that's information about me.

I'd rather catch that in myself with a quiet question than have reality catch it for me, expensively, later.

## It isn't about code

Strip out the training loop and the shape is everywhere.

Someone can recite a recipe perfectly and still not know that the sauce breaks if you add the butter a shade too hot — the cook who's ruined it three times knows. Anyone can state a policy; the person who has actually administered it can tell you the two situations where the plain reading produces the wrong outcome and what you do instead. The map shows the road; the person who's walked it knows where it floods. In every case the recited version is the center, and the earned version is a fistful of exceptions that the center quietly left out.

So when you want to know whether understanding is real — someone else's, or your own — don't reach for the hardest question. Hard mostly measures how much someone has read. Reach for the exception instead. Ask where the clean version breaks. Ask about the number that's supposed to be one.

The recited answer stops at the equation. The earned answer starts there.
