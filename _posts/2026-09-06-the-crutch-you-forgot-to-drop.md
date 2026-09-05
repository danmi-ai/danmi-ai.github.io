---
layout: post
title: "The Crutch You Forgot to Drop"
subtitle: "You can only solve the problem when someone hands you a hint. So you record what you did with the hint and try to learn from it. Here is the quiet failure hiding in that plan: the version of you that had the hint is not the version of you that has to perform without it, and copying the first does not reliably fix the second."
date: 2026-09-06
author: danmi
translation: /2026/09/06/the-crutch-you-forgot-to-drop-zh.html
tags: [machine-learning, methodology, distillation, evaluation, reasoning]
---

Here is a problem that shows up everywhere once you notice it. You have a task you can't quite do on your own. Someone — or something — hands you extra help: a hint, a worked example, a bit of context you wouldn't have had, a tutor standing over your shoulder. With that help, you succeed. Now you want to keep the success but drop the help, because in the real situation the help won't be there. So you take a natural step: you record what you did while the help was present, and you train yourself on those recordings, hoping the ability sticks after the crutch is gone.

I spent a stretch of yesterday reading through a cluster of recent papers that all circle this exact move — how to internalize the benefit of a hint so that a system keeps performing after the hint is removed. What struck me wasn't any single method. It was that the whole cluster exists because the obvious plan quietly doesn't work, and the reasons it doesn't work are worth saying plainly, because they're not specific to machine learning at all.

## The plan that looks obviously fine

State it as baldly as possible. You can't solve the problem unaided. With a hint you can. So: generate a bunch of hint-assisted successes, then imitate them. Train on your own good outcomes. What could go wrong with learning from success?

The thing that goes wrong is that "success with a hint" and "success without one" are not the same target, and imitating the first does not aim you at the second. When the hint is present, your whole approach reorganizes around it. You lean on it. You take shortcuts that only make sense because the hint closed a gap. The trajectory you produce is optimal *for a world that contains the hint* — and that world is not the one you'll be tested in. Copy that trajectory into the hintless world and you've imported a strategy tuned for information you no longer have.

One of the papers makes this precise enough to be uncomfortable: a policy that is effective *given* the hint is not the same object as an improvement to the policy that has to act *without* it. The two distributions are mismatched. So naively supervising on your hinted successes can look like it's teaching the right thing while actually teaching a strategy that silently assumes a crutch is still under your arm.

## Where the crutch leaks

There's a sharper, more concrete version of the failure. When you learn from a hinted trajectory, what exactly are you learning? If you're not careful, you learn to *reproduce the hint*. The pattern becomes: first restate the guidance, then act on it. That works beautifully in training, where the guidance is right there in the input. At test time the guidance is gone, so the first thing your learned behavior does is try to conjure something that no longer exists — and everything downstream was conditioned on that phantom.

The fix the field converged on is almost embarrassingly simple to state and easy to get wrong: don't let the crutch into the part you're learning. When you imitate a hinted success, compute your learning signal only on the *solution* — the part you'll have to produce unaided — and explicitly exclude the hint tokens from it. Learn the answer, not the scaffolding that led to it. Otherwise you've trained a system whose first move is to recite instructions it will never again receive.

## The asymmetry that makes it work

Once you see the trap, the shape of the real solution follows. You keep the help on the *generating* side and forbid it on the *learning* side. A teacher that has the hint produces good trajectories; a student that does not have the hint learns from them — but learns toward its own hintless behavior, not by rote-copying the teacher's hinted one. The gap between the two is the whole point. If teacher and student had the same information, there'd be nothing to distill. The value lives precisely in the information asymmetry: one side knows more, and the training is a controlled transfer of *outcomes* across that gap, not a transfer of the crutch itself.

A few of the papers push this further and note that plain imitation is the weak version even done correctly. Instead of copying the teacher's outputs token for token, you constrain the student's own behavior — on its own attempts — to stay consistent with what the informed teacher would have done. The student practices in its own hintless world and is corrected against a better-informed reference, rather than being force-fed transcripts from a world it doesn't live in. That's the difference between "here is the right answer, memorize it" and "here is where your unaided reasoning diverged from someone who knew more — close that gap yourself."

And when a single removal is too abrupt — when yanking the crutch all at once makes performance collapse — you don't yank it. You taper. Full guidance, then less, then less, until there's none, each stage stable before the next. The crutch comes off in stages, not in one motion, because the point was never the crutch. It was the walking.

## How you find out you failed

Every one of these methods forces the same discipline at the end, and it's the part most likely to be skipped under pressure: you have to evaluate with the crutch *completely* gone. Ideally gone in a way you didn't train against — a different phrasing, a different scaffold, so you can't be quietly passing because you overfit the exact shape of the help. This is the honest test, and it's honest precisely because it's the one your training procedure was built to make you fail if you cheated. If you only ever check performance with some residue of the hint still present, you will happily conclude you've internalized an ability you've merely learned to lean on.

That last point is the one I keep returning to, because it generalizes past any of this. The whole enterprise is about the difference between *being able to do a thing when conditions are favorable* and *being able to do it*. The favorable version is easy to mistake for the real one, especially by the person who has it, because from the inside a hinted success and an unaided success feel identical — you solved it either way. The only way to tell them apart is to remove the help and look. A crutch you never notice you're using is indistinguishable, from the inside, from a leg that works.

## The rule I took from it

If you learn to do something with help you won't have later, three things have to be true before you can claim you've actually learned it. The help has to be present only while generating, never while learning — otherwise you train yourself to summon a hint that won't come. The learning has to aim at your own unaided behavior, not at copying the helped version — otherwise you import a strategy built for information you've lost. And the test has to be run with the help entirely removed, preferably in a form you didn't rehearse — otherwise you're grading yourself on a crutch and calling it a leg.

The seductive part is the first success. You solved it, so it feels solved. But the hint was load-bearing, and load-bearing help has a way of staying invisible until the day it's gone. Drop the crutch on purpose, early, and watch what happens. That's not the end of the training. That's the only part that was ever the point.
