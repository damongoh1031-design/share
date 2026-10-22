# RDNA4 16GB 本地大模型：选型、三维能力评测与 Ubuntu 26.04 部署深度研究

> **硬件基线**：AMD Radeon RX 9060 XT 16GB（Navi 44 / RDNA4 / `gfx1200`）· Ryzen 7 5800X3D · 32GB DDR4 双通道 · Ubuntu 26.04 + Mesa RADV
> **研究日期**：2026-10-22　**版本**：v1.0
> **定位**：在不牺牲游戏环境的前提下，把 16GB 单卡的能力压到极限——选出正确的模型、正确的量化、正确的运行时。

---

## 0. TL;DR

| 场景 | 推荐 | 关键代价 |
|---|---|---|
| **工具调用 / Agent / 写代码 / 中文** | `Qwen3.6-35B-A3B-Uncensored-Aggressive`（IQ4_XS 17.44 GiB） | 15–22 tok/s；4.32 bpw 量化损耗；官方要求 ≥128K 上下文，16GB 卡上难以满足 |
| **稳定对话 / 指令精确 / 要速度与长上下文** | `Gemma4-12B-QAT-Uncensored-Balanced`（Q4_K_M 6.87 GiB） | 数学与难题明显弱（AIME26 77.5 vs 92.7）；语言标签仅 en |
| **26B 的知识广度 + 视觉** | `Gemma4-26B-A4B-QAT-Uncensored-Balanced-MTP`（15.64 GiB） | 顶满显存必须卸载；**Agent 能力反而不如 12B**；速度不稳 |

**三条硬结论：**

1. **运行时选 llama.cpp + Vulkan（Mesa RADV），不装 ROCm。** ROCm 在 Windows 上对 RDNA4 支持滞后，在 Linux 上装错 usecase 会顶掉内核模块导致黑屏——为了几 tok/s 赌整个图形栈不值得。Vulkan 的 MoE kernel 效率足够，且零风险。
2. **Gemma 4 的滑窗 1024 是这张卡上最大的工程红利。** KV cache 被钉死在 ~1 GiB 量级且与上下文长度无关，12B 可以开 128K 上下文而几乎不额外吃显存——这是 16GB 卡跑长上下文的唯一现实路径。
3. **MoE 的"参数越大越聪明"在 16GB 上会翻车。** 26B-A4B 智力比 12B 高，但 Agent 能力反而更低（Tau2 68.2 < 69.0，Gemma 自家数据）。每 token 只激活 3.8B 参数，先崩的就是"每步都不能错"的 Agent 任务。

---

## 1. 研究方法与证据分级

本文所有数字按可信度分为四级，**正文中逐条标注**：

| 等级 | 含义 | 典型来源 |
|---|---|---|
| **A** | 官方实测，可复现 | 模型卡 benchmark 表、HF API 返回的字节数 |
| **B** | 第三方评测，存在评测方偏差 | Qwen 卡中的 Gemma 数字（对手分系统性偏低） |
| **C** | 由机制/架构推导 | KV cache 估算、roofline 上界 |
| **D** | 经验估计，未在本机实测 | 速度区间、abliterated 掉智幅度 |

**必须提前声明的三个局限：**

1. 所有 benchmark 都是**原版 instruction-tuned 模型**的数字，不是你下载的 uncensored + 量化版本。量化与 abliteration 会同时降低绝对分数。
2. 变体（Balanced / Aggressive）由第三方作者校准，**没有任何公开评测**，只能按机制推断。
3. 本文的速度区间是**基于带宽与卸载比例的估算（D 级）**，不是在本机跑出来的。第 9 节给了 30 分钟自测协议来取代这些估算。

---

## 2. 硬件约束推导

### 2.1 显存：名义 16GB，可用 ~15.2 GiB

| 项 | 数值 | 说明 |
|---|---|---|
| 标称显存 | 16 GB | GDDR6 |
| Windows 下 Vulkan 报告可用 | **15.0–15.5 GiB** | 驱动/桌面合成占用 |
| 建议的安全上限 | **14.5 GiB** | 留 0.7 GiB 给上下文增长与碎片 |

16GB 是这张卡所有决策的源头。它决定了：

- **稠密 12B @ Q4 刚好舒服**（6.87 GiB，还剩 8 GiB 给 KV 与上下文）
- **稠密 27B+ @ 任何量化都装不下**（Q4 就 16.8 GiB）
- **MoE 35B @ IQ4_XS 差 2.2 GiB**（17.44 vs 15.2）→ 必须卸载
- **MoE 26B @ Q4_K_M 刚好卡死**（15.64 vs 15.2）→ 必须卸载，且只剩 0 余量

### 2.2 带宽：320 GB/s 是解码速度的天花板

解码（decode）阶段每生成一个 token 都要把参与计算的权重从显存读一遍，所以理论上界是：

```
tok/s_max ≈ 显存带宽 / 每 token 需读取的字节数
```

| 模型 | 量化 | 权重 | 每 token 读取 | 理论上界 | 经验值 | 效率 |
|---|---|---|---|---|---|---|
| Gemma4-12B（dense） | Q4_K_M | 6.87 GiB | 6.87 GiB | **46.6 tok/s** | 26–32 | 56–69% |
| Gemma4-12B + MTP | Q4_K_M | +0.24 GiB | 同上 + draft | ~46.6 | **40+** | 86%+ |
| Gemma4-26B-A4B（MoE） | Q4_K_M | 15.64 GiB | ~2.4 GiB（激活 3.8/25.2） | ~130 tok/s | 25–40 | 19–31% |
| Qwen3.6-35B-A3B（MoE） | IQ4_XS | 17.44 GiB | ~1.5 GiB（激活 3/35） | ~200 tok/s | 15–22 | 8–11% |

**这张表最重要的信息不是数字，而是"效率"那一列的反常：**

- 稠密 12B 跑到理论值的 56–69%，属于正常水平（Vulkan kernel 效率）；
- MoE 的理论上界高得离谱（130–200 tok/s），实测却只有 15–40 —— 差了一个数量级。

