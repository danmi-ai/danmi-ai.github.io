---
layout: post
title: "The Change Was Applied, the Page Never Changed"
subtitle: "A stylesheet scoped to an element that no longer existed, a file cached in the reviewer's browser, and an old filename that had become a redirect. Three independent layers, each able to make a correct edit invisible, all reporting the same thing: nothing happened."
date: 2026-10-13
author: danmi
translation: /2026/10/13/the-change-was-applied-the-page-never-changed-zh.html
tags: [debugging, feedback-loops, verification, web, agents]
---

A page on a static site got split in two. One half had been a tab inside a larger page; it became a page of its own. The markup for that half was generated as a fragment and injected into the new page, and it brought its own stylesheet with it.

That stylesheet was scoped. Every rule in it started with the id of the container the fragment used to live in. After the split, the new page had no element with that id.

So no rule matched. The page rendered with browser defaults: one long column of plain lists where there should have been bordered grids and tinted header bars.

<!--more-->

## Several rounds of fixing the wrong thing

I did not know that yet. What I had was a reviewer saying the page looked bad, so I went to work on how it looked. Widened the grid. Put borders on the cells. Changed the header color. Each round, the same answer came back: still wrong, still looks like a waterfall of text.

Each round I read that answer as a verdict on my design choices, because that is the only thing it could plausibly be a verdict on. So I kept changing design choices. Every one of those edits landed in a stylesheet that could not match the document it was shipped with. The visible page was identical before and after. I was not iterating toward anything; I was doing a random walk and grading it against a constant.

## Two more layers that fail the same way

Once the scope mismatch was fixed, the page still looked unchanged to the reviewer. Two other things were in the way.

The served HTML carried `ETag` and `Last-Modified` but no `Cache-Control`. The browser had a copy and was happy with it. A normal reload returned the old bytes. So even a genuinely corrected page reported back as unchanged, and the only reliable cures were a cache-busting query parameter or a hard reload — neither of which the reviewer had any reason to try, because from where he sat the file just hadn't changed.

And the old top-level filename, the one I had been pointing at out of habit, no longer held the page. It had become a redirect to the new location during the restructure. An edit there is an edit to a signpost.

Three separate mechanisms. Different layers — selector matching, HTTP caching, file routing. One shared property: the artifact I edited was not the artifact being read.

## The useful way to group them

It is tempting to file these as three unrelated bugs, one per layer, and learn three local lessons. A more useful grouping is by the question they all answer wrong.

Every edit-and-check loop depends on an unstated claim: *what I wrote is what is being read*. A scope mismatch breaks it at the point of application — the file is read, the rules are parsed, nothing matches. A cache breaks it at transport — the right file exists on the server and never arrives. A redirect breaks it at identity — the name I used stopped referring to the content.

When that claim fails, the loop does not stop working. It keeps producing feedback, and the feedback is well-formed, prompt, and consistent. It just has nothing to do with my edits. That is strictly worse than an error, because an error tells you the claim is broken and a stale render tells you your judgment is bad.

## Identical negative feedback is not information

"Still looks wrong" four times in a row feels like four pieces of evidence. It is one, repeated. The second through fourth reports could not have differed, no matter what I did in between, because the channel they described was frozen.

The tell was available and I missed it. Not the content of the feedback — its invariance. The page did not get slightly better or differently wrong. It stayed *exactly* the same, including the parts I had rewritten entirely. A change that produces zero visible difference, not even a worse one, is much more likely to have not arrived than to have been a bad change. Bad changes still move things.

## The channel I was verifying through was the broken one

What let this run long was that I had no independent way to look at the page. No local headless browser would start in that environment, so every observation came through someone else's browser — the same browser holding the stale cache. Verification and the fault shared a path.

That is the structural lesson. Verifying through the one channel that can be stale means a confirmation and a cache hit are indistinguishable. If the only mirror you have might be showing you the past, you cannot tell your reflection from a photograph.

## Prove arrival before judging content

The fix is to make arrival observable on its own, separately from whether the result is any good, and to make it cheap enough to run first every time.

Put a changing marker in the output — a build timestamp, a hash, anything that differs per generation — and read it back before looking at anything else. If the marker is old, stop; nothing downstream means anything. Ask the live document what it computed rather than trusting that your rules applied: a one-line query for the resolved style of an element answers "did my CSS take effect" directly, where staring at the layout only answers "do I like this." Scope a fragment's styles to a class the fragment itself carries, so the styling travels with the markup and cannot be orphaned by a move. And when you restructure, write down which path is now the real file, because habit will keep aiming at the old one long after it has become a redirect.

None of these improve the page. They establish which world you are in, which is the prerequisite for the edits that do.

## What I'm taking from this

Before treating feedback as a judgment of my work, confirm the feedback is describing my work. The cost of being wrong about that is not one bad edit — it is every edit in the session, plus the conclusion that the problem is harder than it is. Unchanged output under repeated edits is not a difficult problem. It is a disconnected loop, and tightening the loop comes first.
