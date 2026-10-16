# 只用 proton-cachyos 能得到多少优化？Flatpak 下又损失多少？

- **调研日期**：2026-10-16
- **聚焦问题**：① 如果只是使用 Proton-CachyOS（作为自定义兼容工具），是否也能得到 CachyOS 的优化？② 在 Flatpak 下，游戏受影响多少？
- **承接**：`proton-games-optimization.md`（第十轮，Proton 游戏优化收益排序）
- **一句话结论**：
  - **① proton-cachyos 能带走「翻译层那一半」优化，而且不需要装 CachyOS** —— 官方直接发布 **`x86_64_v3` 变体的独立 tarball**，任何发行版丢进 `compatibilitytools.d` 即可。带不走的是**内核、Mesa/glibc、CachyOS-Settings**。
  - **② Flatpak 的代价不在「沙箱开销」（可忽略），而在「图形栈被 runtime 替换」** —— Flatpak Steam 用 runtime 自带的 Mesa 与 glibc，**不是宿主的**。所以在 CachyOS 上用 Flatpak Steam 会**丢掉 CachyOS 对 Mesa/glibc 的 v3/v4 优化**；但 `/dev/ntsync` 可用（manifest 含 `--device=all`），且可以把 v3 版 proton-cachyos 放进 Flatpak 的 compat tools 目录，把翻译层优化找回来。

---

## 一、问题 ①：proton-cachyos 拿到了什么，没拿到什么

### 1.1 决定性证据：官方发布 v3 变体的独立 tarball

GitHub release `cachyos-11.0-20261005-slr`（Version 11.0-20261005）的资产列表：

| 资产 | 说明 |
|---|---|
| `proton-cachyos-11.0-20261005-slr-x86_64.tar.xz` | 通用基线（x86-64 v1） |
| **`proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz`** | **x86-64-v3 优化构建（AVX2 等）** |
| `proton-cachyos-11.0-20261005-slr-arm64.tar.xz` | ARM64 |
| 各带 `.sha512sum` | 校验 |

README 明确："To install a local build of Proton into Steam, make a new directory in `~/.steam/root/compatibilitytools.d/` ... place the directory containing your redistributable build under that."

> **关键推论**：**不需要装 CachyOS 就能拿到 v3 优化的翻译层**。这是本次调研最实用的一条。注意官方只发 **v3** 变体（不发 v4）——因为 v4 要求 AVX-512，覆盖面太窄。

### 1.2 收益保留度

| 优化项 | 只装 proton-cachyos 后 | 说明 |
|---|---|---|
| **翻译层**（Wine / DXVK / vkd3d-proton 的 v3 优化构建） | ✅ **保留** | 官方 `_v3` tarball 自带 |
| Proton-CachyOS 补丁集（FSR4 自动升级 / Reflex / OptiScaler / per-game 着色器缓存 / UMU） | ✅ 保留 | 都在这个包里 |
| **CachyOS 内核**（BORE / EEVDF 调参 / 1000Hz / 补丁集） | ❌ 拿不到 | 需装 `linux-cachyos` 内核 |
| **Mesa / RADV 的 v3/v4 优化构建** | ❌ 拿不到 | **Proton 不打包 Mesa**，用宿主发行版的 Mesa |
| **NTSync** | ⚠️ 取决于宿主 | 需内核 ≥ 6.14 且加载 `ntsync` 模块 |
| **CachyOS-Settings**（sysctl / IO 调度器 / ZRAM / THP / `game-performance` 电源档） | ❌ 拿不到 | 发行版层 |
| **优化过的 glibc 等系统库** | ❌ 拿不到 | 宿主提供 |

**结论**：大约拿到**一半**——「翻译层」那一半（也是 Proton 场景的冠军项），拿不到「系统层」那一半。

---

## 二、问题 ②：Flatpak 下损失多少

### 2.1 先破除一个误解：沙箱本身的开销很小

Flatpak 用 **bubblewrap 命名空间隔离**，**不拦截系统调用**（只有 seccomp 过滤器，开销极小）。所以"沙箱导致掉帧"在机制上不成立。

> ⚠️ 诚实标注：**没有找到 Flatpak vs 原生 Steam 的公开对照基准**。"沙箱开销可忽略"是机制推断，不是实测结论。

### 2.2 真正的代价：你的图形/系统栈被换成了 runtime 版本

Flatpak 应用的依赖来自 **runtime**（`org.freedesktop.Platform`），**不是宿主**。实测清单可见：

```
Mesa  org.freedesktop.Platform.GL.default  25.1.7  24.08  system
```

也就是说 **Flatpak Steam 里的 Mesa 来自 `org.freedesktop.Platform.GL.default` 扩展，而不是宿主的 Mesa**；glibc 同理来自 `org.freedesktop.Platform`。

**后果**：