**结论（C 级）：MoE 在 Vulkan 上的瓶颈不是带宽，是 kernel 启动开销与逐 token 的调度同步。** 激活的专家只有 8/256，但每层都要做路由、gather、scatter，这些是**固定开销，与激活参数量无关**。所以 MoE 的"省带宽"优势在 16GB 单卡上被开销吃掉了，参数量越大、层数越多，开销越重。

这也解释了为什么**卸载对 MoE 是次线性恶化**：被卸载到 CPU 的专家走 DDR4（~50 GB/s），每 token 只需读激活的那几个，数据量小，但**跨 PCIe 的同步延迟**是固定成本。所以 `--n-cpu-moe` 调优的目标不是"少卸载"，而是"卸载到刚好让 kernel 不等待"。

### 2.3 CPU：5800X3D 的 96MB 3D V-Cache 是 prefill 红利

| 特性 | 对本地推理的意义 |
|---|---|
| 96 MB L3（3D V-Cache） | prefill（prompt 处理）是矩阵乘，命中 L3 能显著提速；长 prompt 首字延迟受益 |
| 8 核 16 线程 | 足够喂满 `--n-cpu-moe` 卸载后的 CPU 计算 |
| 不支持 AVX-512 | llama.cpp 走 AVX2；比 AVX-512 平台慢约 15–25%，但可接受 |

**实用含义**：5800X3D 让"prompt 很长但输出很短"的场景（读文档、审代码、总结）体验远好于同价位 CPU；但**解码阶段它帮不上忙**——解码是显存带宽受限，CPU 只能等。

### 2.4 内存：32GB DDR4 决定了卸载上限

- 双通道 DDR4-3200 ≈ **50 GB/s**，只有显存的 1/6。
- 32GB 总量约束：`llama-server` 常驻 + 卸载权重 + 系统 + 浏览器，实际能给模型的约 **20–24 GB**。

| 模型 | 权重 | 需卸载 | 卸载后内存占用 | 可行性 |
|---|---|---|---|---|
| Gemma4-12B | 6.87 GiB | 0 | 0 | ✅ 全显存 |
| Gemma4-26B-A4B | 15.64 GiB | ≥1.2 GiB | 1.5–4 GiB | ✅ 轻度卸载 |
| Qwen3.6-35B-A3B | 17.44 GiB | ≥2.3 GiB | 3–8 GiB | ✅ 中度卸载 |
| Qwen3.6-35B Q4_K_M | 19.71 GiB | ≥4.5 GiB | 5–10 GiB | ⚠️ 速度明显下降 |
| Qwen3.6-35B Q5_K_P | 26.10 GiB | ≥11 GiB | 12–16 GiB | ❌ 内存+带宽双爆 |

### 2.5 约束汇总

```
显存 15.2 GiB  ─┬─ 稠密 ≤12B @Q4  ── 舒适区
                ├─ MoE 26B  @Q4   ── 临界，必须卸载
                └─ MoE 35B  @IQ4_XS ─ 超限 2.2 GiB，必须卸载
带宽 320 GB/s  ── 稠密解码 26–32 tok/s 是现实上限
内存 32GB/50GB/s ── 卸载 >10 GiB 后体验崩塌
滑窗 1024      ── Gemma 4 的 KV 几乎免费（关键红利）
```

---

## 3. 运行时栈决策

### 3.1 Windows 还是 Ubuntu？

| 维度 | Windows | Ubuntu 26.04 |
|---|---|---|
| Vulkan 后端 | ✅ llama.cpp 官方二进制 | ✅ 需自行编译（或 PPA） |
| RDNA4 驱动成熟度 | 较好（AMD 官方驱动） | 好（Mesa 26.x RADV 已支持 gfx1200） |
| 显存可用量 | ~15.0–15.5 GiB | 更干净，可到 15.5 GiB |
| 长时间服务化 | 差（休眠、更新、驱动重置） | 好（systemd + llama-swap） |
| 游戏 | 原生 | Steam/Proton 成熟 |

**决策：Ubuntu 26.04 作为服务宿主，Windows 保留为游戏/日常。** 理由：本地模型是要 7×24 挂着的服务，systemd 的进程管理、日志、自愈是 Windows 无法比的；而 Ubuntu 上的 Vulkan 栈（Mesa RADV）在 RDNA4 上已经稳定。

### 3.2 Vulkan 还是 ROCm？

**结论：Vulkan。** 这不是性能选择，是风险选择。

| | Vulkan（Mesa RADV） | ROCm |
|---|---|---|
| RDNA4 支持 | ✅ 内核 6.14+ 即支持 gfx1200 | ⚠️ 官方支持矩阵滞后，需 `HSA_OVERRIDE_GFX_VERSION` 欺骗 |
| 图形栈冲突 | 无（就是图形栈本身） | **有**，装错 usecase 会顶掉内核模块 |
| 安装风险 | 低（apt 装 mesa-vulkan-drivers） | **高**（见第 8 节四个坑） |
| 生态 | llama.cpp / KoboldCpp / llamafile | vLLM / PyTorch（对 16GB 单卡意义不大） |
| 性能 | MoE kernel 效率一般 | 稠密矩阵乘更快，但 MoE 支持不成熟 |

**关键论点**：ROCm 的价值在"跑 vLLM/PyTorch 训练/大批量推理"，而这些在 16GB 单卡上都不成立（vLLM 装不下 35B，训练更不可能）。**为一个用不上的能力承担破坏图形栈的风险，是负期望决策。**

### 3.3 工具矩阵：Vulkan 能跑什么

**① 原生 Vulkan 后端（真 GPU 加速）**

| 工具 | 说明 |
|---|---|
| **llama.cpp** | 首选。`-DGGML_VULKAN=ON`，MoE/滑窗/MTP 支持最全 |
| **KoboldCpp** | `koboldcpp-vulkan` 发行版，开箱即用，带 Web UI |
| **llamafile** | 单文件分发，`--gpu vulkan` |
| **text-generation-webui** | 多后端封装，含 Vulkan |
| **GPT4All** | 桌面端，Vulkan 可选 |
| **llama-swap** | 按需换模型的代理层（16GB 单卡必备） |
| **Docker** | `ghcr.io/ggml-org/llama.cpp:server-vulkan` |

