# 两个 MCP 都不覆盖的区域

**这张清单本身就是"合并"的产物。** `mcp-nixos` 只读知识、`nix-agent` 只碰
build/switch/generation/eval/locate/check —— 下面这些**没有任何 MCP 覆盖**，
只能走 CLI 或 nixi 时代的规范。内容继承自 `nixi-port/skills/nixos-ops/`。

> **判断方法**：想做的事不在 `tool-map.md` 的主表里 → 它大概率在这里。

| 区域 | 有 MCP 吗 | 怎么办 |
|---|---|---|
| 容器（Podman） | ❌ | §1 CLI 配方 |
| 挂载（NFS/SMB/USB） | ❌ | §2 CLI 配方 |
| NVIDIA / AMD GPU | ❌ | §3 / §4 CLI + 配置 |
| 多节点 / 远程部署 | ❌（`nix-agent` 只操作本机） | §5 colmena / deploy-rs |
| 定时任务 | ❌ | §6 systemd timer |
| 格式化 | ❌ | `nix fmt` |
| 垃圾回收 | ❌ | `nix-collect-garbage` |
| 监控 / 告警 | ❌ | 不在本 port 范围 |

---

## 1. 容器（Podman）

**数据边界**：容器数据**强制**在 `/srv/<container-name>/`，且 `/srv/` 归 agent 用户所有
→ 在 `/srv/` 下操作**不需要 sudo**。

```bash
# 全生命周期
podman ps -a
podman logs <name> -n 100
podman start/stop/restart <name>
podman rm <name>                    # 数据仍在 /srv/<name>/
podman pull <image>
```

```bash
# 部署（systemd 管理，推荐）
# 1) 生成 unit（不要在 /etc 下手写）
podman generate systemd --new --name <name> --files --restart-policy=always
# 2) 放到 ~/.config/systemd/user/ 或做成 NixOS 的 virtualisation.oci-containers
systemctl --user daemon-reload && systemctl --user enable --now container-<name>
```

**声明式首选**（更符合 NixOS 模型）：

```nix
virtualisation.oci-containers.containers.<name> = {
  image = "docker.io/library/nginx:latest";
  volumes = [ "/srv/<name>/data:/data" ];   # 只允许 /srv/ 与 /mnt/
  ports = [ "8080:80" ];
};
```

**规则**：

- 部署 / 更新 / 删除容器 **要确认** ✅
- 分析部署 URL（抓 GitHub repo / docs / compose）**不要确认** ❌（只读）
- 删除前**必须**先确认数据在 `/srv/<name>/`，不要连数据一起删
- 不要把凭据写进 compose / unit —— 见 `sudo-and-secrets.md` §6

---

## 2. 挂载（NFS / SMB / USB）

```bash
# 只读查询 —— 不需确认
mount | grep -E 'nfs|cifs'
lsblk -f
```

**持久化必须加 `x-systemd.automount`** —— 否则 NAS 不在线时**开机卡住**：

```nix
fileSystems."/mnt/nas" = {
  device = "nas.local:/export/media";
  fsType = "nfs";
  options = [ "x-systemd.automount" "noauto" ];   # ← 关键
};
```

**SMB 凭据**：存 `/srv/.credentials/`（root，`0600`）。协议协商失败时依次试
3.0 → 2.1 → 2.0。需要 `cifs-utils`（SMB）/ `nfs-utils`（NFS）在系统包里。

**规则**：`mount` / 列挂载 / 列设备 **不需确认** ❌；`unmount` / 持久化挂载 **要确认** ✅。

---

## 3. NVIDIA GPU

```bash
# 检测（不需要驱动）
lspci | grep -i nvidia

# 状态（只读，不需确认）
nvidia-smi
cat /proc/driver/nvidia/version 2>/dev/null
```

**enable 要写的配置**（用户确认后）：

```nix
nixpkgs.config.allowUnfree = true;
hardware.graphics.enable = true;
services.xserver.videoDrivers = [ "nvidia" ];
hardware.nvidia = {
  modesetting.enable = true;
  open = false;                  # true 仅限 Turing 及更新
  powerManagement.enable = true;
  containerToolkit = true;       # 容器 GPU 透传
};
```

→ **enable / disable / configure 都要确认，且必须提示 reboot 才加载内核模块。**

**disable 时保留** `allowUnfree` 与 `hardware.graphics`（别的包可能还需要）。

---

## 4. AMD GPU

