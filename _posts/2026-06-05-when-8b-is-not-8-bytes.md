---
layout: post
title: "When \"8B\" Is Not 8 Bytes: A Rant on the Unit Mess in LLM Land"
subtitle: "On SI prefixes, Byte vs billion, decimal vs binary, and the bilingual translation cliff"
date: 2026-06-05
author: danmi
lang: en
translation: /zh/2026/06/05/when-8b-is-not-8-bytes/
tags: [standards, rant, units, SI, LLM]
---

How messy is unit notation in LLM land? Three real scenarios, and you'll get it.

## Three Confusion Stories

**Story 1: "Is 8B eight bytes?"**

A hardware engineer who's been writing Verilog for 20 years opens his first LLM paper. He sees "Llama 3 8B model" and thinks: *"That's an eight-byte model? No way."* Because B = Byte is twenty years of muscle memory. Only when he reads about 16 GB VRAM does he realize — oh, here B isn't Byte, it's billion, it's parameter count. Same letter, two meanings within half an hour.

**Story 2: "Are 8192 and 300B the same number system?"**

A new grad student reads the GPT-4 docs: context length "8192 tokens", training data "300B tokens." The first is 2¹³ = 8192 = 8 × 2¹⁰, binary-aligned. The second is 300 × 10⁹, decimal SI prefix. Inside one document, the numbering system jumps between binary and decimal. The reader has to mentally classify *every single number* before parsing it.

**Story 3: "Is 15B tokens 1.5 billion or 15 billion?"**

A Chinese grad student reports to their advisor: "We pretrained on 15B tokens." The advisor pauses for two seconds: *"15亿 (1.5 billion) or 150亿 (15 billion)?"* The student freezes — they had subconsciously equated B with 亿. But B = billion = 10⁹ = 十亿; 15B = 15 × ten-billion = **150亿** in Chinese. A factor of 10 difference. Get the numeral wrong, and your scaling-law math is off by an order of magnitude.

---

## Chapter 1: Empirically, How Many Parameters?

You think "Llama 3 8B" means 8,000,000,000? Pull the `config.json` from HuggingFace:

| Marketing name | Actual params | Conversion | Note |
|---|---|---|---|
| GPT-3 "175B" | 175,181,291,520 | ÷10⁹ = 175.18B | SI 10⁹ |
| Llama 3 "8B" | 8,030,261,248 | ÷10⁹ = 8.03B | rounded ~0.4% off |
| Qwen3 "8B" | 8,200,000,000 | ÷10⁹ = 8.2B | rounded **2.4% off** |
| DeepSeek V3 "671B" | 671B total / 37B activated | MoE — must write both numbers | one number is misleading |
| GPT-4 "1.76T" (leaked) | 8×220B or 16×111B | leaked numbers don't agree | architecture itself debated |

*Sources: HuggingFace model cards / `config.json`, official tech reports*

> **Roast**: "8B" is actually 8.03B (Llama) or 8.2B (Qwen). Round numbers look good in headlines. But Chinchilla scaling-law math: 7B × 20 = 140B tokens vs 7.6B × 20 = 152B tokens — that's a 12B-token gap. Your integer rounding just ate ~10% of your compute-budget decision basis. Is the truth that hard to print?

---

## Chapter 2: 8192 — Decimal or Binary?

You've seen these numbers: **512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072**.

LLM context lengths. All powers of 2. "128K context" is *not* 128 × 1000 = 128,000; it's 128 × 1024 = **131,072**. This is genuinely binary (KiB family), because positional encodings, attention masks, and FlashAttention block sizes all align to powers of 2 for hardware efficiency.

But in the same paper, params and token counts use decimal SI K/M/B/T:

```
context = 8192 tokens = 8Ki tokens (binary, 2¹³)
params  = 8B = 8×10⁹ (decimal)
training = 15T tokens = 15×10¹² (decimal)
batch   = 4M tokens = (4×10⁶ or 4×2²⁰? author's mood)
```

The reader is forced to switch bases mentally on every line. Worse, in "4M tokens batch size" the author themselves often hasn't decided between 4×10⁶ and 4×2²⁰. Difference: 4.86%. Enough to make an ablation study draw the wrong conclusion.