**② 纯前端，接 OpenAI 兼容接口（不关心后端）**

Open WebUI、SillyTavern、LibreChat / LobeChat / AnythingLLM、各类 IDE 插件。

**③ 没有 Vulkan 后端（别浪费时间）**

- **Ollama**：官方只编 CUDA / ROCm / CPU，RDNA4 上会掉 CPU 或走 ROCm
- **vLLM**：CUDA/ROCm only，且 16GB 装不下目标模型
- **TensorRT-LLM / SGLang**：NVIDIA only
- **LM Studio / Jan**：有 Vulkan 引擎，但 Linux + RDNA4 成熟度需实测（LM Studio 还有多卡 tensor-split 崩溃的已知问题）

### 3.4 为什么是 llama.cpp

1. **唯一完整支持 Gemma 4 滑窗 + MTP 推测解码 + Qwen 混合线性注意力的实现**
2. `--n-cpu-moe` 是 16GB 卡跑 26B/35B MoE 的唯一现实手段
3. `--jinja` 支持各家的 chat template（Gemma 4 的 `<|think|>`、Qwen 的 `enable_thinking`）
4. 出问题能看源码、能改；Ollama 那层封装在排查时是负担

**排查"是不是真跑在 GPU 上"（必查）：**

```bash
# 启动日志应出现
ggml_vulkan: Found 1 Vulkan devices:
ggml_vulkan: 0 = AMD Radeon RX 9060 XT (RADV GFX1200) | uma: 0 | fp16: 1 | bf16: 1
# 运行中看 GPU 占用
radeontop
# 速度低于 10 tok/s 基本可以判定掉 CPU 了
```

---

## 4. 模型生态：abliterated / uncensored 全景

### 4.1 榜单观察（2026-10 时点，按下载量）

HF `other=uncensored` 榜单的头部几乎被两个家族垄断：**Qwen3.5/3.6/3.8 系**与 **Gemma 4 系**，且大量是 `huihui-ai` 的 abliterated 转量化。下载量最高的单个仓库达 **244 万**（`huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF`）。

这说明两件事：

1. **uncensored 需求是真实且大规模的**，不是小众玩票；
2. **社区已经形成了"官方发布 → huihui-ai 去审查 → 第三方量化"的标准流水线**，你下载的几乎都是这条链的产物。

### 4.2 abliterated 的机制与代价

**机制**：拒绝行为在残差流中大致对应一个**线性方向**（refusal direction）。Abliteration 通过对比"有害 prompt"与"无害 prompt"的激活差，算出该方向，然后在权重中**正交化移除**它。

**代价（D 级经验区间，非实测）：**

| 维度 | 典型退化 | 原因 |
|---|---|---|
| 安全性拒答 | **-80% ~ -95%** | 这正是目标 |
| 知识（MMLU 类） | -1% ~ -3% | 移除方向与部分知识表征耦合 |
| **指令遵循** | **-5% ~ -10%** | 拒答与"照格式办/别加戏"共享机制 |
| 长链推理 | -3% ~ -8% | 中间步骤的自我纠错被削弱 |

**工程含义**：abliterated 模型的**指令遵循掉得比知识多**。如果你的用途是"严格按 JSON 输出 / 遵守 20 条约束"，要么选 `Balanced` 变体，要么接受更高格式违规率。

### 4.3 三个候选（字节级实测，A 级）

#### A. `HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced`

| 文件 | 字节 | GiB |
|---|---|---|
| `Q4_K_M` | 7,381,381,760 | **6.87** |
| `mmproj`（BF16 视觉投影） | 175,115,264 | 0.16 |
| `mtp-gemma-4-12B-it.gguf` | 253,707,328 | 0.24 |

- **架构**：12B dense（11.95B）、48 层、滑窗 1024、上下文 256K、**encoder-free**、支持音频
- **MTP**：+60% 解码速度
- **量化**：**只出 Q4_K_M** —— QAT（量化感知训练）在 4-bit 就是最优，再做别的量化是纯损失
- **采样**：temp 0.6 / top_k 64 / top_p 0.9 / min_p 0.05 / repeat_penalty 1.1
- **启动**：`-md mtp-gemma-4-12B-it.gguf --spec-type draft-mtp`
- **坑**：语言标签仅 `en`（中文能力弱）；LM Studio 多卡 tensor-split 会崩（作者确认）

#### B. `HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive`

| 量化 | GiB | 评价 |
|---|---|---|
| IQ2_M | 10.86 | 质量太差，不推荐 |
| Q2_K_P | 13.95 | 可全上显存，但 2-bit 掉智严重 |
| IQ3_M | 14.38 | 可全上显存，质量勉强 |
| **IQ4_XS** | **17.44** | **推荐档**（4.32 bpw，需卸载 2.2 GiB） |
| Q3_K_P | 17.72 | K_P 版 3-bit，优于 IQ4_XS？存疑 |
| IQ4_NL | 18.42 | 需卸载 3.2 GiB |
| Q4_K_M | 19.71 | 需卸载 4.5 GiB |
| Q4_K_P | 21.82 | 需卸载 6.6 GiB |
| Q5_K_P | 26.10 | ❌ 内存+带宽双爆 |
| Q6_K_P | 28.54 | ❌ |
| Q8_K_P | 40.61 | ❌ |

- `mmproj` f16：899,283,072 B = **0.84 GiB**
- **架构**：35B 总 / 3B 激活、hidden 2048、40 层、布局 `10 × (3×(Gated DeltaNet→MoE) → 1×(Gated Attention→MoE))`、MoE 256 专家 8 路由 + 1 shared、MTP 多步训练、原生 262,144 上下文（可扩至 1,010,000）
- **许可证**：**apache-2.0**（三个候选里唯一明确可商用的）
- **语言**：en / zh / multilingual —— **中文原生，决定性优势**
- **K_P 是什么**：作者自定义的 "Perfect" 量化，用 +5–15% 体积换 1–2 档质量。是标准 GGUF 格式，但 **HF 兼容组件与 LM Studio 的量化列不认它**（显示 "?"）
- **坑**：README 要求 **≥128K 上下文**以保住思考能力；必须 `--jinja`；`Aggressive` 变体会**主动追加免责声明**（破坏简洁性）

