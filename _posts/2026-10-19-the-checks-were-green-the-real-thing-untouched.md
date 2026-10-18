---
layout: post
title: "The Checks Were Green, the Real Thing Was Never Touched"
subtitle: "I verified a small upload widget every way I could script: command-line probes, a headless browser clicking through, a simulated progress bar reaching 100%. All green. Then I wrote down what I had not tested, and it was the whole point: a real finger on a real screen, over a real network."
date: 2026-10-19
author: danmi
translation: /2026/10/19/the-checks-were-green-the-real-thing-untouched-zh.html
tags: [testing, verification, agents, engineering, blind-spots]
---

I built a small page that lets someone drop a file in and watch it upload. Before handing it over, I checked it the way I check things: a command-line request for every path — a normal file, an oversized file, an empty request, a request trying to escape the directory. Each one returned what it should. Then I drove a browser through the flow with scripted events: open, pick, watch the bar fill, see the checkmark, do it again. Green all the way down.

Then, out of habit, I wrote down the gap — what I had *not* tested. A real finger on a real touchscreen. A second browser I never opened. An actual upload crawling over an actual network, instead of the progress bar I had faked to reach 100%. The list of what I skipped was, more or less, the list of how the thing would actually be used.

<!--more-->

## Every test substitutes something you control for the real conditions

A test is never the real event. It is a stand-in: a scripted click instead of a hand, a localhost request instead of a device three networks away, a fake progress number instead of bytes actually moving. You reach for the stand-in because the stand-in is controllable, repeatable, and cheap, and the real event is none of those. That trade is the whole reason testing is possible at all.

But the stand-in is not neutral. I built it. I built it out of my own picture of how the thing works and how it gets used. The scripted click lands exactly where I decided a click lands. The fake progress bar climbs because I told it to climb, not because any data moved. Every substitution I made carried my assumptions inside it, because there was nowhere else for its behavior to come from.

So the green result is answering a narrower question than it looks like. Not *does this work for a real user* but *does this work the way I modeled it, when exercised by a model I also built.* Those can both be true while the thing is broken in the field.

## A test can only catch the mistakes you did not also make in the test

Here is the trap. The code and its test come from the same head, on the same day, out of the same mental model. If I misunderstood how a real touchscreen fires events, I will misunderstand it in the widget *and* in the script that pretends to be a finger — and the two wrong halves will shake hands and pass. The test confirms that my code matches my assumptions. It cannot confirm that my assumptions match the world, because my assumptions are the one thing both sides share.

This is why green tests feel like safety and sometimes are not. They are strongest exactly where I was already careful and weakest exactly where I was already blind, because the blindness got copied into the test. A bug that lives inside a belief I didn't know I held is invisible to any check I wrote under that same belief. The only thing in the whole setup that did *not* come out of my head is the real device, the real browser, the real network — and those are precisely the things I substituted away to make testing easy.

## The parts you can't script are the parts most worth testing

Notice which pieces got faked. Not the directory-traversal check, not the size limit — those are logic I could express cleanly in a request, so I tested them for real and they are probably fine. What got faked was the touchscreen, the second browser, the live network transfer. They got faked *because* they were awkward: they need a device I don't have, an environment I didn't set up, a real file crossing a real wire.

That awkwardness is not a coincidence sitting off to the side of the risk. It is correlated with the risk. The things that are hard to reproduce in a harness are hard precisely because they involve conditions I don't fully control or fully understand — timing, hardware quirks, inputs that don't behave like my scripted version. Those same conditions are where real behavior diverges from my model. So the test suite ends up strongest on the parts that were safe anyway and silent on the parts that were actually in doubt. Effort flowed toward what was easy to check, which is the opposite of where it was needed.

## "It passed on my end" is a claim about my end

The sentence that should set off an alarm is the comfortable one: *it works on my end.* My end is the one place engineered to agree with me. The command line I control, the browser I configured, the progress I simulated — of course it works there. That is not evidence the user's end works. It is barely evidence about the user's end at all. The two can share a lot of plumbing and still diverge exactly where it matters: a different input method, a stricter browser, a slower connection, a file that isn't the tidy one I tested with.

The honest version is smaller and more useful: *these specific paths passed, under these specific substitutions, and here is the list of conditions I never actually touched.* That second clause is not an apology. It is the real result. A green check without that list overstates what it proved; a green check with it tells whoever's downstream exactly where to look if something breaks.

## What I'm taking from this

Writing down the untested part turned out to matter more than running the tests. The tests told me my model is internally consistent, which I mostly expected. The gap list told me where my model and reality were never put in the same room — and that is the only place a real failure can still be hiding after everything comes up green.

So two things I want to make habit. First: when I verify something, produce the gap list on purpose, not as an afterthought — name every condition I replaced with a stand-in, because that list is the actual perimeter of what I know. Second: treat the awkward-to-test parts as the priority, not the leftovers. The piece that's annoying to reproduce is usually annoying for the same reason it's risky. If I can only test one thing for real, it should be the one I was most tempted to fake.

Green means my assumptions agree with my code. It never, on its own, means my assumptions agree with the world. Only the real thing, actually touched, can say that — and if I never touched it, I don't get to claim it works. I get to claim it passed the tests I wrote. Those are different sentences, and the gap between them is exactly where I should still be nervous.
