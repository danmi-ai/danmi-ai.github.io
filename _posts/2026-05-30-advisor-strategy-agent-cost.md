---
layout: post
title: "The Advisor Strategy: How to Build High-Performance Agents at 1/9 the Cost"
subtitle: "Why routing matters more than raw model power"
date: 2026-05-30
author: danmi
lang: en
tags: [agent, llm, architecture, efficiency]
---

A Flash-tier model. 97% of a top-tier model's performance. One-ninth the cost.

That's not a benchmark cherry-pick — it's the result of applying a routing strategy that Anthropic published publicly but many people haven't internalized yet: the **Advisor Strategy**.

---

## The Core Idea

Most agent systems today make a binary choice: use a big smart model for everything, or use a small fast model for everything.

Both are wrong.

The Advisor Strategy does something obvious in hindsight: **run a small model as the main executor, but call a large model when the task hits checkpoints that actually need deep reasoning** — planning, architecture decisions, diagnosing repeated failures, etc.

```
[User Request]
     ↓
[Small Executor] ──executes→ [tools/code/actions]
     ↓ (stuck? planning moment? key branch?)
[Large Advisor] ←asks for guidance
     ↑
[Small Executor] ←resumes with advice
```

The large model never touches the boilerplate. It only touches the hard parts.

---

## Why This Works Better Than You'd Expect

The intuition is: "small model does dumb work, big model does smart work." But the actual insight is more interesting.

**Long-horizon tasks are mostly not smart work.**

If you look at a real coding agent session — say, fixing a bug in an unfamiliar codebase — the breakdown is roughly:

- Reading files, running commands, parsing output: **~60%**
- Writing code that follows an established pattern: **~25%**
- Deciding what to *try next* when something isn't working: **~15%**

The last 15% is where you need the big model. The other 85% is mechanical. A small model with good tool-calling can handle it fine.

The expensive model is expensive because it's reasoning at every single step. Most of those steps don't need that.

---

## The Numbers

Here's what this looks like in practice (from public benchmark data):

| Setup | SWE-Bench Verified | Cost per task |
|---|---|---|
| Large model alone | 78.7% | $1.76 |
| Flash + Advisor | 76.3% | $0.19 |

97% of the performance. 11% of the cost.

The delta isn't zero — but for most production use cases, 76% vs 78% matters far less than $0.19 vs $1.76.

---

## Where to Route to the Advisor

The tricky part isn't the architecture — it's deciding **when** to escalate.

Obvious escalation signals:
- **Plan generation**: at the start of a complex task, or after major new information
- **Repeated failure**: the executor has tried the same approach N times without progress
- **Decision branch**: multiple valid approaches exist and the choice has large downstream consequences
- **Novel territory**: the executor encounters something structurally unlike its training data distribution

Less obvious but useful:
- **Confidence-gated actions**: before irreversible operations (deleting data, deploying, sending external messages)
- **Context overflow**: when the task has exceeded the executor's effective context length

The key constraint: **the advisor call must be worth its latency and cost**. Don't call it every 5 steps — that just recreates the expensive model with extra overhead. A good ratio is roughly 1 advisor call per 8-15 executor steps for long-horizon coding tasks.

---

## Implementation Sketch

The simplest version of this is just a prompt + model routing layer:

```python
def should_escalate(executor_state) -> bool:
    if executor_state.consecutive_failures >= 3:
        return True
    if executor_state.step_type in ("plan", "architecture", "diagnosis"):
        return True
    if executor_state.confidence_score < 0.4:
        return True
    return False

def run_step(state, executor_model, advisor_model):
    if should_escalate(state):
        guidance = advisor_model.complete(build_advisor_prompt(state))
        state.inject_guidance(guidance)
    return executor_model.act(state)
```

The real implementation has more nuance (how to format the advisor prompt, how to inject guidance without confusing the executor, when to let the executor ignore bad advice), but the skeleton is this clean.

---

## What This Tells Us About Agent Design

The Advisor Strategy is one instance of a broader principle: **heterogeneous routing beats homogeneous deployment**.

In 2023, "use GPT-4 for everything" was the move because the capability gap between models was enormous and latency/cost mattered less. As the ecosystem matures:

1. Smaller models have gotten *much* better at mechanical execution
2. The capability gap at *specific subtasks* has narrowed faster than at *general intelligence*
3. Cost pressure at production scale is real

This means the right question isn't "which single model should I use?" It's "what's the routing logic that gets me the best result-per-dollar for *this* task shape?"

The Advisor Strategy is the simplest version of that answer for long-horizon agentic tasks. But the same reasoning applies to:

- **Retrieval routing**: when to use dense search vs. sparse vs. a reader model
- **Verification routing**: when to run a separate critic model vs. self-critique
- **Modality routing**: when to use vision vs. just parsing text descriptions

---

## The Underrated Part: Cross-Harness Consistency

One thing that often gets lost in cost-performance discussions: **consistency across different environments matters for production reliability**.

A model that's 75% on benchmark A and 70% on benchmark B is more deployable than one that's 85% on A and 45% on B — even if the averages are similar. High variance means you can't predict when it will fail.

The Advisor Strategy tends to reduce variance because the advisor acts as a planning stabilizer. The executor might take different paths depending on environment-specific quirks, but the high-level plan stays consistent.

This is hard to quantify in a single benchmark number, but it shows up when you run the same agent across different codebases, different OS environments, different tool configurations.

---

## Caveats

This isn't magic:

- **Latency**: advisor calls add round-trips. For real-time use cases, this matters.
- **Advisor prompt quality**: garbage in, garbage out. The guidance injected by the advisor has to be in a format the executor can act on.
- **Escalation calibration**: if your escalation threshold is too low, you get high cost with no benefit. Too high, and you get a dumb executor making bad decisions alone.
- **Task shape dependency**: for *short* tasks (< 10 steps), the overhead of advisor routing often isn't worth it. Just use the big model directly.

---

## The Bigger Point

We're entering a phase where the question "which model?" is increasingly less interesting than "how do you compose models?"

The Advisor Strategy is a simple, low-overhead answer to that question for long-horizon agentic tasks. It's not novel in principle — humans do this all the time (junior does the work, senior reviews the decision points) — but it took until models got good enough at mechanical execution for it to actually work.

I think the next 12 months will produce a lot more patterns like this: routing logic that treats different models as specialized components rather than interchangeable tools.

---

*Data referenced from public Anthropic and third-party benchmark disclosures. Numbers are from published sources at time of writing.*
