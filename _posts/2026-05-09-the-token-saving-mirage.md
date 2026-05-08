---
layout: post
title: "The Token-Saving Mirage: Why Caveman Talk Won't Save Your API Bill"
subtitle: "Viral prompt tricks vs. what actually works for reasoning compression"
date: 2026-05-09
author: danmi
tags: [llm, reasoning, efficiency, prompt-engineering, research]
---

Last week my timeline exploded with variations of the same idea: "Talk to your LLM like a caveman to save tokens!" and "Use classical Chinese — it's more information-dense!" The [caveman skill](https://github.com/juliusbrussee/caveman) hit 900+ HN upvotes. Reddit threads popped up claiming 30–50% savings from forcing models to think in terse languages.

I spent a day surveying the actual academic landscape on this topic. Here's what I found: **the viral tricks operate in the shallowest layer of a much deeper stack, and the real gains are elsewhere.**

## The Six Layers of Token Compression

When you zoom out, "saving tokens" spans at least six distinct research directions:

| Layer | What it compresses | Key work | Compression |
|-------|-------------------|----------|-------------|
| 1. Textual prompt compression | Input context | LLMLingua-2 (ACL 2024) | 2–5× |
| 2. Symbolic CoT | Reasoning format → code/symbols | Chain-of-Code, Chain-of-Symbol | ~0.5× CoT length |
| 3. **Latent CoT** | Reasoning itself → hidden states | Coconut (COLM 2025), CODI (EMNLP 2025) | **3–10×** |
| 4. Token-level context | Context → soft embeddings | Gisting (NeurIPS 2023) | 4–26× |
| 5. Short CoT | Same format, fewer words | Chain of Draft (2025) | 7.6% of CoT tokens |
| 6. Stylistic | Output language style | Caveman / "think in Chinese" | 2–4× output only |

The caveman trick lives in Layer 6 — the shallowest, least impactful layer. It only touches **output tokens** (not thinking tokens, not input tokens), and even its creator [admits on HN](https://news.ycombinator.com/item?id=47647455) that the 75% savings claim is "preliminary, not a rigorous benchmark."

## Why Terse Languages Don't Actually Help Much

The intuition is appealing: classical Chinese packs more meaning per character. "学而时习之" is 5 characters vs. "study and frequently review what you've learned" at 7 words. Surely fewer characters = fewer tokens = cheaper?

Three problems:

**1. Characters ≠ tokens.** BPE tokenizers (GPT, Llama, Qwen) process rare characters as multi-byte sequences. A single classical Chinese character can cost 2–4 tokens. The string looks shorter to your eyes but not to the tokenizer.

**2. Models think in English internally.** [Wendler et al. (ACL 2024)](https://aclanthology.org/2024.acl-long.820/) showed that Llama-family models have an internal "latent language" that's predominantly English. Non-English input triggers an implicit translation step before reasoning begins. You're not shortening the reasoning path — you're lengthening it.

**3. Out-of-distribution reasoning degrades accuracy.** Classical Chinese constitutes <1% of mainstream pretraining data. Asking a model to reason in it is asking it to reason out-of-distribution. AC-EVAL (EMNLP 2024 Findings) found that CoT provides *limited* benefit even for understanding ancient Chinese texts — let alone reasoning *in* that register.

## What Actually Works: The Research Frontier

### Chain of Draft — The Honest Version of "Caveman Talk"

[Chain of Draft](https://arxiv.org/abs/2502.18600) (Zoom, 2025) does what caveman talk *claims* to do, but with rigor: it prompts the model to write only key-value pairs at each step (`speed=60, t=2h, d=120`). Result: **7.6% of original CoT tokens while matching accuracy on GSM8K.** No training required. Just a better system prompt.

This is the "correct academic version" of the caveman intuition: don't change the language, change the *verbosity constraint*.

### Latent CoT — The Real Frontier

The most exciting work eliminates text-based reasoning entirely:

**Coconut** (Meta, [arXiv:2412.06769](https://arxiv.org/abs/2412.06769)) feeds the model's last hidden state directly back as the next input embedding, skipping the decode→tokenize→embed round trip. The model "thinks" in continuous vector space. On ProntoQA it gains +5–15 points over text CoT while using ~50% fewer generated tokens.

**CODI** ([EMNLP 2025](https://aclanthology.org/2025.emnlp-main.36/)) makes this practical: the same model acts as both teacher (text CoT) and student (latent CoT) via self-distillation. With just 6 continuous thought tokens, it matches full text CoT accuracy on GSM8K. That's a **3× compression** of the reasoning chain — not the output style, the *reasoning itself*.

**Soft Thinking** (NeurIPS 2025) is the training-free version: instead of argmax-ing each token, keep the full probability-weighted embedding as a "concept token." No fine-tuning needed, just a modified decoding loop. MATH accuracy *increases* by 2.5 points while tokens drop 22%.

### The Hierarchy of Impact

If your goal is genuinely to reduce token spend:

1. **LLMLingua-2** for context compression (plug-and-play, 2–5×, proven)
2. **Chain of Draft** for reasoning verbosity (prompt change only, 10×+, published benchmarks)
3. **Latent CoT methods** for the reasoning itself (requires fine-tuning, 3–10×, active research)
4. **Caveman/terse style** as cherry on top (prompt change, ~2× output only, no benchmark data)

Notice the order: the viral trick is literally last in terms of impact-per-effort.

## The Meta-Lesson

Every few months, AI Twitter discovers a "one weird trick" that travels faster than the research it trivializes. Last year it was "just add 'think step by step.'" Now it's "talk like a caveman." These aren't wrong exactly — they gesture at real phenomena — but they're surface-level approximations of deeper ideas that already have proper papers, benchmarks, and implementations.

The gap between "viral AI life hack" and "actual research" isn't just about rigor. It's about *knowing where you are in the stack*. Layer 6 tricks will never match the gains available at Layer 3. If you're optimizing API costs at scale, start from the top of the table, not the bottom.

---

*References: [Chain of Draft](https://arxiv.org/abs/2502.18600) · [Coconut](https://arxiv.org/abs/2412.06769) · [CODI](https://aclanthology.org/2025.emnlp-main.36/) · [Soft Thinking](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f7396d1c54d51416958d63e285377103-Abstract-Conference.html) · [LLMLingua-2](https://aclanthology.org/2024.findings-acl.57/) · [Caveman Skill](https://github.com/juliusbrussee/caveman)*
