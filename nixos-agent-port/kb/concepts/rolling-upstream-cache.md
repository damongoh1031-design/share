# 对接"名字会滚动"的上游：缓存六件套

> **TL;DR** 当上游的资源名带一个**单调递增的代数**（Hydra 的 `latest-<gen>-...`、
> API 的 `v<N>`、镜像的 `latest-<build>`）时，缓存不能是简单的"取一次存起来"。
> 要处理六种真实故障：**代数计数器解析、失败冷却、rollover 重检、fallback 永不 memoize、
> 名字与计数分离、并发锁**。这套东西跟具体领域无关，任何对接会滚动上游的项目都能直接搬。

标签：`mcp-design` `caching` · 证据等级：`A`（源码直读）

## 问题

上游用"别名 + 代数计数器"发布资源：

```
latest-48-nixos-25.11
latest-50-nixos-unstable
latest-51-group-manual
```

每次上游发布新一批数据，就**递增代数并原子重定向别名**。老代数**会被退休**
（退休后请求 404）。

天真实现的四种崩法：

| 天真做法 | 怎么崩 |
|---|---|
| 硬编码别名 | 上游一退休就 404，**每次查询都失败** |
| 取一次永久缓存 | 上游滚动了，进程还钉在旧数据上 |
| 发现失败就无限重试 | 上游抖动时，所有并发调用者排队各等一次超时 |
| 把 fallback 结果也缓存 | 一次抖动换来**长期**的降级数据 |

## 模式：六件套

### ① 代数计数器解析（不硬编码）

```
^latest-(\d+)-<resource>$      ← 捕获组就是代数
```
**代数最大的就是最新。** 不写死数字，写解析规则。

> 例子（`mcp-nixos`）：`_ALIAS_RE = ^latest-(\d+)-nixos-(unstable|\d+\.\d+)$`。
> 还有第二个别名（flake 索引）用同一个探测发现，因为它的旧代数也会被退休。

### ② 失败冷却

探测失败后，**在 N 秒内不再探测**。

> 例：`_DISCOVERY_RETRY_COOLDOWN = 30.0`。没有它，一次上游抖动会让每个并发调用者
> 各排一次 10 秒超时 —— 因为 fallback 结果**故意不缓存**（见 ④）。

### ③ rollover 重检（区分"没有"和"还没填"）

上游发布是**两阶段**的：先建别名，再往里填数据。所以会观察到"别名存在但为空"的窗口。

- 空别名 ≠ 探测失败 → 不该当候选
- 空别名的结论**要过期** → 否则进程永远钉在旧代数

> 例：`_ROLLOVER_RECHECK = 300.0`。源码注释："An alias observed empty means Hydra is
> mid-publish. Counts — and the resolution derived from them — are a snapshot of that window,
> so they expire."

### ④ fallback 永不 memoize

这是最关键、最反直觉的一条。

| | 缓存？ | 为什么 |
|---|---|---|
| 发现成功的结果 | ✅ | 正常路径 |
| **fallback / 降级结果** | ❌ | 退休别名会 404；缓存降级数据 = 把一次抖动放大成长期故障 |

**代价**：上游持续故障时，每次调用都要重试一次探测。**用 ② 的冷却来限制这个代价**，
而不是缓存降级结果。

> 源码注释原文："The cache therefore **never memoizes a fallback result** — it retries
> discovery on the next call — so this map only has to cover a single request during an
> upstream blip."（即 fallback 表只需要覆盖"一次请求"的窗口）

### ⑤ 名字与计数分离

"这个资源叫什么"和"它里面有多少条"是两件事，**缓存也要分开**。

> 例：`alias_names`（解析必需）vs `available_channels`（仅展示）。
> 源码注释："A partial `_count` failure must not shrink the set of channels we can resolve."
> —— 展示用的计数失败，不该让解析能力缩水。

### ⑥ 并发锁 + 把结论穿过返回值

工具调用通常跑在线程池里（`asyncio.to_thread`），**首请求会并发竞争**。

- 加锁保证"填充决策"原子
- **但不要把"是否在用 fallback"放在共享状态里** —— 一个调用者的结论不该影响另一个

> 源码注释："the fallback verdict is threaded through return values rather than shared state
> so one resolution cannot act on another's outcome."

## 一个相关的坑：revision 有两种可信度

同一个"当前版本"可能有**两种来源**，可信度不同，回执里要**分开标注**：

| 标签 | 含义 | 能拿来干什么 |
|---|---|---|
| `indexed` | 数据就是从这**这个** commit 构建的 | ✅ 可以安全地与其他数据对比 |
| `branch_head` | 上游分支当前 HEAD（best-effort 抓取） | ⚠️ 只是指针，**可能领先索引若干 commit** |

**别把"分支尖"当成"数据版本"。** 回执里要写清是哪种。

## 通用检查清单

给任何"上游会滚动"的项目做缓存时问：

1. 资源名里有没有单调递增的部分？我是在**解析**它还是**硬编码**它？
2. 探测失败后有没有冷却？
3. 有没有"资源存在但内容为空"的中间态？它的结论会过期吗？
4. 降级结果被缓存了吗？（**如果有，这是最严重的 bug**）
5. "标识"和"元数据"的缓存是一起失效的吗？（不该是）
6. 首请求并发时会竞争吗？
7. 回执里区分了"精确来源"与"best-effort 来源"吗？

## 相关

- [mcp-envelope-protocol](./mcp-envelope-protocol.md)
