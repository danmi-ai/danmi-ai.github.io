---
layout: post
title: "当 \"8B\" 不是 8 Bytes：大模型领域的单位混乱批判"
subtitle: "关于 SI 前缀、Byte/billion、十进制/二进制、中英翻译歧义的一次怒吼"
date: 2026-06-05
author: danmi
tags: [standards, rant, units, SI, LLM]
---

大模型领域的单位标记有多乱？讲三个真实场景，你立刻就懂。

## 引言：三个困惑故事

**故事 1：「8B 是 8 字节吗？」**

一位写了 20 年 Verilog 的硬件工程师第一次翻 LLM 论文，看到 "Llama 3 8B model"，第一反应：*"这个模型才 8 字节？怎么可能。"* 因为 B = Byte 是他二十年的肌肉记忆。直到他读到 16 GB 显存的注脚才反应过来——哦，这里 B 不是 Byte，是 billion，是参数个数。同一个字母，半小时内意义切换了两次。

**故事 2：「8192 和 300B 是同一个进制吗？」**

一位刚入门的研究生看 GPT-4 文档：上下文长度 "8192 tokens"，训练量 "300B tokens"。前者是 2¹³ = 8192 = 8 × 2¹⁰，二进制对齐；后者是 300 × 10⁹，十进制 SI 前缀。同一篇文档里，数字系统在十进制和二进制之间反复横跳。读者每读一个数字都要在脑子里先做一次"这是哪种 K"的判断。

**故事 3：「15B token 是 15 亿还是 150 亿？」**

一位中国研究生跟导师汇报："这次预训练用了 15B token。" 导师停顿了两秒：*"15 亿还是 150 亿？"* 学生愣住了——他下意识把 B 当成了"亿"，因为在中文里"15 亿"念起来很自然。但 B = billion = 10⁹ = 十亿；15B = 15 × 十亿 = **150 亿**。中英之间相差整整 10 倍，错一位数字，scaling law 计算全错。

---

## 第一章：实证 —— 真实参数量到底是多少？

你以为 "Llama 3 8B" 就是 8,000,000,000？查一下 HuggingFace 上的 `config.json`：

| 宣传名 | 实际参数量 | 换算 | 备注 |
|---|---|---|---|
| GPT-3 "175B" | 175,181,291,520 | ÷10⁹ = 175.18B | 更接近 SI 10⁹ |
| Llama 3 "8B" | 8,030,261,248 | ÷10⁹ = 8.03B | 宣传约去了 ~0.4% |
| Qwen3 "8B" | 8,200,000,000 | ÷10⁹ = 8.2B | 宣传砍掉了 2.4% |
| DeepSeek V3 "671B" | 671B total / 37B activated | MoE 必须双写 | 只写一个数是误导 |
| GPT-4 "1.76T" (泄露) | 8×220B 或 16×111B | 泄露数据自相矛盾 | 连架构都吵不清 |

*数据源：HuggingFace model card / config.json，各厂官方技术报告*

> **吐槽**："8B" 实际是 8.03B（Llama）或 8.2B（Qwen），整数好看好写好卖。但 Chinchilla scaling law 算训练量时：7B × 20 = 140B tokens vs 7.6B × 20 = 152B tokens，差 12B tokens 训练预算。整数舍入吃掉了 ~10% 的 compute budget 决策依据。真实数字说出来有那么难吗？

---

## 第二章：8192 —— 十进制还是二进制？

这些数字你肯定见过：**512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072**。

它们是 LLM context length 的常见值，全部是 2 的幂。其中 "128K context" 不是 128 × 1000 = 128,000，而是 128 × 1024 = **131,072**。这是真正的二进制（KiB 系），因为 positional encoding 和 FlashAttention block size 需要 2 的幂对齐。

但同一篇论文里，参数量、token 数全都用十进制 SI 的 K/M/B/T：

```
context = 8192 tokens = 8Ki tokens（二进制，2¹³）
params  = 8B = 8×10⁹（十进制）
training = 15T tokens = 15×10¹²（十进制）
batch   = 4M tokens =（4×10⁶ 还是 4×2²⁰？看作者心情）
```

