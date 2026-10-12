# 容器 / 挂载 / GPU 命令配方

> 来源：nixi `docs/content/tools.md` 的 `container` / `mount` / `nvidia` / `amdgpu` / `scheduler`
> 五个工具段。

## 1. 容器（Podman / Docker）

### 网络模型
- 所有容器加入共享 `nixi` 网络 → **同节点容器互相用名字解析**
- 跨节点引用用**节点 IP**（容器 DNS 只在本地有效）

### 数据边界
- 容器数据**强制**在 `/srv/<container-name>/`
- volume mount 只接受 `/srv/`（容器数据）和 `/mnt/`（外部挂载）
- **删容器默认保留数据**；要连数据一起删必须用户明确说 purge

### 常用命令

```bash
# 列表与检查
podman ps -a
podman inspect <name>
podman logs --tail 100 <name>
podman exec -it <name> <cmd>

# 部署（先 dry 看会拉什么镜像）
podman pull docker.io/nginx:latest
podman run -d --name webserver \
  --network nixi \
  -p 8080:80 \
  -v /srv/webserver/data:/data \
  nginx:latest

# 外部存储先挂载，再 bind（例：/mnt/media:/media:ro）

# 更新（等价于重新 run）
podman pull nginx:latest
podman stop webserver && podman rm webserver
# 再用同样的 run 命令起（数据在 /srv/webserver/ 所以不丢）

# 删除
podman rm <name>                      # 保留 /srv/<name>/ 数据
podman rm <name> && rm -rf /srv/<name>/   # purge，需显式确认
```

### 从 URL 分析部署配置（只读）
用户说 "帮我部署 nextcloud" 或给一个 GitHub repo 链接时：
1. 抓 repo 找 `docker-compose.yml` / `Dockerfile` / 文档
2. 提取：镜像、端口、volume、env
3. 有不清楚的**先问用户**，不要猜
4. 这一步是只读的，不需要确认

### Stack 命名约定
相关服务用 stack 前缀：`<stack>` 主服务、`<stack>-db` 数据库、`<stack>-cache` 缓存。
例：`nextcloud` + `nextcloud-db` + `nextcloud-redis`。依赖先部署。

## 2. 挂载（NFS / SMB / USB）

```bash
# 列设备与挂载
lsblk -f
findmnt
mount | grep -E '/mnt|/srv'

# NFS
mkdir -p /mnt/media
mount -t nfs 192.168.1.10:/media /mnt/media

# SMB（用户名交互式输入，不要写在命令行）
mkdir -p /mnt/movies
mount -t cifs //nas/movies /mnt/movies -o username=erik
mount -t cifs //nas/public /mnt/public -o guest        # 匿名

# 卸载
umount /mnt/media

# 持久化（改 configuration.nix）
# fileSystems."/mnt/media" = {
#   device = "192.168.1.10:/media";
#   fsType = "nfs";
#   options = [ "x-systemd.automount" "noauto" ];   # NAS 离线时不会卡启动
# };
```

**持久化必须加 `x-systemd.automount`** —— 否则 NAS 不在线时开机卡住。

**SMB 凭据**：存 `/srv/.credentials/`（root 所有，600）。协议协商失败时依次试 3.0 → 2.1 → 2.0。
需要 `cifs-utils`（SMB）和 `nfs-utils`（NFS）在系统包里。

## 3. NVIDIA GPU

```bash
# 检测（不需要驱动）
lspci | grep -i nvidia

# 状态
nvidia-smi
cat /proc/driver/nvidia/version 2>/dev/null
```

**enable 需要写什么配置**（用户确认后）：
```nix
nixpkgs.config.allowUnfree = true;
hardware.graphics.enable = true;
services.xserver.videoDrivers = [ "nvidia" ];
hardware.nvidia = {
  modesetting.enable = true;
  open = false;                          # true 仅限 Turing+
  powerManagement.enable = true;
  containerToolkit = true;               # 容器 GPU 透传
};
```
→ **enable / disable / configure 都要确认，且必须提示 reboot 才加载内核模块。**

**disable 时保留** `allowUnfree` 和 `hardware.graphics`（其他包可能还需要）。

## 4. AMD GPU

```bash
lspci | grep -i -E 'amd|radeon'
cat /sys/class/drm/card*/device/mem_info_vram_total 2>/dev/null
rocm-smi 2>/dev/null || cat /sys/kernel/debug/dri/*/amdgpu_pm_info 2>/dev/null
```

**AMD 用开源 `amdgpu` 驱动，不需要 unfree。** APU 特别处理：
- initrd 早加载 `amdgpu`（early KMS）
- ROCm HIP + OpenCL（Ollama / llama.cpp 加速）
- `/opt/rocm/hip` symlink
- APU 上 Ollama 服务配 `rocmOverrideGfx` + GTT 共享内存
  （`GPU_MAX_ALLOC_PERCENT`、`HSA_ENABLE_SDMA`）
- `gtt_size` 控制 GPU 能访问多少系统 RAM
- `rocm_override` 设 `HSA_OVERRIDE_GFX_VERSION` 解决老 GPU 的 ROCm 兼容

**APU 检测与共享内存信息**：从 sysfs `/sys/class/drm/` 读，输出要带性能提示。

## 5. 定时任务

```bash
# 一次性
sudo systemd-run --on-active=2h --unit=reboot-later systemctl reboot

# 周期性（systemd calendar 语法）
# OnCalendar=*-*-* 03:00:00     每天 03:00
# OnCalendar=Mon *-*-* 09:00:00 每周一 09:00
# OnCalendar=hourly / daily / weekly / monthly

# 管理
systemctl list-timers --all --no-pager
systemctl status <timer>.timer
```

**周期性 timer 要设 `Persistent=true`** —— 错过（重启）后补跑。
清理 generation 是最适合做成周期任务的，例：每周 `nix-collect-garbage --delete-older-than 30d`。