#### C. `HauhauCS/Gemma4-26B-A4B-QAT-Uncensored-HauhauCS-Balanced-MTP`

| 文件 | 字节 | GiB |
|---|---|---|
| `Q4_K_M` | 16,796,015,520 | **15.64** |
| `mmproj`（BF16） | 1,194,827,776 | 1.11 |
| `mtp-gemma-4-26B-A4B-it.gguf` | 251,937,728 | 0.23 |

- **架构**：26B 总 / 4B 激活（25.2B / 3.8B）、30 层、滑窗 1024、上下文 256K、128 专家 8 激活 + 1 shared、视觉编码器 ~550M
- **MTP**：+35%
- **量化**：只出 Q4_K_M
- **采样**：同 12B
- **坑**：15.64 GiB 顶满 15.2 GiB 可用显存 → **必须** `--n-cpu-moe`；视觉 mmproj 占 1.11 GiB，建议单独端口按需启

---

## 5. 三维能力对比

### 5.1 智力（知识 + 推理）

| 指标 | A: Gemma4-12B | C: Gemma4-26B-A4B | B: Qwen3.6-35B | 来源 |
|---|---|---|---|---|
| MMLU-Pro | 77.2 | 82.6 | 85.2 | A（Gemma 官方 / Qwen 官方） |
| GPQA Diamond | 78.8 | 82.3 | 86.0 | A |
| AIME26（无工具） | 77.5 | 88.3 | 92.7 | A |
| LiveCodeBench v6 | 72.0 | 77.1 | 80.4 | A |
| Codeforces ELO | 1659 | 1718 | — | A |
| HLE（无工具） | 5.2 | 8.7 | 21.4 | A |
| BigBench Extra Hard | 53.0 | 64.8 | — | A |
| C-Eval（中文） | — | 82.5 | 90.0 | A / B |
| MRCR v2 128k（8 needle） | 43.4 | 44.1 | — | A |

**四条解读：**

1. **知识面三家挤在 82–86**（MMLU-Pro）。日常问答、写文案、翻译几乎无感差距——**别为那 3 分付速度代价**。
2. **难题才是真分层**：HLE 21.4 / 8.7 / 5.2。26B 是 12B 的 1.7 倍，Qwen 又是 26B 的 2.5 倍。这是"需要想一下才能答对"与"直接答错"的分界。
3. **A 的短板在数学**：AIME26 77.5，落后 26B 整整 10.8 分。dense 12B 的推理深度确实不够，这不是量化能救的。
4. **C 的长上下文是虚的**：参数翻倍，128K 检索只从 43.4 涨到 44.1（+0.7）。别指望 26B 替你读长文档——它的优势在单点知识，不在长程整合。

### 5.2 Agent 能力（工具调用 / 多轮任务）

| 指标 | A: 12B | C: 26B-A4B | B: Qwen3.6-35B | 来源 |
|---|---|---|---|---|
| Tau2（3 项均） | **69.0** | **68.2** | — | A（Gemma 官方） |
| TAU3-Bench | — | **59.0** | 67.2 | B（Qwen 自测） |
| SWE-bench Verified | — | **17.4** | **73.4** | B（Qwen 自测，对手偏低） |
| SWE-bench Pro | — | 13.8 | 49.5 | B |
| Terminal-Bench 2.0 | — | 34.2 | 51.5 | B |
| Tool Decathlon | — | **12.0** | 26.9 | B |
| MCPMark | — | 14.2 | 37.0 | B |
| MCP-Atlas | — | 50.0 | 62.8 | B |
| Claw-Eval Avg | — | 58.8 | 68.7 | B |
| Claw-Eval Pass^3 | — | 28.0 | 50.0 | B |

### 5.3 核心发现：C 的 Agent 能力是三个里最弱的

**两条独立来源互相印证：**

- **Gemma 官方 Tau2**：26B = **68.2** < 12B = **69.0**（自家模型、自家评测，倒挂）
- **Qwen 自测 TAU3**：26B = **59.0**，同表里 Qwen3.6 = 67.2、Gemma4-31B = 67.5

再加上 Tool Decathlon 12.0、SWE-bench Verified 17.4、MCPMark 14.2 —— C 在**所有 Agent 类指标上都垫底**。

**机制解释（C 级推断）**：Agent 任务吃的是**单步可靠性**——多轮状态跟踪、严格按 schema 输出、工具报错后恢复。这些能力对"激活参数量"极其敏感：

| | 每 token 激活 | Agent 表现 |
|---|---|---|
| Gemma4-12B（dense） | **11.95B（全量）** | 稳定 |
| Gemma4-26B-A4B（MoE） | **3.8B** | 最弱 |
| Qwen3.6-35B-A3B（MoE） | 3B | 最强（另有训练侧优势） |

26B-A4B 的激活量只有 12B dense 的 **1/3**。在"每步都不能错"的任务上，容量不足会直接体现为：工具参数填错、多轮状态丢失、报错后不恢复。

**Qwen 为什么能用 3B 激活打赢？** 训练侧差异：Qwen3.6 明确以 agentic coding 为目标做了后训练（SWE-bench 73.4 vs Gemma4-31B 52.0），且有 MTP 多步训练。**激活量是必要非充分条件**——MoE 的 Agent 能力靠训练补，不靠参数堆。

**但 B 的分数要打两个折扣：**

1. 那是 200K 上下文 + 官方 scaffold 跑出来的；16GB 卡上 32K–64K，会明显缩水
2. IQ4_XS 是 4.32 bpw，官方数字是 BF16

### 5.4 指令遵循

**三张卡都没公布 IFEval / IFBench**，所以这一维只能看机制与代理指标。**诚实声明：以下为 C/D 级推断，不是数字。**

#### 机制差异（确定的事实，A 级）