---

## Chapter 3: byte vs bit vs billion — Three B's Fighting

Before LLMs, B had agreed-upon meanings in computing:
- **B = Byte** (capital B = 8 bits) — for storage
- **b = bit** (lowercase b = 1 bit) — for transfer rates

Then LLMs added a third:
- **B = billion** (10⁹, parameter count)

Hence the brain-melting sentence:

> "How much memory does an 8B model take in FP16?"
> Answer: 8B × 2 Bytes = 16 GB.

Note: the "8B" is billion, the "Bytes" is byte, and the "GB" is byte. **Three B's, three meanings, one sentence.** A new person can parse this only by leaning on context — not by following any rule. That's not "convention." That's "luck."

---

## Chapter 4: Why ML Companies Keep Using This Garbage Unit

Short answer: **the K/M/B convention came from finance, not engineering.**

When OpenAI launched the GPT-3 API in 2020, pricing was "$0.002 / 1K tokens." That K/M/B isn't from SI prefixes (even if the values happen to match) — it's from how Wall Street prints earnings reports: thousand (K) / million (M) / billion (B) dollars. Finance has used this for decades. Product managers reused it without thinking.

The whole industry copied. Business folks find "$5 / 1M tokens" more intuitive than "$5 × 10⁻⁶ / token". This is a product-management win, not a CS one.

**The problem**: when this finance-speak was carried into technical reports, papers, and code comments, the ambiguity didn't disappear — it just got ignored. A Wall Street analyst reads "15B" and knows it's billion. A hardware engineer reads "8B" and thinks Bytes. Same abbreviation, two cultures, zero explicit marker.

---

## Chapter 5: The Translation Cliff Between English and Chinese

### 5.1 Billion ≠ 亿

Highest-frequency error:
- English **billion = 10⁹ = 十亿** (literally "ten-yi")
- Chinese **亿 = 10⁸**
- So **"15B tokens" = 150亿 tokens** (NOT 15亿)

But Chinese readers instinctively map "15B" → "15亿". Off by 10×.

### 5.2 The "w" Unit That Materialized in Chinese Internet

A pure Chinese-internet phenomenon:
- **w = 万 = 10⁴** (ten-thousand)
- "100w" = 1 million = 10⁶ = 1M
- "1kw" = 10 million = 10⁷ (the SI prefix `k` stacked on top of Chinese 万)
- "500w samples" appears constantly in Chinese tech chats

This `w` lives only in Chinese internet slang. No English doc recognizes it. A foreign colleague seeing `# 500w samples` in a comment might guess: 500 watts? 500 weeks? 500 women?

The horror part is the `kw` stack. SI design rule: prefixes don't compound (you can't write `kk` = 10⁶). But Chinese users freely write "1kw" — to them it's just "thousand" + "ten-thousand" stuck together.

### 5.3 The Tragedy of "兆"

The Chinese character "兆" has **two completely different values** depending on region:
- **Mainland China**: 兆 = mega = 10⁶. "兆字节" = MB.
- **Taiwan / Classical Chinese**: 兆 = 10¹². "一兆" = trillion.

Same character. The two sides differ by **10⁶**. This is the long/short-scale `billion` problem in Chinese form — same word, different orders of magnitude.

---

## Chapter 6: Europe's Historical Baggage — Long vs Short Scale

### 6.1 Two billions

Europeans have been arguing internally for centuries:
- **Short scale** (US / modern UK / international business / science): billion = 10⁹, trillion = 10¹²
- **Long scale** (France / Germany / Iberia / Italy): billion = 10¹², trillion = 10¹⁸

Naming logic:
```
Long scale:  "bi-llion" = million² = (10⁶)² = 10¹²
Short scale: "bi-llion" = 10^(3×2+3) = 10⁹
```

The prefix "bi-" means *the second power of million* in long scale, but *the second step of thousand-stride* in short scale. Same prefix, different logic.

### 6.2 Toward unity

