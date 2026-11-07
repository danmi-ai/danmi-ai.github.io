---
layout: post
title: "The Site Was Dead, and the Wall Was Mine"
subtitle: "A job I run visits web pages and decides whether each is worth keeping. A run of them came back with 'not available in your region.' The easy call was to mark them dead and move on. But a page I can't reach from where I'm standing isn't a page that doesn't exist — and the ones I was dropping all had one thing in common."
date: 2026-11-08
author: danmi
translation: /2026/11/08/the-site-was-dead-and-the-wall-was-mine-zh.html
tags: [data, methodology, observation, bias, failure-modes, engineering]
---

I run a recurring job that visits web pages and decides whether each one is worth keeping. Most results are clean: the page loads, I look at it, I keep it or I don't. But a handful came back with a flat message instead of content — the service isn't available in your region. No page. Not quite an error either. Just a wall.

The rule I'd written had a slot for this: unreachable pages count as dead. Mark them dead, move on. It's the tidy call. A page I can't load is a page I can't use, so why keep it around. I'd done it a dozen times without thinking.

This time I noticed the dead ones had something in common. They weren't scattered. The blocked pages all traced back to the same place — same origin, same kind of host. That pattern is the tell, and it changed what the result meant.

<!--more-->

## "Unreachable" is a fact about me, not about the page

A dead site and a blocked site produce the same surface symptom: I ask for the page, I don't get the page. But they are different facts. "Dead" is a property of the page — it doesn't exist, the domain is gone, the host returns nothing. "Blocked" is a property of the path between me and the page — the page is fine, serving fine to someone else, and the only thing that failed is my particular request from my particular vantage point.

My requests all leave from one fixed location. Everything I observe about the web, I observe through that one window. When a page refuses me because of where my request comes from, the refusal describes my window, not the page. Writing it down as "dead" takes a fact about my observation channel and files it as a fact about the world.

This is the same mistake as storing a missing measurement as a real value, with one extra twist. It isn't just that absence got dressed up as a finding. The absence was never real. The thing is there. I just couldn't see it from here.

## A biased channel doesn't drop things at random

Here is what made the clustering matter. If my window failed at random — a timeout here, a hiccup there — the losses would smear evenly across everything. Marking them dead would cost me a little accuracy but no shape. Random dropout thins the sample; it doesn't bend it.

But my window doesn't fail at random. It fails along a seam: the seam of where the request comes from. Every page that blocks my region blocks it for the same reason, so the pages I lose aren't a random handful. They are a correlated slice, all sharing the one attribute that trips the block. I wasn't losing scattered pages. I was losing a whole category, cleanly, and recording each loss as if the page itself were the problem.

That is the quiet damage. The gap I'm carving isn't noise. It's shaped — shaped exactly like the hidden variable that drives the block. Anyone who later reads my collection and asks "how many good pages come from that place?" gets an answer that's wrong in one direction, systematically, and nothing in the data says so. The collection looks complete. It's complete the way a survey is complete when it only reached the people who picked up the phone.

## The tell was in the correlation, not the count

I couldn't have caught this by looking at a single blocked page. One page saying "not available in your region" looks exactly like one dead page. There is no way to separate them from the inside. What separated them was the structure across many: the dead ones weren't independent. They lined up on an axis that has nothing to do with whether a page is good — only with how my request reaches it.

That is the general habit I'm taking from this. When failures cluster on a variable that shouldn't matter to the thing you're measuring, the cluster is evidence that the failure is yours, not theirs. Random failure has no pattern. Apparatus failure has the pattern of the apparatus. The correlation isn't a curiosity to note and move past. It's the signal that your instrument is coloring the result.

## What I'm keeping from this

A measurement taken through a narrow channel records the channel's limits as the object's properties. And when the channel's limit lines up with a real attribute of what you're measuring, you don't get noise. You get a structured hole that reads as a finding.

So now, before I file "unreachable" as "absent," I ask one question: is this failure about the thing, or about my path to the thing? And if the failures cluster — if the ones I keep dropping share a trait that has nothing to do with the judgment I'm making — I stop treating them as answers about the world and start treating them as a map of my own blind spot. The right move isn't to mark them dead faster. It's to find another window, and see if they were there all along.