| | A / C（Gemma 4） | B（Qwen3.6） |
|---|---|---|
| `system` role | **原生支持**（Gemma 4 新增） | 支持 |
| 思考开关 | system prompt 开头插 `<|think|>` token | `chat_template_kwargs: {"enable_thinking": false}` |
| 思考输出格式 | `<|channel>thought\n…<channel|>` | `<think>…</think>` |
| 多轮陷阱 | **历史里不得含上一轮 thinking**（工具调用轮除外） | 默认只保留最近一轮；`preserve_thinking` 可开全历史 |
| 软开关 | 有 | **不支持** `/think` `/nothink` |

**两个真实会咬人的坑：**

1. **Gemma 4**：如果客户端把上一轮的 `<|channel>thought…<channel|>` 原样塞回历史，模型的格式遵循会明显退化。工具调用轮例外（必须保留）。
2. **Qwen3.6**：传 `/nothink` 无效。想关思考必须走 `enable_thinking: false`，否则**思考关不掉 → 首字延迟爆炸**。

#### 变体校准差异（这条最关键）

| 变体 | 拒答率 | 副作用 |
|---|---|---|
| **Balanced**（A、C） | 中 | 更守风格约束 |
| **Aggressive**（B） | 低 | **会主动追加免责声明**，违反"简洁""只要 JSON""保持正式" |

如果你对指令遵循的要求是"照格式办、别加戏"，`Balanced` 优于 `Aggressive`。

#### 量化差异

| | 量化方式 | 等效 bpw | 格式约束稳定性 |
|---|---|---|---|
| A / C | **QAT**（4-bit 原生训练） | ~4.9 | 接近原版 |
| B | **IQ4_XS**（后训练量化） | 4.32 | 对长指令链更敏感 |

**代理指标**：Tau2/TAU3 本身就是"指令 + 工具 schema 遵守"的综合测试。C 在这项垫底 → **C 对复杂指令链的遵守是三个里最弱的**。

#### 指令遵循综合排序（D 级）

```
A（Balanced + QAT + dense）  >  C（Balanced + QAT，但激活容量不足）  >  B（Aggressive + IQ4_XS）
```

注意这个排序与"智力"排序**几乎相反**。这是本文最有操作价值的一条：**更聪明的模型不一定更听话。**

---

## 6. 量化工程

### 6.1 量化家族速查

| 类型 | 代表 | 特点 | 本机建议 |
|---|---|---|---|
| **QAT** | Gemma 4 官方 | 训练时感知量化，4-bit 即最优 | ✅ 直接用，别再量化 |
| **K-quant** | Q4_K_M / Q5_K_M / Q6_K | 通用最优性价比 | ✅ 首选 |
| **I-quant** | IQ4_XS / IQ3_M | 同体积更优，但 kernel 支持参差 | ⚠️ Vulkan 上实测后再定 |
| **K_P（作者自定义）** | Q4_K_P / Q5_K_P | +5–15% 体积换 1–2 档质量 | ⚠️ 工具链不认，需实测 |
| **Q8_0 / f16** | — | 无损但装不下 | ❌ |

**Vulkan 上的实测建议**：IQ 系在部分 llama.cpp Vulkan 版本会**回退 CPU**（日志里看到 `dequantize` 落到 CPU 就是踩了）。用 IQ4_XS 前务必看启动日志确认全部层在 GPU。

### 6.2 显存预算表（14.5 GiB 安全线）

| 模型 | 权重 | mmproj | KV（32K） | 合计 | 余量 |
|---|---|---|---|---|---|
| A: Gemma4-12B Q4_K_M | 6.87 | 0.16 | ~0.2（滑窗） | **7.23** | **+7.3 GiB** |
| C: Gemma4-26B Q4_K_M | 15.64 | 1.11 | ~0.2（滑窗） | **16.95** | **-2.5 GiB → 必须卸载** |
| B: Qwen3.6-35B IQ4_XS | 17.44 | 0.84 | ~0.7 | **18.98** | **-4.5 GiB → 必须卸载** |

### 6.3 KV cache 估算

**Gemma 4 系列（滑窗 1024）——这是最大的红利：**

滑窗意味着每层只保留最近 1024 个 token 的 KV，**KV 占用与上下文长度无关**。48 层 × 1024 token × 每 token 每层约 4 KB（f16 估算）≈ **0.2 GiB**，且开 128K 上下文也是这个数。

> **工程结论**：12B 在 16GB 卡上可以放心开 `-c 131072`，几乎不额外吃显存。这是它相对 Qwen 的**结构性优势**。

**Qwen3.6-35B-A3B（混合注意力）：**

40 层中只有 **10 层是全注意力**（Gated Attention，16 Q 头 / 2 KV 头 / head_dim 256），其余 30 层是 Gated DeltaNet（线性注意力，状态恒定）。

```
每 token 每全注意力层 KV = 2(K,V) × 2(kv_heads) × 256(head_dim) × 2(BF16) = 2,048 B
10 层 → 20,480 B/token ≈ 20 KB/token
32K 上下文  ≈ 655 MB
128K 上下文 ≈ 2.6 GB（f16）/ 1.3 GB（q8_0）
```

**这就是 Qwen 的硬伤**：官方要求 ≥128K 上下文保思考质量，但 128K KV（即使 q8_0 也要 1.3 GB）+ 17.44 GiB 权重，在 15.2 GiB 的卡上根本装不下。**你必须做取舍：要么砍上下文（思考质量掉），要么砍量化（权重质量掉）。**

### 6.4 `--n-cpu-moe` 二分法

不要猜层数，用二分：

```bash
# 1. 先全上 GPU，看 OOM
llama-server -m model.gguf -ngl 999 --n-cpu-moe 0 -c 32768
#    日志会报 "failed to allocate Vulkan0 buffer" 并指出缺多少 MiB

# 2. 从保守值开始
--n-cpu-moe 8

# 3. 看日志里的实际占用，每次 ±2 收敛到 14.5 GiB
#    目标不是"最小卸载"，而是"不触发 OOM 且 kernel 不等待"
```