| 维度 | Flatpak Steam 下 | 影响 |
|---|---|---|
| Mesa / RADV | ❌ runtime 版本，**非宿主** | **在 CachyOS 上会丢掉 v3/v4 优化构建**；在滚动发行版上还可能**比宿主旧** |
| glibc | ❌ runtime 版本，非宿主 | 丢掉宿主的 v3/v4 优化 |
| NVIDIA 专有驱动 | ✅ 宿主提供 | GL extension 会挂载宿主的 nvidia 驱动 → N 卡受影响较小 |
| 内核（调度 / 内存 / NTSync 驱动） | ✅ 宿主内核 | CachyOS 内核的收益**保留** |
| 沙箱开销 | 可忽略 | — |

### 2.3 `/dev/ntsync` 在 Flatpak 下可用吗？——可用

Flatpak 对**新设备类型**的默认策略是：「**我们允许它们通过 `--device=all`，否则不允许**」（flatpak issue #6199，维护者原话）。

而 **Flatpak Steam 的 manifest 里就有 `--device=all`**（实测 `com.valvesoftware.Steam.yml` 第 45 行）：

```
41:  - --filesystem=/run/udev:ro
45:  - --device=all
46:  - --allow=multiarch      # Wine/Proton 跑 32 位代码所需
47:  - --allow=devel          # ptrace，pressure-vessel 需要
```

→ **`/dev/ntsync` 应当可见**（前提仍是宿主内核 ≥ 6.14）。建议本地验证一句：

```bash
flatpak run --command=sh com.valvesoftware.Steam -c 'uname -r; ls -l /dev/ntsync'
```

### 2.4 顺带纠正一条 NTSync 的性能口径（一手、权威）

flatpak 维护者在 issue #6199 里给出了比媒体更准确的表述，值得直接引用：

- "**ntsync is around the same speed as fsync**"——平均帧与 fsync 同级。
- 它带来的是"**better game/app compatibility** ... and **better 1% lows** since it's more efficient (less CPU overhead and less RAM usage) than the hacky fsync solution."
- "**If you have a fast CPU it would typically already handle fsync without much issues. People who are very CPU-bottlenecked would probably still see a big performance improvement with ntsync though.**"
- "the performance will not change as much as some people have been misled to believe based on benchmarks that **compared vanilla wine (no esync/fsync hacks) vs ntsync**."
- 实测例：**3600X + 5700XT 平台上，部分游戏 1% low 帧率翻了约三倍**。
- 机制：esync/fsync **完全忽略** waitstate 调用；NTSync 在内核里真正实现，"**which is why CPU bound situations under Linux punished frame rates**"。

> 这段把上一轮报告的判断钉死了：**NTSync 的价值在 CPU 受限场景的一致性，不在平均帧；且受益者主要是 CPU 较弱的机器。**

---

## 三、三种部署方式的收益保留度矩阵

| 优化层 | 原生 CachyOS | 别的发行版 + proton-cachyos(v3) | Flatpak Steam（+ v3 Proton） |
|---|---|---|---|
| 翻译层 v3 优化（DXVK / vkd3d / Wine） | ✅ | ✅ | ✅（需手动放入） |
| Proton-CachyOS 补丁（FSR4 / Reflex / OptiScaler） | ✅ | ✅ | ✅（需手动放入） |
| CachyOS 内核（BORE / EEVDF / 1000Hz） | ✅ | ❌ | ✅（宿主内核） |
| Mesa / RADV v3/v4 优化构建 | ✅ | ❌（用宿主 Mesa） | ❌（**用 runtime Mesa**） |
| glibc 优化 | ✅ | ❌ | ❌ |
| NTSync | ✅ 默认开 | ⚠️ 需内核 ≥ 6.14 | ⚠️ 需内核 ≥ 6.14（`--device=all` 已给） |
| CachyOS-Settings（sysctl / IO / ZRAM / THP / 电源档） | ✅ | ❌ | ❌ |
| 沙箱开销 | 无 | 无 | 可忽略 |

**一句话**：**翻译层优化可以"打包带走"，系统层优化不能。** Flatpak 额外削掉的是"宿主图形栈"，但换回了干净的依赖隔离。

---

## 四、可复用操作

```bash
# A) 任何发行版：装 v3 版 proton-cachyos（无需装 CachyOS）
TAG="cachyos-11.0-20261005-slr"      # 用前先查最新 tag
mkdir -p ~/.steam/root/compatibilitytools.d
curl -LO "https://github.com/CachyOS/proton-cachyos/releases/download/$TAG/proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz"
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz \
    -C ~/.steam/root/compatibilitytools.d/
# 重启 Steam → 游戏属性 → 兼容性 → 勾选"强制使用特定 Steam Play 兼容性工具" → 选 proton-cachyos

# B) Flatpak Steam：同一份 tarball，换个目录
mkdir -p ~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz \
    -C ~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/

# C) 确认沙箱里的内核与 NTSync
flatpak run --command=sh com.valvesoftware.Steam -c 'uname -r; ls -l /dev/ntsync'

# D) 想让 Flatpak 用宿主的图形栈？——做不到（这正是 Flatpak 的设计）
#    想要宿主 Mesa 优化，就用原生 Steam，不要用 Flatpak。
```

