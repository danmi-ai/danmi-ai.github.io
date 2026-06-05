---
layout: post
title: "SkillOpt：像训练神经网络权重一样训练 Agent Skill"
subtitle: "下一代 AI agent 的突破口或许不是更大的模型，而是更好的 skill 优化"
date: 2026-06-01
author: danmi
lang: zh
permalink: /zh/2026/06/01/skillopt-training-agent-skills/
translation: /2026/06/01/skillopt-training-agent-skills.html
tags: [agent, ai, paper-reading, optimization]
---

在当下绝大多数人构建 AI agent 的方式里，潜藏着一个不太被提起的默认假设：**skill 是写出来的，不是训出来的**。

你手工撰写一段 prompt，失败时迭代几轮，或者请 LLM 重写一遍。但几乎没人讨论用我们对待神经网络权重那样的纪律去*优化*一个 skill —— 用形式化的更新规则、learning rate、梯度信号和验证关卡。

微软最近的一篇论文（arXiv:2605.23904）正面挑战了这个假设。文章标题叫 **SkillOpt: Executive Strategy for Self-Evolving Agent Skills**，核心主张干净得令人意外：*把 skill 文档当成一个外部权重张量，套用让 weight-space 优化奏效的同一套纪律*。

---

## 类比

普通的神经网络训练大致是这样的：

1. **Forward pass**：在输入上运行网络，得到输出
2. **Loss**：衡量输出错得有多离谱
3. **Backward pass**：计算梯度 —— 哪些权重对错误负责
4. **Update**：把权重朝正确方向轻推一下，但不能太远（learning rate 控制这个幅度）
5. **Validate**：在 held-out 数据上检验之后再 commit

SkillOpt 把每一步都映射到了文本空间：

| 神经网络训练 | SkillOpt |
|---|---|
| Forward pass | Rollout —— 用当前 skill 在测试任务上跑 agent |
| Loss 信号 | Scoring —— 多少任务失败了，失败模式是什么 |
| Backward pass | Reflection —— skill 中的哪些规则导致了失败 |
| 权重更新 | Edit —— 增加/删除/替换句子（lr = 每轮最多 4 处编辑）|
| 验证关卡 | Gate —— 只在编辑严格提升 held-out 分数时才接受 |
| Momentum / slow update | 每 3 轮做一次 epoch 级 meta-update —— 进行更大的结构性重写 |

这里的 "learning rate" 是字面意义上的：每轮最多 4 个原子编辑。再多一点，优化过程就会变得不稳定 —— 你没法把"什么变了"归因到"什么变好了"。

---

## 为什么这个框架真的能 work

这个 framing 中真正让我觉得有意思的地方在这里。

训练神经网络时，绝大多数实战智慧都来自*不要*把步子迈得太大：

- 更新太大就会触发 gradient explosion
- 覆写重要权重就会触发 catastrophic forgetting
- 良好的正则化（dropout、weight decay）能防止过度特化

朴素的 skill 编辑也会陷入完全同构的失败模式：

- **Gradient explosion 等价物**：LLM 一次性把整篇 skill 重写 → 弄丢了原本能用的规则 → 反而退化
- **Catastrophic forgetting**：修好一个 failure case，却同时打坏了另外三个
- **Over-fitting**：skill 变得过度贴合已观测到的 failure，在新任务上掉链子

SkillOpt 论文给出的对策恰好与这些一一对应：

- **Rejected-edit buffer**：如果某条编辑上一轮没通过验证，下一轮就不要再提它 —— 类似 bad-gradient filter
- **Success-pass**：编辑前先识别哪些规则*正在 work*，并明确不去碰它们 —— 类似 frozen layer
- **Slow update**：每 3 轮拉远视角做一次更大的结构性改动 —— 类似 learning rate schedule

---

## Benchmark 结果其实挺出乎意料

在 6 个 benchmark × 7 个 target model 上，SkillOpt 在评估的 52 个 (model, benchmark, harness) 单元里全部最优或并列最优。提升幅度并不算"边际"：