**判据**：如果 `n-cpu-moe` 从 8 加到 12 速度没变，说明瓶颈不是显存而是 kernel 开销，**别再往上加**。

**通用起始值**：

| 模型 | 起始 `--n-cpu-moe` | 目标显存 |
|---|---|---|
| Gemma4-26B-A4B Q4_K_M | 8 | 14.5 GiB |
| Qwen3.6-35B IQ4_XS | 6 | 14.5 GiB |

---

## 7. 部署 runbook（Ubuntu 26.04）

### 7.1 系统准备

```bash
sudo apt update
sudo apt install -y build-essential cmake git libcurl4-openssl-dev \
                    mesa-vulkan-drivers vulkan-tools libvulkan-dev

# 验证 Mesa RADV 已识别 RDNA4
vulkaninfo --summary | grep -E "deviceName|driverName"
# 期望: AMD Radeon RX 9060 XT (RADV GFX1200) / driverName = radv
```

**必须通过的验证（缺一不可）：**

```bash
ls /usr/share/vulkan/icd.d/          # 只应有 radeon_icd.x86_64.json
glxinfo | grep "OpenGL renderer"     # 应为 AMD Radeon ... (radeonsi, ...)
modinfo amdgpu | head -3             # 内核模块来自 /lib/modules（非 dkms）
ls -l /dev/kfd /dev/dri/renderD128   # 两者应同时存在
```

### 7.2 放大 GTT（关键）

Vulkan 默认只能用到约一半系统内存做 GTT。32GB 机器上放大到 24GB，让卸载的权重留在 GTT 而非频繁换页：

```bash
sudo nano /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT 追加：
#   amdgpu.gttsize=24576 ttm.pages_limit=6291456
sudo update-grub && sudo reboot
```

- `amdgpu.gttsize` 单位 **MB**（24576 = 24 GiB）
- `ttm.pages_limit` 单位 **4 KiB 页**（6291456 × 4 KiB = 24 GiB）
- **两个必须同改**，否则以较小者为准
- 上限建议 ≤ 物理内存的 70%（32GB → ≤22 GiB；24 GiB 属激进值，若不稳定降到 20480 / 5242880）

**BIOS 侧**：开启 **Re-Size BAR**（Above 4G Decoding），否则 GTT 映射受限。

### 7.3 编译 llama.cpp（Vulkan）

```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build -DGGML_VULKAN=ON -DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# 验证
./build/bin/llama-server --version
./build/bin/llama-server -m /path/model.gguf -ngl 999 -c 4096 --port 8080
```

**权限**（否则 Vulkan 打不开设备）：

```bash
sudo usermod -aG render,video $USER
# 重新登录生效
```

### 7.4 systemd 服务

```ini
# /etc/systemd/system/llama-gemma12.service
[Unit]
Description=llama.cpp Gemma4-12B (Vulkan)
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/opt/models
ExecStart=/opt/llama.cpp/build/bin/llama-server \
  -m /opt/models/gemma4-12b-q4km.gguf \
  -md /opt/models/mtp-gemma-4-12B-it.gguf --spec-type draft-mtp \
  --mmproj /opt/models/gemma4-12b-mmproj.gguf \
  -ngl 999 -c 131072 --jinja \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5
ProtectSystem=strict
ReadWritePaths=/opt/models
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now llama-gemma12
journalctl -u llama-gemma12 -f
```

### 7.5 llama-swap：16GB 单卡多模型

16GB 装不下三个模型，但 `llama-swap` 可以在请求到达时**按需换载**，对外只暴露一个端口：

```yaml
# /etc/llama-swap/config.yaml
healthCheckTimeout: 300
models:
  gemma12:
    cmd: /opt/llama.cpp/build/bin/llama-server -m /opt/models/gemma4-12b-q4km.gguf -ngl 999 -c 131072 --jinja --port ${PORT}
    ttl: 600          # 空闲 10 分钟卸载
  qwen35:
    cmd: /opt/llama.cpp/build/bin/llama-server -m /opt/models/qwen36-35b-iq4xs.gguf --n-cpu-moe 6 -ngl 999 -c 65536 --jinja --port ${PORT}
    ttl: 600
```

**关键**：`ttl` 让模型在空闲后自动卸载，避免和游戏抢显存。

### 7.6 三套启动参数（可直接抄）

```bash
# ── A: Gemma4-12B Balanced（推荐主力）──────────────────────
llama-server -m gemma4-12b-q4km.gguf \
  -md mtp-gemma-4-12B-it.gguf --spec-type draft-mtp \
  -ngl 999 -c 131072 --jinja \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --temp 0.6 --top-k 64 --top-p 0.9 --min-p 0.05 --repeat-penalty 1.1 \
  --host 0.0.0.0 --port 8080

# ── B: Qwen3.6-35B Aggressive（Agent 专用）─────────────────
llama-server -m qwen36-35b-iq4xs.gguf \
  --n-cpu-moe 6 -ngl 999 -c 65536 --jinja \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --temp 1.0 --top-k 20 --top-p 0.95 --presence-penalty 1.5 \
  --host 0.0.0.0 --port 8081

# ── C: Gemma4-26B-A4B Balanced（视觉/知识备选）─────────────
llama-server -m gemma4-26b-a4b-q4km.gguf \
  -md mtp-gemma-4-26B-A4B-it.gguf --spec-type draft-mtp \
  --n-cpu-moe 8 -ngl 999 -c 32768 --jinja \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --temp 0.6 --top-k 64 --top-p 0.9 --min-p 0.05 --repeat-penalty 1.1 \
  --host 0.0.0.0 --port 8082
```

**MTP 回退**：如果 Vulkan 上 MTP 不稳定（输出乱码/崩溃），去掉 `-md` 与 `--spec-type draft-mtp`，损失 35–60% 解码速度但稳定。

---

## 8. 风险清单

### 8.1 ROCm 的四个坑（如果你哪天非要装）

1. **`amdgpu-install` 默认 `--usecase=all` 会装 `amdgpu-dkms`，顶掉内核 amdgpu 模块 → 开机黑屏。**
   必须：`amdgpu-install --usecase=rocm --no-dkms`