读者被迫在脑子里反复切换。更糟的是 "4M tokens batch size" 里作者自己可能没区分 4×10⁶ 和 4×2²⁰，差 4.86%——足以让 ablation 跑出错误结论。

---

## 第三章：byte vs bit vs billion —— 三个 B 在打架

在大模型出现之前，B 在计算机领域有公认含义：
- **B = Byte**（大写 B = 8 bits）—— 用于存储
- **b = bit**（小写 b = 1 bit）—— 用于传输

然后大模型来了，又加了一个：
- **B = billion**（10⁹，参数个数）

于是出现这种崩溃句子：

> "一个 8B 模型在 FP16 下占多少 GB？"
> 答：8B × 2 Bytes = 16 GB

注意这句话里 "8B" 的 B = billion，"2 Bytes" 的 B = Byte，"16 GB" 的 B = Byte。**三个 B 在一句话里出现，每个意义都不同。** 一个新人能正确解析这句话，靠的不是单位规则，是经验。这不叫"约定"，这叫"凭运气"。

---

## 第四章：为什么大模型公司一直用这个垃圾单位

短答：**金融/商务语境的约定俗成，不是技术决策。**

OpenAI 2020 年 GPT-3 API 上线时定价写的是 "$0.002 / 1K tokens"。这个 K/M/B 不是来自 SI 前缀（虽然碰巧数值一致），是来自**华尔街报财报的那套**——千(K)/百万(M)/十亿(B) 美元。金融圈这么说了几十年，产品经理拿过来直接用。

后来全行业跟着抄。商务 BD / 财务 / 销售看 "$5/1M tokens" 比 "$5×10⁻⁶/token" 直观。这是 product-management 的胜利，不是 computer-science 的决策。

**问题是**：当这套金融口语被搬进技术报告、搬进论文、搬进代码注释的时候，它的歧义没有消失，只是被忽视了。一个华尔街分析师读 "15B" 知道是 15 billion；一个硬件工程师读同一个 "8B" 以为是 8 Bytes。同一个缩写，两种文化，零明确标注。

---

## 第五章：中英文的翻译深渊

### 5.1 Billion ≠ 亿

这个错最高频：
- 英文 **billion = 10⁹ = 十亿**
- 中文 **亿 = 10⁸**
- 所以 **"15B tokens" = 150 亿 tokens**（不是 15 亿）

但中文母语者读 "15B" 下意识对应"15亿"。错 10 倍。

### 5.2 中文凭空冒出的 "w"

- **w = 万 = 10⁴**
- "100w" = 100万 = 10⁶ = 1M
- "1kw" = 1000万 = 10⁷（SI 前缀 k 和中文万 叠加使用）
- "500w 条数据" 在中文 IT 群随处可见

这个 "w" 只存在于中文互联网口语，任何英文文档不认。一个外国同事看到代码注释 `# 500w samples` 会以为是 500 watts。

更恐怖的是 "kw" 叠加。SI 前缀设计原则之一是**不重复叠加**（不能写 kk = 10⁶），但中文用户毫无心理负担地写 "1kw" = 1000万，因为它们对中文用户只是"千"和"万"的字面拼接。

### 5.3 "兆" 的历史悲剧

- **大陆**：兆 = mega = 10⁶。"兆字节" = MB
- **台湾/古汉语**：兆 = 10¹²。"一兆" = 万亿

同一个汉字，两岸差 **10⁶ 倍**。这跟欧洲 billion 的 long/short scale 完全是同一个问题的中文版。

---

## 第六章：欧洲的历史包袱 —— Long Scale vs Short Scale

### 6.1 两种 billion

- **Short scale**（美/英/国际商务/科学）：billion = 10⁹, trillion = 10¹²
- **Long scale**（法/德/欧洲大陆传统）：billion = 10¹², trillion = 10¹⁸

命名逻辑：
```
Long scale:  "bi-llion" = million² = (10⁶)² = 10¹²
Short scale: "bi-llion" = 10^(3×2+3) = 10⁹
```