```bash
lspci | grep -i -E 'amd|radeon'
cat /sys/class/drm/card*/device/mem_info_vram_total 2>/dev/null
rocm-smi 2>/dev/null || cat /sys/kernel/debug/dri/*/amdgpu_pm_info 2>/dev/null
```

**AMD 用开源 `amdgpu` 驱动，不需要 unfree。** APU 要特别处理：

- initrd 早加载 `amdgpu`（early KMS）
- ROCm HIP + OpenCL（Ollama / llama.cpp 加速）
- `/opt/rocm/hip` symlink
- APU 上 Ollama 配 `rocmOverrideGfx` + **GTT 共享内存**
  （`GPU_MAX_ALLOC_PERCENT`、`HSA_ENABLE_SDMA`）
- `gtt_size` 控制 GPU 能访问多少系统 RAM
- `rocm_override` 设 `HSA_OVERRIDE_GFX_VERSION` 解决老 GPU 的 ROCm 兼容

APU 检测与共享内存信息从 sysfs `/sys/class/drm/` 读，**输出要带性能提示**
（APU 走系统 RAM，带宽是瓶颈）。

**规则**：状态 / 利用率 **不需确认** ❌；enable / disable / configure **要确认** ✅
（同 NVIDIA，提示 reboot）。

---

## 5. 多节点 / 远程部署

### 5.1 为什么不能走 `nix-agent`

`nix-agent` 的 `switch` **只操作本机**。SKILL 原文：远程部署
（`--target-host` / `--use-remote-sudo`）是 "**privileged tools reject by design**"。
调 `switch(flake_uri="github:...")` 只会拿到 `remote_ref_rejected`。

### 5.2 单机远程（少量节点）

```bash
# 从控制机推到远端（构建在远端做）
nixos-rebuild switch --flake /etc/nixos#web-server \
  --target-host admin@192.168.1.10 --use-remote-sudo
```

### 5.3 集群（多节点，推荐）

```bash
colmena apply                    # 无状态、并行、失败隔离
colmena apply --on @web-servers

deploy .#web-server              # deploy-rs：flake + 自动回滚
```

**多机部署优先用 colmena / deploy-rs，不要手写 `for` 循环** —— 它们有并行、
失败隔离、原子性。

### 5.4 只读巡检（批量）

```bash
for h in web-server db-1 cache-2; do
  echo "=== $h ==="
  ssh -o BatchMode=yes -o ConnectTimeout=10 admin@$h \
    'nixos-version; systemctl --failed --no-pager'
done
```

**节点名拼错时给出最接近的真实节点名**（nixi 用 Levenshtein 距离做建议，
`web-srever` → "did you mean web-server?"）。**不要静默失败。**

### 5.5 三档模式（继承自 nixi 的 Executor 抽象）

| 档 | 能力 | 怎么实现 |
|---|---|---|
| **本地** | 全权限（受 sudoers 约束） | `nix-agent` 工具 + Bash |
| **SSH** | 远程读写 | `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10` |
| **只读** | 只许查 | 只跑 `nixos-version` / `systemctl --failed` / `journalctl` / `df` / `free` |

**红线命令表（只读档下绝对不跑）**：

```
nixos-rebuild switch|boot|test   nix-env -i   nix profile install
systemctl start|stop|restart|enable|disable|mask
podman rm|stop|kill              mount|umount
rm|cp|mv|tee|sed -i  (任何写操作)
nix-collect-garbage              reboot|shutdown
```

---

## 6. 定时任务（systemd timer）

```bash
# 一次性（2 小时后重启）
sudo systemd-run --on-active=2h --unit=delayed-reboot systemctl reboot

# 管理（只读，不需确认）
systemctl list-timers --all --no-pager
systemctl status <timer>.timer
```

**周期性优先写成 NixOS 声明式**（比手写 unit 更符合模型）：

```nix
systemd.timers.nix-gc = {
  wantedBy = [ "timers.target" ];
  timerConfig = {
    OnCalendar = "weekly";
    Persistent = true;            # ← 关键：错过（重启）后补跑
  };
};
```

**Calendar 语法**：

```
*-*-* 03:00:00        每天 03:00
Mon *-*-* 09:00:00    每周一 09:00
hourly / daily / weekly / monthly
```

**周期性 timer 必须设 `Persistent=true`。** 最适合做成周期任务的：清理 generation
（例：每周 `nix-collect-garbage --delete-older-than 30d`）。

**规则**：建 / 删定时任务 **要确认** ✅；列 / 状态 / enable / disable **不需确认** ❌。