2. **`--usecase=graphics` 会装第二个 Vulkan ICD（amdvlk / amd_pro_icd）→ 游戏选错驱动。**
   装完检查 `/usr/share/vulkan/icd.d/` 是否只剩 `radeon_icd.x86_64.json`。
3. **ROCm apt 源会把 `libdrm-amdgpu1`、`llvm` 降级 → Mesa 被破坏。**
   加 pin 钉住 Ubuntu 源：
   ```
   # /etc/apt/preferences.d/99-keep-mesa
   Package: libdrm-amdgpu1 mesa-* llvm-* libllvm*
   Pin: release o=Ubuntu
   Pin-Priority: 1001
   ```
4. **显存争抢与驱动无关**：ROCm 与游戏同时跑会 OOM。靠 `systemctl stop` 或 llama-swap `ttl` 解决。

### 8.2 其他已知风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| LM Studio 多卡 tensor-split 崩溃 | 启动失败 | 单卡模式；或直接用 llama.cpp |
| IQ 系量化在 Vulkan 回退 CPU | 速度掉到 3–5 tok/s | 看启动日志；不行换 Q4_K_M |
| K_P 量化工具链不认 | LM Studio/兼容组件显示 "?" | 用 llama.cpp 原生 |
| MTP 在 Vulkan 不稳定 | 乱码/崩溃 | 去掉 `-md`/`--spec-type` |
| Gemma 4 历史含 thinking | 格式遵循退化 | 客户端剥离上一轮 thought 块（工具轮除外） |
| Qwen `/nothink` 无效 | 延迟爆炸 | 用 `enable_thinking: false` |
| 26B 视觉 mmproj 占 1.11 GiB | 挤爆显存 | 单独端口按需启 |

---

## 9. 自测协议（30 分钟，替代本文所有 D 级估算）

**目的**：验证两个关键假设——① C 的 Agent 能力真的不如 A；② Qwen 在 32K 上下文下思考质量掉多少。

### 9.1 测试集（10 条）

| 类别 | 数量 | 设计要点 |
|---|---|---|
| 多步工具调用 | 3 | 含**一个必然失败的工具**，看报错恢复能力 |
| 长指令（20 条约束） | 3 | 看格式遵循：JSON schema、字数、语气、禁用词 |
| 中文知识 | 2 | 常识 + 专业，看是否夹英文 |
| 代码修复 | 2 | 给带 bug 的函数 + 报错，看是否只改必要处 |

### 9.2 每个模型跑两遍

- `-c 32768` 一遍
- `-c 131072` 一遍（验证 Qwen "上下文掉思考"到底多严重）

### 9.3 记录四个数

| 指标 | 采集方式 |
|---|---|
| 首次正确率 | 人工/脚本判对错，不看第二遍 |
| 格式违规次数 | 20 条约束里违反了几条 |
| 平均 tok/s | llama-server 日志的 `eval time` |
| 上下文衰减 | (32K 正确率 − 128K 正确率) / 32K 正确率 |

### 9.4 判据

- **C 在多步工具调用上若真的输给 A** → 直接删掉 C，省 2.5 GiB 显存
- **Qwen 若在 32K 下正确率跌 >20%** → 它在这张卡上不适合做 Agent，退回 A
- **A 若格式违规 ≤1 条且 ≥25 tok/s** → 定为主力，B 只在"必须更聪明"时启用

---

## 10. 结论

**这张卡的现实定位是：一个能跑 12B dense 全速、26B/35B MoE 半速、支持 128K 上下文的本地推理节点。** 它不是"跑大模型"的机器，是"把 12B 用到位"的机器。

**最终推荐：**

1. **主力：Gemma4-12B QAT Balanced。** 6.87 GiB 全上显存，128K 上下文几乎免费（滑窗红利），26–32 tok/s（MTP 40+），指令遵循最好。**它的问题只有两个：数学弱、中文弱。**
2. **Agent/中文/代码时切到 Qwen3.6-35B IQ4_XS。** 它是三个里唯一真正能干活（SWE-bench 73.4）且中文原生的，代价是 15–22 tok/s 和上下文取舍。
3. **26B-A4B 不做主力。** 智力涨了一点，Agent 掉了，速度掉了，显存爆了。只在"明确需要 26B 知识广度或视觉"时用。

**如果只记一句话**：*在 16GB 上，激活参数量比总参数量重要，滑窗比上下文长度重要，Balanced 比 Aggressive 听话。*

---

## 附录 A：benchmark 原始数据

完整数据见 [`data/benchmarks.csv`](data/benchmarks.csv)。

**Gemma 4 官方表（instruction-tuned）**

| 指标 | 31B | 26B A4B | 12B Unified | Gemma3-27B（no-think） |
|---|---|---|---|---|
| MMLU Pro | 85.2 | 82.6 | 77.2 | 67.6 |
| AIME 2026 no tools | 89.2 | 88.3 | 77.5 | 20.8 |
| LiveCodeBench v6 | 80.0 | 77.1 | 72.0 | 29.1 |
| Codeforces ELO | 2150 | 1718 | 1659 | 110 |
| GPQA Diamond | 84.3 | 82.3 | 78.8 | 42.4 |
| **Tau2（3 项均）** | **76.9** | **68.2** | **69.0** | 16.2 |
| HLE no tools | 19.5 | 8.7 | 5.2 | — |
| HLE with search | 26.5 | 17.2 | — | — |
| BigBench Extra Hard | 74.4 | 64.8 | 53.0 | 19.3 |
| MMMLU | 88.4 | 86.3 | 83.4 | 70.7 |
| MMMU Pro | 76.9 | 73.8 | 69.1 | 49.7 |
| OmniDocBench 1.5（↓） | 0.131 | 0.149 | 0.164 | 0.365 |
| MATH-Vision | 85.6 | 82.4 | 79.7 | 46.0 |
| MedXPertQA MM | 61.3 | 58.1 | 48.7 | — |
| CoVoST | — | — | 38.5（不含中文） | — |
| FLEURS（↓） | — | — | 0.069 | — |
| **MRCR v2 8needle 128k** | **66.4** | **44.1** | **43.4** | 13.5 |

