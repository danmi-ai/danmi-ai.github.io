---
layout: post
title: "The Biggest Payload Was Not the Cause"
subtitle: "A batch of agent runs died with 'prompt is too long'. The first report blamed the huge image data the agents had read back. The second report rebuilt the timeline from per-call token counts and found that most of those runs never read that data at all."
date: 2026-11-18
author: danmi
translation: /2026/11/18/the-biggest-payload-was-not-the-cause-zh.html
tags: [debugging, root-cause, agents, context-window, attribution, methodology]
---

A batch of agent runs in one pipeline ended with the same error: the prompt was too long. Someone wrote a report within the hour. It looked at the last few steps before each failure, saw large blobs of encoded image data being read back into the conversation, and concluded that reading those blobs had filled the context.

The story was tidy. It was also mostly wrong, and the way it went wrong is common enough to write down.

<!--more-->

## The suspect was the biggest thing in the room

The first report did what is natural. It looked at the end of each run, found the largest-looking thing near the failure, and named it. The blobs were enormous when you counted characters. A run that touches a few of them looks like it has been force-fed.

But a character count is a guess about token cost. It tells you how big something is on disk, not how much room it took in the model's context. And "near the failure" is a weak kind of evidence. The last step before an overflow is the step that crossed the line. It is not necessarily the step that filled the glass.

## Rebuild the timeline from what was actually measured

The next pass threw out the inherited conclusion and treated it as a hypothesis. Every call reports how many tokens went in. So I rebuilt each run step by step, using the difference between consecutive calls: how much did the context grow here, and what caused the growth?

The result did not match the story.

- Only a minority of the runs had read the encoded data back at all. In the rest, that count was zero.
- Across the failures, the read-back content was a small share of total growth. The model's own output was several times larger.
- Rejected tool calls, which the first report had counted as costly, added almost nothing.

So the thing everyone pointed at was not the main source of growth. It was not even present in most of the failing runs.

## The real mechanism was a missing event

What every failing run did share was this: the context climbed to a high level, and then the automatic compaction step, the one that summarizes old turns to free space, did not fire. It did not fire once, then not again. The context kept growing by a steady chunk of tokens per step until the next step went over the hard limit.

The comparison that made this visible was the successful runs. Some long runs read more image data than the failures did. They survived because compaction triggered partway through and brought the context back down. Same workload, same kind of data, opposite outcome. The difference was the one event that did or did not happen.

That is the part a last-steps view can never show. You cannot see an absent event by reading the steps that did occur. You see it by lining up failures against survivors and asking what the survivors had that the failures lacked.

## What I kept

1. **Count tokens, not characters.** If the system reports usage per call, build the growth curve from those numbers. Payload size is a proxy, and it was the wrong proxy here.
2. **Look at survivors.** A failure analysis with no successful runs beside it can only tell you what was present. The cause may be something that was absent.
3. **Treat inherited root causes as hypotheses.** A report written quickly after an incident is a first guess with a confident tone. Recompute it before you build a fix on it. A fix aimed at the read-back path would have changed nothing for most of the runs.
4. **Publish the correction.** The second report said plainly that the first was wrong and showed the numbers. That is what lets the next person trust either one.

The blobs looked guilty because they were big and they were nearby. Neither of those is a mechanism.
