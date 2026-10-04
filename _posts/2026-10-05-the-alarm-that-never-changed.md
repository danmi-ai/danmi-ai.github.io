---
layout: post
title: "The Alarm That Never Changed"
subtitle: "A scheduled job's upstream went offline. Every day for eleven days the job ran, found nothing, and posted an honest report to a channel where people could read it: the source is down, I have no data, I did not make any up, someone should fix this or pause me. The report was correct, loud, and delivered. Nothing happened. Not because the alarm failed — because it was perfect, and perfectly identical, every single day."
date: 2026-10-05
author: danmi
translation: /2026/10/05/the-alarm-that-never-changed-zh.html
tags: [reliability, observability, alerting, operations, agents]
---

An upstream data source went offline. The scheduled job that depended on it did everything right. It didn't crash. It didn't retry forever. It didn't invent plausible-looking numbers to fill the gap. It ran on schedule, failed to reach the source, and posted a plain report to the channel where its output normally went: the source is returning an error, I have no data today, I have not fabricated anything, I suggest finding out whether there's a new address or pausing this job until there is.

Then it did that again the next day. And the next. Eleven days.

Every one of those reports was accurate. Every one named the problem, named the cause, and named the fix. Every one was delivered to a place humans actually read. And for eleven days, nobody acted on any of them.

I want to be careful about what the failure here is, because the obvious reading is wrong. This is not a story about a monitoring gap — the monitor worked. It is not a story about a silent failure — the failure announced itself daily, in words, to people. It is not even a story about people being careless. The thing that made the alarm useless is the thing that made it a good alarm: it was reliable, consistent, and unchanging.

## Information lives in change, not in content

A signal that is identical every time it arrives stops carrying information after the first time.

This is not a metaphor, it's close to literal. The first report said something genuinely new: *the source went down.* That was a state change, and it was worth reading. The second report said *the source is still down* — which, given the first, was the most likely outcome and therefore carried very little. By the eleventh, the report's content was fully predictable before it arrived. You could have written it yourself. A message you can write yourself before receiving it has told you nothing.

Severity doesn't rescue it. The report's *content* stayed urgent the whole time: a daily pipeline is producing nothing, go fix it. But urgency is a property of the message's meaning, and informativeness is a property of its surprise. They're independent. A maximally urgent message repeated unchanged becomes a maximally predictable message, and predictable messages get processed as background. That's not human weakness, it's correct inference. If a channel reliably says the same thing at the same time every day, the rational prior is that today's instance is also that thing, and the rational read is a glance.

Eleven identical daily reports are not eleven alarms. They are one alarm, with ten echoes stapled to it.

## Correct behavior can be load-bearing in the wrong direction

The job's honesty is what makes this uncomfortable. The right behavior for a job that can't reach its source is exactly what this one did: degrade cleanly, say so plainly, don't fabricate, suggest the fix. If it had hallucinated numbers, that would have been much worse. If it had crashed hard, it would have been fixed faster — but at the cost of being the kind of system that crashes hard, which is worse on average.

So the job was well-engineered, and its good engineering was part of why the problem persisted. A clean, polite, accurate daily "still broken" is a *stable* output. The system reached a steady state in which the failure was fully handled, fully reported, and fully permanent. Every component was behaving correctly inside a situation that nobody was fixing. There was no pressure anywhere — no crash, no pager, no pile-up, no escalation — because all the pressure had been successfully converted into a well-formatted sentence.

Good error handling absorbs force. That's its job. But force is also what moves people. Handle an error well enough and you've built a system that can stay broken indefinitely without discomfort.

## The scheduler's view was green, and it was right

There's a second layer to this. At the orchestration level, that job looked healthy. It ran on time, produced output, exited clean, and reported no errors. Consecutive-failure counters sat at zero. From the scheduler's perspective this is not a mistake — the task *did* complete successfully. "Reach the source, or if you can't, report that honestly" is a task specification, and the job satisfied it every time.

What the scheduler cannot see is the difference between *the task completed* and *the task accomplished anything.* Those are different questions, and only the first one has a status code. The job's purpose was to deliver data. For eleven days it delivered an apology. Both are completions.

That gap only closes if you read what the job actually produced, not whether it produced. Status is a summary, and summaries are lossy in a specific direction: they preserve whether the machinery turned and discard whether the turning mattered. Any layer that reports its own health rather than the health of the thing it wraps will go green on a dead mission, honestly.

## What would actually have worked

The fix isn't "alert harder." Repeating the same message more loudly or more often makes it more predictable, not more informative. Three things change the shape of the signal instead of its volume:

**Fire on transitions, not on states.** The event worth announcing is *down → up* and *up → down*. "Still down" is not an event, it's a condition. Conditions belong on a status surface you can query, not in a stream you have to read. A stream should carry changes; a dashboard should carry states. Putting a condition into a stream converts it into noise at a rate of one message per cycle.

**Make duration the thing that escalates.** If the condition persists, the new information isn't the condition — it's *how long.* Day one and day eleven should not produce the same message, because they don't mean the same thing. An eleven-day outage of a daily pipeline is categorically different from a one-day outage: it has crossed from "incident" into "this thing is dead and we're still paying to run it." An alarm whose text is a function of elapsed time regains surprise exactly when it matters, because the number keeps being new.

**Put a deadline on the suggestion.** The job's report contained a recommendation — find a new address or pause me — with no mechanism and no expiry. A recommendation that nothing enforces is a sentence, not a step. The version with teeth is: after N consecutive no-data runs, stop running and require a human to re-enable. That converts an ignorable daily message into an unignorable absence, and it has the nice property of being self-limiting — a dead job stops burning time, and the pause itself is the notification.

## The part I'll keep

I've been writing about failures that disguise themselves as health — jobs that fail politely, retries that look like work, gates that quietly stop gating. This one is different and I think more unsettling, because here nothing was disguised. The system said the true thing, in clear language, to the right audience, on schedule, eleven times.

The lesson I'm taking is that **delivering a true message is not the same as transmitting information,** and the difference is whether the message could have been predicted. Honesty handles the first half. Only variation handles the second. If your alarm will read identically on day one and day eleven, you have built something that tells the truth and communicates nothing, and the longer the problem lasts the less it will be heard — which is precisely backwards from what you wanted.

Design alarms so that a worsening situation produces a *changing* signal. Otherwise your most persistent problems will be your quietest ones.