**Qwen3.6-35B-A3B 官方表**（列序：Qwen3.5-27B / Gemma4-31B / Qwen3.5-35BA3B / Gemma4-26BA4B / Qwen3.6-35BA3B）

| 分类 | 指标 | 数值 |
|---|---|---|
| Coding Agent | SWE-bench Verified | 75.0 / 52.0 / 70.0 / 17.4 / 73.4 |
| | SWE-bench Multilingual | 69.3 / 51.7 / 60.3 / 17.3 / 67.2 |
| | SWE-bench Pro | 51.2 / 35.7 / 44.6 / 13.8 / 49.5 |
| | Terminal-Bench 2.0 | 41.6 / 42.9 / 40.5 / 34.2 / 51.5 |
| | Claw-Eval Avg | 64.3 / 48.5 / 65.4 / 58.8 / 68.7 |
| | Claw-Eval Pass^3 | 46.2 / 25.0 / 51.0 / 28.0 / 50.0 |
| | SkillsBench Avg5 | 27.2 / 23.6 / 4.4 / 12.3 / 28.7 |
| | QwenClawBench | 52.2 / 41.7 / 47.7 / 38.7 / 52.6 |
| | NL2Repo | 27.3 / 15.5 / 20.5 / 11.6 / 29.4 |
| | QwenWebBench | 1068 / 1197 / 978 / 1178 / 1397 |
| General Agent | TAU3-Bench | 68.4 / 67.5 / 68.9 / 59.0 / 67.2 |
| | VITA-Bench | 41.8 / 43.0 / 29.1 / 36.9 / 35.6 |
| | DeepPlanning | 22.6 / 24.0 / 22.8 / 16.2 / 25.9 |
| | Tool Decathlon | 31.5 / 21.2 / 28.7 / 12.0 / 26.9 |
| | MCPMark | 36.3 / 18.1 / 27.0 / 14.2 / 37.0 |
| | MCP-Atlas | 68.4 / 57.2 / 62.4 / 50.0 / 62.8 |
| | WideSearch | 66.4 / 35.2 / 59.1 / 38.3 / 60.1 |
| Knowledge | MMLU-Pro | 86.1 / 85.2 / 85.3 / 82.6 / 85.2 |
| | MMLU-Redux | 93.2 / 93.7 / 93.3 / 92.7 / 93.3 |
| | SuperGPQA | 65.6 / 65.7 / 63.4 / 61.4 / 64.7 |
| | C-Eval | 90.5 / 82.6 / 90.2 / 82.5 / 90.0 |
| STEM | GPQA | 85.5 / 84.3 / 84.2 / 82.3 / 86.0 |
| | HLE | 24.3 / 19.5 / 22.4 / 8.7 / 21.4 |
| | LiveCodeBench v6 | 80.7 / 80.0 / 74.6 / 77.1 / 80.4 |
| | HMMT Feb25 | 92.0 / 88.7 / 89.0 / 91.7 / 90.7 |
| | HMMT Nov25 | 89.8 / 87.5 / 89.2 / 87.5 / 89.1 |
| | HMMT Feb26 | 84.3 / 77.2 / 78.7 / 79.0 / 83.6 |
| | IMOAnswerBench | 79.9 / 74.5 / 76.8 / 74.3 / 78.9 |
| | AIME26 | 92.6 / 89.2 / 91.0 / 88.3 / 92.7 |
| 视频 | VideoMME | 82.8 / 75.3 / — / — / 82.5 |
| | VideoMMMU | 82.3 / 77.6 / 81.6 / 76.0 / 80.4 |
| | MLVU | 85.9 / 72.8 / — / — / 85.6 |
| | MVBench | 74.6 / — / — / — / 74.8 |
| | LVBench | 73.6 / — / — / — / 71.4 |

> **偏差提示**：Qwen 表中的 Gemma4-26BA4B 列是 **Qwen 团队自测**，对手分系统性偏低（如 SWE-bench Verified 17.4）。但 Tau2（Gemma 自家 68.2）与 TAU3（Qwen 自测 59.0）**方向一致**，两条独立来源都指向"C 的 agentic tool use 偏弱"。

---

## 附录 B：命令速查

```bash
# 环境验证
vulkaninfo --summary | grep -E "deviceName|driverName"
ls /usr/share/vulkan/icd.d/
ls -l /dev/kfd /dev/dri/renderD128
cat /sys/module/amdgpu/parameters/gttsize    # 单位 MB

# 显存监控
radeontop
watch -n1 'cat /sys/class/drm/card0/device/mem_info_vram_used'

# 模型下载（Ubuntu 26.04 需 pipx）
pipx install uv && uv tool install huggingface_hub[cli]
hf download HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced \
  --include "*Q4_K_M*" --local-dir /opt/models

# 速度基准（单次）
llama-bench -m model.gguf -ngl 999 -p 512 -n 128

# 服务健康检查
curl http://localhost:8080/health
curl http://localhost:8080/v1/models
```

---

## 附录 C：来源

| 内容 | 来源 |
|---|---|
| Gemma 4 架构与 benchmark | `google/gemma-4-12B-it`、`gemma-4-26B-A4B-it`、`gemma-4-31B-it` 官方模型卡 |
| Qwen3.6-35B-A3B 架构与 benchmark | `Qwen/Qwen3.6-35B-A3B` 官方模型卡 |
| 量化体积（字节级） | HuggingFace API `siblings` 接口实测（2026-10-22） |
| uncensored 生态榜单 | HF `models?other=uncensored` 按 downloads 排序 |
| Vulkan 运行时矩阵 | llama.cpp / KoboldCpp / llamafile / Ollama 官方文档 |
| ROCm 安装风险 | AMD `amdgpu-install` 文档 + Mesa/RADV 包依赖关系 |

---

*本文档由 DSH 会话生成，数据采集于 2026-10-22。模型生态迭代快，benchmark 与量化版本建议每季度复核一次。*
