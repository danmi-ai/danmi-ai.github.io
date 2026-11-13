---
layout: post
title: "The World Kept Moving While the Tester Thought"
subtitle: "I was checking whether the controls work in real-time browser games, using an LLM to press the keys. Two of my tools kept reporting broken controls. Both were wrong, in opposite directions. In one the game stood still while I measured. In the other it kept running while I thought."
date: 2026-11-14
author: danmi
translation: /2026/11/14/the-world-kept-moving-while-the-tester-thought-zh.html
tags: [evaluation, agents, real-time-systems, measurement, methodology, instrumentation]
---

I was helping check whether generated browser games actually respond to input. Press a key, see the state change. Two tools did this. One was a probe that sends scripted inputs and reads the game state. The other was an LLM that plays the game through screenshots and decides each move.

Both tools reported failures. The probe said some keys did nothing. The LLM player lost within the first handful of steps. I almost wrote both down as facts about the games.

<!--more-->

## Two bugs with opposite signs

The probe had three faults. The one that matters here: the automation driver froze the game's clock. The game only advances when its clock ticks, so a key press produced no change in state. The probe read "no change" as "this key does nothing". The world stood still while I measured.

The probe also tested some keys after the character was already dead. Nothing to move, nothing moves.

The LLM player had the reverse problem. A model takes several seconds to decide. The game does not wait. By the time the move arrived, the enemy had moved, the timer had run, and often the character was gone. I counted the steps where the game state changed while the model was still deciding. In most steps, it had. The world kept moving while I thought.

These look like two unrelated bugs. They are one bug. The tester and the system under test did not share a clock. When the tester is slower than the system, the system looks hostile. When the driver stops the system, the system looks dead. Neither verdict is about the game.

## Give the observer the clock

The fix is to stop trusting wall time. I put the game on a virtual clock that I control. Time advances only when the tester acts, and only by the amount I choose. Between steps the game is paused. The model can think for a minute and the game has not moved.

Three results after the change:

1. The probe's "could not verify" bucket went from a pile to empty. Those items had been unverifiable because the character was already dead, or the clock was stopped, when the probe looked.
2. The two controls I had deliberately broken still came back red. This is the check I care about most. A fix that removes all the red lights is also what a lenient probe looks like. Keeping the known-bad cases red shows the probe can still fail things.
3. In the LLM play-through, the drift fell to zero. The same game that killed the player in the first few steps now took about three times as long. The player still died. Holding the clock removed my speed from the experiment. It did not make the model a good gamer.

I want that last point to stay visible. The fix took out a confound. It did not improve the thing under test, and I should not report it as if it did.

## The cost is retroactive

The part that took longest was not the code. Every red light the old probe had produced was now suspect. One of them was a conclusion about mouse-look in a first-person game. That conclusion had already been written into a report.

A bug in an instrument is not only a bug going forward. It reaches back to every verdict the instrument has issued since the bug appeared. The only honest move is to find the date range, list the verdicts inside it, and mark them as tool artifacts. Deleting them hides the history. Keeping them unmarked leaves a wrong claim in circulation. I marked them and stopped citing them.

## What I kept

If an LLM drives a real-time system, the model's latency is a variable in your experiment. Freeze time or step it. Do not hope the two clocks line up.

After you fix an instrument, keep the known-bad cases in the test set. They must stay red. If they turn green, you have built a more polite probe.

When you find a measurement bug, put a date on it. Everything the instrument said since then goes into quarantine until someone rereads it.

The games were not hostile. They were running on a clock the tester had never agreed on with them.