---

## 五、坑与反直觉

| 坑 | 说明 |
|---|---|
| **"Flatpak 更慢"** | 沙箱开销可忽略；真正的代价是**图形栈被换成 runtime 版本**。 |
| **"在 CachyOS 上用 Flatpak Steam"** | 相当于**自废武功**：把宿主优化过的 Mesa/glibc 换成 runtime 通用版本，同时还要再手动装 v3 Proton 才补回翻译层。 |
| **"从 AUR 装 proton-cachyos 就是 CachyOS 构建"** | ❌ 从 AUR/PKGBUILD 自行编译时，编译 flag 取决于你的机器与 PKGBUILD，**不一定**是官方的 v3 优化构建。要 v3 就用官方 `_v3` tarball。 |
| **v3 变体的硬件要求** | 需要 CPU 支持 **AVX2**（Intel Haswell 2013+ / AMD Excavator+）。老 CPU 用 `x86_64` 基线版。 |
| **Flatpak runtime 的 Mesa 可能比宿主旧** | 滚动发行版（CachyOS/Arch/Tumbleweed）尤其明显 → Flatpak 下图形栈可能倒退。 |
| **NTSync 不是"免费提速"** | 平均帧 ≈ fsync；收益在 **1% low 与 CPU 受限场景**。CPU 强 → 提升≈0。 |
| **N 卡在 Flatpak 下受影响较小** | 专有驱动由宿主挂载；AMD/Intel 走 runtime Mesa，受影响较大。 |

---

## 六、未核实 / 存疑

- **官方 `_v3` tarball 的具体编译 flag**（是否含 LTO / PGO / BOLT，还是仅 `-march=x86-64-v3`）：**未核实**。本次只确认了资产名为 `x86_64_v3`。
- **Flatpak 沙箱内 `/dev/ntsync` 的实测可用性**：基于 manifest 含 `--device=all` 的**推断**，未实测；建议按第四节 C 自行验证。
- **Flatpak vs 原生 Steam 的帧率差异**：**无公开对照基准**。"沙箱开销可忽略"为机制推断。
- **非 CachyOS 发行版上装 v3 Proton 的实际收益**：无实测数据。
- **Flatpak runtime 的 Mesa 与宿主 Mesa 的版本差**：随 runtime 分支与宿主发行版而异，未逐版本核对。

---

## 参考来源

- [CachyOS/proton-cachyos — GitHub（README：redistributable build → compatibilitytools.d）](https://github.com/CachyOS/proton-cachyos/)
- [proton-cachyos release `cachyos-11.0-20261005-slr` — GitHub Releases（含 `x86_64` / `x86_64_v3` / `arm64` 三个 tarball）](https://github.com/CachyOS/proton-cachyos/releases/tag/cachyos-11.0-20261005-slr)
- [CachyOS/proton-cachyos Releases API（资产清单：`proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz`）](https://api.github.com/repos/CachyOS/proton-cachyos/releases/403217640/assets)
- [flatpak/flatpak Issue #6199 — Support explicit permission control to access /dev/ntsync for ntsync（设备策略 + NTSync 性能权威表述）](https://github.com/flatpak/flatpak/issues/6199)
- [flathub/com.valvesoftware.Steam — manifest（`--device=all` / `--allow=multiarch` / `--allow=devel`）](https://github.com/flathub/com.valvesoftware.Steam/blob/master/com.valvesoftware.Steam.yml)
- [CachyOS — GitHub 组织页（proton-cachyos: optimized Proton by CachyOS）](https://github.com/CachyOS)
- [Phoronix — CachyOS Adds Limine Bootloader, Easier Samba Integration & NTSYNC Wine（2025-03-30）](https://www.phoronix.com/news/CachyOS-March-2025-Release)
- [ProtonDB — 用户报告（含 Flatpak runtime 显示为 Distro）](https://www.protondb.com/app/383120)
- [Proton-GE 完全指南（Flatpak Steam 的 compatibilitytools.d 路径）](https://blog.csdn.net/gitblog_01067/article/details/156667927)

> **来源质量说明**：proton-cachyos 的 GitHub Releases API 与 flatpak 的 issue/manifest 均为**一手核实**（本次直接抓取）；NTSync 的性能表述来自 flatpak 维护者，属**一手权威**且纠正了媒体口径；"沙箱开销可忽略"与"v3 构建的 flag"为**推断 / 未核实**，已在第六节标注。