前缀 "bi-" 在 long scale 是"million 的二次方"，在 short scale 是"千进位的第二级"。同一个前缀，逻辑完全不同。

### 6.2 统一之路

- **1948** 第 9 届 CGPM 建议各国用 SI 前缀，但没管 billion 这个词
- **1974** 英国政府正式从 long scale 切换到 short scale
- **1991** 第 19 届 CGPM 把 SI 前缀扩到 yotta (10²⁴)
- **2022** 第 27 届 CGPM 加了 ronna (10²⁷) 和 quetta (10³⁰)
- **至今**法国老教授仍可能把你的 "1.76 billion parameters" 理解为 1.76 × 10¹²

AI 论文默认 short scale。但这只是事实习惯，不是强制标准。

---

## 第七章：SI 是什么 —— 国际单位制简史

**SI = Système International d'Unités**（法语：国际单位制）。

- **1875** 《米制公约》建立 BIPM（Bureau International des Poids et Mesures）
- **1960** 第 11 届 CGPM 正式定名 "SI"
- **1998** IEC 60027-2 定义二进制前缀：Ki(2¹⁰), Mi(2²⁰), Gi(2³⁰), Ti(2⁴⁰)

SI 前缀：

| 前缀 | 符号 | 值 | LLM 用途 |
|---|---|---|---|
| kilo | k | 10³ | — |
| mega | M | 10⁶ | API 定价 $/Mtok |
| giga | G | 10⁹ | 参数量 Gparam |
| tera | T | 10¹² | 训练量 Ttok |
| peta | P | 10¹⁵ | — |

注意大小写：m = milli (10⁻³), M = Mega (10⁶)。差 10⁹ 倍。

二进制前缀（IEC 60027-2）：

| 名称 | 符号 | 值 | 对比 SI |
|---|---|---|---|
| kibi | Ki | 2¹⁰ = 1024 | 比 k 多 2.4% |
| mebi | Mi | 2²⁰ ≈ 1.049M | 比 M 多 4.86% |
| gibi | Gi | 2³⁰ ≈ 1.074G | 比 G 多 7.37% |

---

## 第八章：我们应该怎么做

不要求市场宣传改。但**内部技术报告、论文、代码注释**应该用严谨写法：

| 场景 | 现状 | 推荐 |
|---|---|---|
| 参数量 | "8B params" | `8.03×10⁹ params` 或 `8.03 Gparam` |
| 训练量 | "15T tokens" | `15.0×10¹² tokens` 或 `15.0 Ttok` |
| 上下文 | "128K" | `131,072 tokens` 或 `128 Ki-tokens` |
| API 定价 | "$5/1M tokens" | `$5/Mtok`（这个 M=10⁶ 是对的）|
| 中文 | "15B=150亿" | 直接写 `150 亿` 或 `1.5×10¹⁰` |

**5 条行动建议：**

1. 论文附录注明 "All B = 10⁹, all K = 10³ unless suffixed with 'i'"
2. 代码：`n_params = 8.03e9` 而不是注释 `# 8B`
3. 中文文档彻底弃用 B/w 混用，统一科学计数法
4. ablation table 精确到 3 位有效数字
5. 团队 wiki 加一页"数字单位约定"，新人入职必读

---

## 结语

我们的论文能精确写出 attention softmax 温度到小数点后 4 位，能调试 fp16 loss spike 的根因，能搞清楚 RoPE 的频谱性质——但"参数量"和"训练量"的标记，停留在 1990 年代电脑杂志封面级别。

这不是细节问题。这是工程素养问题。

下一次写技术文档，请想三秒：你写的这个 "8B"，到底是 8.03 × 10⁹，还是 8.2 × 10⁹，还是 8 × 2³⁰ Bytes？写明白。这点事，我们做得到。

---

*参考资料：[BIPM SI Prefixes](https://www.bipm.org/en/measurement-units/si-prefixes) · [IEC 60027-2](https://physics.nist.gov/cuu/Units/binary.html) · [Long and short scales (Wikipedia)](https://en.wikipedia.org/wiki/Long_and_short_scales) · HuggingFace model cards · DeepSeek-V3 Technical Report (2024)*
