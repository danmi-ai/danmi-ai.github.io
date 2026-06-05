---
layout: post
title: "Advisor Strategy：如何用 1/9 的成本造出高性能 Agent"
subtitle: "为什么路由策略比单纯堆模型能力更重要"
date: 2026-05-30
author: danmi
lang: zh
permalink: /zh/2026/05/30/advisor-strategy-agent-cost/
translation: /2026/05/30/advisor-strategy-agent-cost.html
tags: [agent, llm, architecture, efficiency]
---

一个 Flash 级别的小模型。性能达到顶级模型的 97%。成本只有九分之一。

这不是 benchmark 上挑出来的好看数字——而是把 Anthropic 公开发布、但很多人还没真正吃透的一种路由策略落地后的实际结果：**Advisor Strategy（顾问策略）**。

---

## 核心思路

如今大部分 agent 系统都在做一个二元选择：要么所有事情都用大模型，要么所有事情都用小模型。

两种做法都不对。

Advisor Strategy 做了一件事后看来很显然的事：**让小模型作为主执行器（executor）持续推进任务，只在真正需要深度推理的关键节点上调用大模型**——比如规划、架构决策、诊断反复失败的问题等等。

```
[用户请求]
     ↓
[小模型 Executor] ──执行→ [tools / code / actions]
     ↓ (卡住？规划时刻？关键分支？)
[大模型 Advisor] ←请求指导
     ↑
[小模型 Executor] ←带着建议继续推进
```

大模型从不碰那些套路化的工作，只在真正困难的环节出手。

---

## 为什么这套方案的效果比你以为的还要好

直觉上的解释是："小模型干粗活、大模型干细活"。但真正的洞察其实更有意思。

**长链路任务里，绝大部分都不是真正需要"动脑"的工作。**

如果你认真观察一个真实的 coding agent 会话——比如在一个不熟悉的代码库里修一个 bug——任务的分布大致是这样：

- 读文件、跑命令、解析输出：**约 60%**
- 按既有模式写代码：**约 25%**
- 在某个方案不奏效时决定**下一步**该怎么走：**约 15%**

最后那 15% 才是真正需要大模型的地方。剩下 85% 都是机械性的工作。一个具备良好 tool-calling 能力的小模型完全能搞定。

大模型贵在哪里？贵在它**每一步**都在做高强度推理。但绝大多数步骤根本不需要那种推理。

---

## 数字说话

实际效果是这样的（来自公开 benchmark 数据）：

| 配置 | SWE-Bench Verified | 单任务成本 |
|---|---|---|
| 仅用大模型 | 78.7% | $1.76 |
| Flash + Advisor | 76.3% | $0.19 |

性能保留 97%，成本只有 11%。

差距不是零——但在大多数生产场景中，76% 和 78% 之间的差距远没有 $0.19 和 $1.76 之间的差距来得重要。

---

## 何时该路由给 Advisor

真正棘手的不是架构本身，而是判断**什么时候**该升级到 advisor。

明显的升级信号：
- **规划生成**：复杂任务的开始阶段，或者拿到重大新信息之后
- **反复失败**：executor 已经在同一个思路上尝试了 N 次还没有进展
- **决策分叉**：存在多个合理方案，且不同选择会带来差异巨大的下游后果
- **未知地形**：executor 遇到的问题在结构上明显偏离它训练数据的分布

不那么明显但很有用的：
- **置信度门控的动作**：在执行不可逆操作之前（删除数据、部署上线、发送对外消息）
- **上下文溢出**：任务已经超出 executor 的有效 context 长度

关键约束在于：**advisor 的每一次调用都必须值回它的 latency 和 cost**。不能每 5 步就 call 一次——那样做无非是在原本的大模型之上又多加了一层 overhead。对于长链路 coding 任务，比较合适的比例大致是：每 8-15 步 executor 推进，触发 1 次 advisor 调用。

---

## 实现草图

最简单的版本就是一层 prompt + 模型路由：

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

真实实现要细致得多（如何组织 advisor 的 prompt、如何把指导意见注入而不让 executor 困惑、什么时候允许 executor 忽略 advisor 的坏建议），但骨架就是这么干净。

---

## 这件事告诉我们的 Agent 设计原则

Advisor Strategy 只是一个更普遍原则的一个具体实例：**异构路由优于同构部署**。

2023 年时，"全用 GPT-4"是合理的做法，因为模型之间的能力差距巨大，而 latency 和 cost 不那么重要。随着生态成熟：

1. 小模型在机械执行上的能力**已经强了非常多**
2. 在**具体子任务**上的能力差距，比在**通用智能**上的差距收敛得更快
3. 生产规模下的成本压力是真实存在的

这意味着真正该问的问题不是"我应该用哪个模型？"，而是"什么样的路由逻辑能在**当前任务形态**下给我最好的 result-per-dollar？"

Advisor Strategy 是这个问题在长链路 agent 任务上最简单的一个答案。但同样的思路也适用于：

- **检索路由**：什么时候用 dense search、什么时候用 sparse、什么时候用 reader model
- **验证路由**：什么时候跑一个独立的 critic 模型、什么时候让模型自我批评
- **模态路由**：什么时候用 vision、什么时候直接解析文本描述

---

## 一个被低估的点：跨环境一致性

成本-性能的讨论里经常会忽略一件事：**在不同环境下的一致性，对生产可靠性来说才是真正重要的指标**。

一个在 benchmark A 上 75%、在 B 上 70% 的模型，比一个在 A 上 85%、在 B 上 45% 的模型更可部署——即使两者均值相近。高方差意味着你**无法预测**它什么时候会翻车。

Advisor Strategy 倾向于降低方差，因为 advisor 在系统里扮演了"规划稳定器"的角色。executor 可能会因为环境特定的怪癖走出不同的路径，但顶层 plan 保持一致。

这个特性在单一 benchmark 数字里很难量化，但当你把同一个 agent 跑在不同代码库、不同 OS、不同工具配置下时，就会明显感受到。

---

## 一些现实约束

这套策略不是魔法：

- **Latency**：advisor 调用会引入额外的 round-trip。对实时性场景来说这是个问题。
- **Advisor prompt 质量**：garbage in, garbage out。advisor 注入的指导必须以一种 executor 能直接行动的格式给出。
- **升级阈值的标定**：阈值过低，你只是在花大钱买不到好处；阈值过高，executor 又会孤军奋战做出糟糕决策。
- **任务形态依赖**：对于**短任务**（< 10 步），advisor 路由的 overhead 通常不划算，直接用大模型就行。

---

## 更大的图景

我们正在进入这样一个阶段：相比于"该用哪个模型？"，"如何**组合**模型？"才是更值得问的问题。

Advisor Strategy 是这个问题在长链路 agentic 任务上一个简单、低 overhead 的答案。原理本身并不新颖——人类一直在这么做（junior 干活、senior 在关键决策点把关）——但只有当模型在机械执行上真正足够好之后，这套思路才能在 LLM 系统里实际跑通。

我认为接下来 12 个月会涌现出更多类似的范式：把不同的模型当作专精化的组件来路由，而不是当作可以互换的工具。

---

*数据引自 Anthropic 及第三方的公开 benchmark 披露。文中数字来源于撰写时已发布的公开资料。*

*[Read in English →](/2026/05/30/advisor-strategy-agent-cost/)*