- **1948** 9th CGPM recommends SI prefixes — but doesn't address `billion` because billion isn't an SI word
- **1974** UK government officially switches from long to short scale
- **1991** 19th CGPM extends SI to yotta (10²⁴)
- **2022** 27th CGPM adds ronna (10²⁷) and quetta (10³⁰)
- **Today** older French academics may still parse "1.76 billion parameters" as 1.76 × 10¹²

AI papers default to short scale, but only by convention — no standard enforces it.

---

## Chapter 7: What is SI — A Brief History

**SI = Système International d'Unités** (French: International System of Units). The only globally recognized, rigorously defined, language-agnostic prefix system on Earth.

- **1875** Treaty of the Metre signed in Paris; BIPM (Bureau International des Poids et Mesures) founded
- **1960** 11th CGPM officially adopts the name "SI"; standardizes 7 base units
- **1998** IEC 60027-2 defines binary prefixes: Ki (2¹⁰), Mi (2²⁰), Gi (2³⁰), Ti (2⁴⁰)

SI prefixes:

| Prefix | Symbol | Value | LLM use |
|---|---|---|---|
| kilo | k | 10³ | — |
| mega | M | 10⁶ | API pricing $/Mtok |
| giga | G | 10⁹ | params: Gparam |
| tera | T | 10¹² | training: Ttok |
| peta | P | 10¹⁵ | — |

Note case: m = milli (10⁻³), M = Mega (10⁶). They differ by 10⁹.

Binary prefixes (IEC 60027-2):

| Name | Symbol | Value | vs SI |
|---|---|---|---|
| kibi | Ki | 2¹⁰ = 1024 | +2.4% over k |
| mebi | Mi | 2²⁰ ≈ 1.049M | +4.86% over M |
| gibi | Gi | 2³⁰ ≈ 1.074G | +7.37% over G |

---

## Chapter 8: A Proposal

I'm not asking marketing to change. They won't. But for **internal tech reports, papers, code comments**, we should write rigorously:

| Context | Garbage style | Recommended |
|---|---|---|
| Param count | "8B params" | `8.03×10⁹ params` or `8.03 Gparam` |
| Training | "15T tokens" | `15.0×10¹² tokens` or `15.0 Ttok` |
| Context | "128K" | `131,072 tokens` or `128 Ki-tokens` |
| API pricing | "$5/1M tokens" | `$5/Mtok` (this M=10⁶ is fine) |
| Chinese | "15B = 150亿" | just `150 亿` or `1.5×10¹⁰` |

**Five concrete actions:**

1. Paper appendix: state "All B = 10⁹, all K = 10³ unless suffixed with `i`"
2. Code: `n_params = 8.03e9` instead of `# 8B` comments
3. Chinese docs: drop the B / 亿 / w mixing — use scientific notation
4. Ablation tables: 3 significant figures, with raw count in footnote when rounded
5. Team wiki: add a "number-and-unit conventions" page; mandatory new-hire reading

---

## Closing

Our papers can pin down attention softmax temperature to 4 decimal places, debug the root cause of fp16 loss spikes, and explain RoPE's spectral properties — but our reports' "param count" and "training data" notation is stuck at the 1990 PC-magazine cover level, where K/M/B/T mean whatever you want.

This isn't a detail. It's an engineering-hygiene issue.

We don't need to change marketing copy. But in **internal tech reports, arXiv papers, code comments, and wiki pages**, we should use SI prefixes or scientific notation. It's basic engineering hygiene — leaving a clean interface for the next person and the next discipline.

Next time you write technical documentation, take three seconds: that "8B" — is it 8.03 × 10⁹? 8.2 × 10⁹? 8 × 2³⁰ Bytes? Spell it out. We can do this. It's a small thing. Our field can afford it.

---

*References: [BIPM SI Prefixes](https://www.bipm.org/en/measurement-units/si-prefixes) · [IEC 60027-2](https://physics.nist.gov/cuu/Units/binary.html) · [Long and short scales (Wikipedia)](https://en.wikipedia.org/wiki/Long_and_short_scales) · HuggingFace model cards · DeepSeek-V3 Technical Report (2024)*

*[阅读中文版 →](/zh/2026/06/05/when-8b-is-not-8-bytes/)*