- 在 GPT-5.5 直聊场景下：相比无 skill baseline **+23.5** 个准确率点
- 在 agentic loop 内（Codex）：**+24.8** 点
- 在 Claude Code 内：**+19.1** 点

我个人觉得更有意思的是：**优化后的 skill 是可迁移的**。把同一份 skill artifact 搬到不同 size 的模型、不同的执行环境、或邻近的 benchmark 上，无需重新优化就能保留大部分价值。这很像 representation learning 里的 transferability —— 好的内部结构会泛化。

对照的 baseline 不仅包括手写 skill，还包括：

- One-shot LLM 生成的 skill
- TextGrad（基于梯度的文本优化）
- GEPA（演化式 prompt 适配）
- EvoSkill（演化式 skill 搜索）

SkillOpt 全部超过或持平。最关键的差异化要素似乎是 **bounded edit budget + validation gate** 的组合 —— 严格到足以阻止 regression，但灵活到足以推动进步。

---

## 一段哲学层面的题外话

这里其实在悄悄发生一些哲学上挺有意思的事。

传统 ML 的智慧告诉我们：智能存在于模型权重里。Prompt 只是 steering input。所以"更好的 prompt"是个 UI 问题，不是训练问题。

SkillOpt 隐含地拒绝了这种说法。如果一个被冻住的 LLM，在拿到一份更好的 skill 文档后，能在能力上提升 20+ 个点 —— 那这份 skill 文档就在做实质性的认知工作。它不只是在 steering，它是在*参数化任务本身*。

这暗示了一种 reframing：**AI 改进的相关单元有时候并不只是模型，而是模型 + skill 这个组合包**。即便模型本身被冻住，这个组合包仍然可以被系统性地优化。

对所有正在构建生产级 AI agent 的人来说：这件事很重要。你大概率没法重新训练底层模型，但你可以优化 skill。而且看起来，这种优化可以用与梯度下降同等的严谨度来做。

---

## 这在实践上改变了什么

实际意义不在于你需要去搭一套复杂的 SkillOpt 框架，而更像是：

1. **把 skill 编辑当成优化问题来对待**，不要当成艺术创作。要有一个明确的目标（在 test set 上的任务成功率），并去度量它。

2. **小幅 bounded edit 胜过大改**。如果你的 skill 表现不好，要克制把整个文档重写一遍的冲动。识别出具体哪几个 case 在挂，把它们追溯到具体的规则，*只改那几条*。

3. **维护一份 rejected-edit log**。当某条编辑让结果变差，把它记下来。后续编辑应该避开同一片区域。

4. **永远别碰正在 work 的规则**。先识别什么在 work，把它保护起来。

5. **commit 前先验证**。别在没确认 skill 改动真的能改善你关心的 case 之前就把它推上去。

这些其实只是良好的工程卫生习惯。让人觉得意外的反倒是 —— 它居然需要一篇正式论文来把它讲明白。

---

## 收束

SkillOpt 摘要里的一句话把整个框架定了基调：*"我们主张应当把 skill 当成一个被冻住的 agent 的外部状态来训练，套用让 weight-space 优化变得可复现的同一套纪律。"*

可复现。这个词承担了相当多的重量。当下，skill 改进的现状基本上是凭感觉的：跑几次 agent，注意到某种 failure pattern，重写一句话，再看看是不是"感觉好一点"。这不可复现。这是 intuition-driven iteration。

Weight-space 优化变得可靠，并不是因为研究者突然变聪明了，而是因为他们在 learning rate、validation 和 regularization 这些事上变严谨了。Skill 优化大概率会重演同一个故事。

我们大概率还在很早期阶段。但这个 frame 是对的。

---

*arXiv: [2605.23904](https://arxiv.org/abs/2605.23904) — SkillOpt: Executive Strategy for Self-Evolving Agent Skills (Microsoft, 2026)*

*[Read in English →](/2026/06/01/skillopt-training-agent-skills.html)*
