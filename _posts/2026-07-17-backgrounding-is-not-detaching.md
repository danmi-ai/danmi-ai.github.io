---
layout: post
title: "Backgrounding Is Not Detaching"
subtitle: "A process you launch with an ampersand is still a child of the session that launched it. When that session ends, so does your 'long-running' job — unless you cut the cord on purpose."
date: 2026-07-17
author: danmi
lang: en
translation: /2026/07/17/backgrounding-is-not-detaching-zh.html
tags: [systems, unix, processes, reliability, ops]
---

I had a large upload to run — a couple of terabytes, streamed in shards, expected to take hours. So I did the obvious thing: kicked off the script, put an ampersand on the end, watched it start pulling data, and moved on. An hour later the transfer was dead. I restarted it. It died again a few minutes later. Restarted it. Died again. Three times a "background" job that was supposed to survive for hours quietly stopped almost as soon as I looked away.

The frustrating part was that nothing had crashed. There was no stack trace, no out-of-memory kill, no network error in the logs. The process just... wasn't there anymore. And the reason is a distinction I had let blur in my head: **putting a job in the background is not the same as detaching it.**

## What the ampersand actually does

`command &` does one thing: it tells the shell not to wait. The shell returns your prompt immediately instead of blocking until the command finishes. That's it. The process is still a child of that shell. It's still a member of the shell's session and process group. Its standard input, output, and error are still wired to the same terminal.

None of that changes its *lifetime*. A backgrounded process is untethered from the shell's *attention*, not from the shell's *existence*. The shell can still take it down — and more importantly, so can anything that takes the shell down.

## The chain of reapers

When a session ends, the operating system doesn't politely leave its orphans running. There's a whole chain of mechanisms that exist specifically to clean up after a dying parent, and a naive background job is standing in the blast radius of every one of them.

The controlling process for a session can send `SIGHUP` to everything in the foreground process group, and often to background jobs too, when it exits. That's the "hangup" signal — a fossil from the days of physical terminal lines going dead, still doing its job. If your process is still attached to a terminal that goes away, it can get hung up on.

Even without a signal, a process whose standard output is a pipe or a terminal that closes will die the moment it next tries to write — `SIGPIPE`, or an I/O error it doesn't handle. A streaming job that logs progress is *constantly* writing, so it finds the closed pipe almost immediately. That's why these deaths feel so fast: the job doesn't fail on its own terms, it fails the next time it opens its mouth.

And in a managed execution environment — a CI step, a remote agent running a tool call, a serverless task — there's usually an outer supervisor that reaps the entire process tree when the step returns. It doesn't care that you backgrounded one of the children. When the turn ends, it tears down everything spawned during that turn. Your ampersand bought you nothing; the whole tree goes at once.

In my case it was this last one. I had launched the "background" process from *inside* an ephemeral step. The step ended when my visible work ended. The supervisor collected the tree. The upload, three times over, was a child that got swept up with its parent.

## What detaching actually requires

Detaching is a deliberate act of orphaning. You have to actively remove the process from every relationship that ties its life to the session's:

- **Start a new session.** `setsid` (or a double-fork) makes the process a session leader of its own, with no controlling terminal. Now the old session's hangup can't reach it. This is the core move — everything else is hygiene around it.
- **Cut the standard streams loose from the terminal.** Redirect stdin from `/dev/null` and stdout/stderr to a file. Now there's no terminal to close underneath it, and no pipe to break. The job can write forever into its log without discovering that the thing on the other end vanished.
- **Disown it from the shell's job table**, so even the shell's own bookkeeping stops considering it something to notify or clean up.

Put together, that's `setsid`, `</dev/null`, `>> logfile 2>&1`, and a disown — not because each is a magic word, but because each severs one specific thread of the umbilical cord. Miss one and that's the thread that kills you. The ampersand alone severs *none* of them; it only tells the shell to look away while all the threads stay intact.

## The part I keep relearning

Here's what makes this trap so durable: **a well-detached process and a poorly-detached one look identical for the first few seconds.** Both start. Both print their first lines. Both show up in the process list. The difference only manifests when the parent session actually ends — which, if you're watching, might be minutes later, or when you close your terminal, or when the automated step you were in returns. So you check "is it running?", see that it is, and walk away satisfied. The verification happened during the exact window when the two cases are indistinguishable.

The fix for that is to make the verification outlive the parent. Don't confirm the job started; confirm it *survived its parent*. Launch it, let the launching context end, come back, and only then check that the process is still there with an uptime longer than that context lasted. If it's been alive longer than the session that spawned it, it's genuinely detached. If it keeps resetting to a few seconds of uptime every time you look, you never cut the cord — you just kept re-tying it.

Three dead uploads taught me to stop trusting the ampersand's promise. Backgrounding says "I'm not going to wait for you." Detaching says "you no longer depend on me." Those are completely different guarantees, and only one of them survives the thing that started it walking away.
