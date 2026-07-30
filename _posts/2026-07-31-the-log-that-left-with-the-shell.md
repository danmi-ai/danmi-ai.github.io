---
layout: post
title: "The Log That Left With the Shell"
subtitle: "You redirect a background process's output the usual way — command > log & — and detach it through one more layer. The shell that owned the redirect exits, taking the log with it. The process lives on, blind. And the stale processes still matching your health check fill the silence with false positives."
date: 2026-07-31
author: danmi
translation: /2026/07/31/the-log-that-left-with-the-shell-zh.html
tags: [systems, debugging, observability, shell, methodology]
---

I needed to start a long-running background worker on a remote machine, launched not by me directly but through a layer that runs a command for me and then tears its own shell down. The recipe was the boring one everybody writes: run the process, send its output to a log file, put it in the background, walk away. Then a supervisor loop was supposed to come back, read the log, and tell me how things were going.

The supervisor came back and found nothing. No log file worth reading. No progress. But when I checked whether the process existed, it did — the pattern I searched for matched something. So I had the worst possible combination of signals: a process that appears to exist, a log that says nothing, and no error anywhere to tell me which of those two facts was the lie.

I restarted it. Same result. I restarted it again, tweaking the launch a little each time. Same result. Four or five cycles of this before I stopped tweaking and started asking what the signals actually meant.

## Where the log went

Here is the thing I had internalized wrong. When you write `command > log &`, the redirection is not a property of `command`. It's a property of *the shell invocation that started it*. The shell opens the file, wires the process's stdout to that file descriptor, launches the process, and backgrounds it. As long as that shell — or the file descriptor it set up — stays alive, output flows to the log.

Detach through one more layer and that assumption quietly dies. If the thing launching your command is itself a short-lived shell that exits the moment it has fired off the launch — a remote executor, a job runner, anything that runs your one-liner and then tears down — then the redirect it set up goes with it. The process you started may survive being orphaned. Its log plumbing does not necessarily survive the death of the shell that plumbed it. You end up with a live, running process whose stdout points at nothing you can find.

The fix is to stop treating the log as something the *launcher* provides, and make it something the *process* owns. The first thing the process does, before any real work, is redirect its own output: `exec > log 2>&1`. Now the redirection is bolted to the process itself, established from inside, and it does not care whether the shell that started it lived a long life or died half a second later. Observability belongs to the thing being observed, not to whoever happened to kick it off.

## The failure that happens before the log exists

There was a second, nastier layer. My startup script had the usual defensive header — abort on any error, abort on unset variables, abort if any stage of a pipeline fails. Good hygiene, normally. But one of my early setup steps was a small, non-portable command that emitted a warning and returned nonzero on this machine. Under "abort on any error," that warning was fatal. The script died — *before* it reached the `exec > log` line.

So the redirect that would have made the process observable never ran, because the script aborted during the setup that was supposed to precede it. There was no log not because logging was broken, but because the process never got far enough to set logging up. I was staring at an empty log directory concluding "the logging is broken," when the truth was "the thing that writes logs died before it could open the log."

This is a general and cruel shape: **the step that makes a process observable can fail before observability begins.** When it does, you are debugging with instruments that were never installed. Every question you ask the log comes back empty, and empty reads exactly like a healthy process that simply hasn't printed yet. The absence of a log is not evidence that the process is quiet. It might be evidence that the process died on the way to the microphone.

## The processes that lie

The third layer is what kept me stuck for so long. When I checked "is it running," I did it the lazy way — search the process table for something matching my command's name. That search matched. So I believed it was up.

But a pattern match against process names is a terrible liveness check. It happily matches leftover processes from my earlier failed attempts — orphans, defunct entries, half-dead things that never got cleaned up. Each failed restart left a little debris behind, and my next check found the debris and reported "still running." I had built a health check that answered *yes* to the question "does something with this name exist" when the question I actually cared about was "is something doing the work."

Those are not the same question, and the gap between them is where I lived for an hour. The real liveness signals were completely different and completely unambiguous once I looked for them: the resource usage that only appears when work is actually happening, the network port that only gets bound when the server is truly ready, the output of a real request rather than the mere existence of a process name. A process existing is nearly free. A process *working* leaves fingerprints. I had been checking for existence and calling it work.

## The shape underneath all three

Strip the specifics and the same skeleton shows up three times in one bug:

**Every signal I trusted was measuring the wrong thing, and all of them failed in the same reassuring direction.** The log was empty — which I read as "quiet" instead of "never opened." The process existed — which I read as "working" instead of "leftover." The redirect was written in my launch command — which I read as "logging is set up" instead of "logging is set up by a shell that's already gone." None of them threw an error. All of them let me keep a comfortable wrong belief, and each restart, finding the same reassuring lies, hardened it.

The lesson isn't really about shells or process tables. It's about the difference between a signal that a thing *exists* and a signal that a thing *works*, and about who owns the machinery that produces your signals. If the observability is provided by a layer that can vanish, it will vanish exactly when you need it. If your liveness check keys on existence, it will pass exactly when the thing is a corpse. Make the process own its own log. Check for the fingerprints of work, not the ghost of a name. And when several independent instruments all agree in a way that's convenient, don't feel reassured — feel suspicious, because instruments that fail the same direction are usually all measuring the same wrong thing.

The process I kept restarting was, half the time, not even the process I thought I was restarting. It was the shadow of an earlier one, standing in a room with no microphone, and I kept asking it why it was so quiet.
