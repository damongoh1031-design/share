---
id: btrfs-multiuser-home-dedup-vs-symlink
title: btrfs 多用户 home 共享：去重 / 软链接 / 共享目录 / reflink 的取舍
tags: [btrfs, dedup, duperemove, bees, reflink, symlink, hardlink, multi-user, storage]
created: 2026-10-19
updated: 2026-10-19
version: 1
status: stable
source: 本次会话分析 + btrfs/duperemove 官方文档、Arch Wiki、内核 FIDEDUPERANGE 语义
confidence: 已核实
---

## 一句话结论

**底层用 btrfs 去重（duperemove）省空间，语义上"必须是同一份可变数据"的地方用共享组目录，软链接只用于指向 home 之外的只读大文件，硬链接不要用。**

去重和软链接不是同一层的两个选项：去重是**存储层**的透明共享，软链接是**命名空间层**的路径跳转。混在一起比较才会纠结。

## 三者定位

| 维度 | btrfs 去重（dedup） | 软链接（symlink） | 共享组目录 + ACL |
|---|---|---|---|
| 作用层 | 文件系统 extent | 目录项路径 | 权限模型 |
| 两个账户看到什么 | 各自独立的完整文件 | 同一个目标文件 | 同一个目标目录 |
| 权限耦合 | 无 | 有（按目标文件的权限判定） | 有（组权限） |
| 一个账户改文件，另一个 | 不受影响（COW 分离） | 立刻看到改动 | 立刻看到改动 |
| 应用兼容性 | 完全透明 | 应用不跟随 symlink 时会坏 | 透明 |
| 空间节省条件 | 内容按块相同 | 100%（真共享） | 100% |
| 删除一个账户的 home | 另一个不受影响 | 目标在 home 内 → 变死链 | 不受影响 |
| 可逆性 | 可逆（只增引用计数） | 可逆 | 可逆 |

## 决策表

| 场景 | 用哪个 | 理由 |
|---|---|---|
| 两份 home 里有大量**内容相同但各自独立**的文件（照片、文档、ISO、源码、node_modules、容器镜像层） | **duperemove 去重** | 透明、权限不耦合、删一边不影响另一边 |
| **必须共用同一份可变数据**（Steam 游戏库、媒体库、共享项目目录） | **共享组目录 + setgid + ACL** | 语义就是"一份"，去重无法解决"两边改出分歧" |
| 只读大文件给另一个账户看 | **symlink 到 `/srv/...`** | 零拷贝，目标必须在 home 之外且 `o+rx` |
| 需要"同起点、之后各自改" | **`cp --reflink=always`** | 瞬时完成、COW、之后完全独立 |
| 想省空间又不想维护定时任务 | **先开 `compress=zstd`** | 零维护成本，与去重叠加 |
| 硬链接 | **不要用** | 见「坑」第 3 条 |

## 推荐架构（三层）

```
/home  (btrfs)
├── @alice   子卷  压缩 zstd:3   ← 普通 home，去重覆盖
├── @bob     子卷  压缩 zstd:3   ← 普通 home，去重覆盖
└── (duperemove 每周扫 /home，跨子卷去重)

/srv/shared  普通目录，组 shared，setgid 2775
├── steam/    ← Steam 库，两个账户在 Steam 里添加为库文件夹
└── media/    ← 只读媒体，两个 home 里各放一个 symlink
```

要点：

- 每个账户一个**子卷**，快照互不影响；btrfs 去重**支持跨子卷**（同一文件系统内），所以子卷不会削弱去重效果。
- 两个子卷的**压缩算法和级别必须一致**。压缩参数不同 → 落盘字节不同 → 去重直接失效。
- 共享目录放在 `/srv`，不要放进任何一个 home。home 一般是 `0700`，另一个账户连路径都穿不过去。

## 可复用操作

### 1. 去重（主方案）

```bash
# 确认文件系统与子卷
findmnt -no FSTYPE,OPTIONS /home
btrfs subvolume list /home

# 每个账户一个子卷
btrfs subvolume create /home/alice
btrfs subvolume create /home/bob
btrfs property set /home/alice compression zstd:3
btrfs property set /home/bob   compression zstd:3   # 必须与 alice 一致

# 安装并首次全量去重（root）
apt install duperemove          # Debian/Ubuntu；Fedora: dnf install duperemove
duperemove -dr --hashfile=/var/lib/duperemove.hash /home

# 每周自动跑（--hashfile 让后续只处理变更文件）
cat >/etc/systemd/system/duperemove.service <<'EOF'
[Unit]
Description=btrfs dedupe /home
[Service]
Type=oneshot
ExecStart=/usr/sbin/duperemove -dr --hashfile=/var/lib/duperemove.hash /home
EOF
cat >/etc/systemd/system/duperemove.timer <<'EOF'
[Unit]
Description=Weekly btrfs dedupe /home
[Timer]
OnCalendar=weekly
Persistent=true
[Install]
WantedBy=timers.target
EOF
systemctl enable --now duperemove.timer
```

`duperemove -dr` = dedupe + recursive。加 `-v` 看进度。

### 2. 共享组目录（真正共享的那部分）

```bash
groupadd shared
usermod -aG shared alice
usermod -aG shared bob

mkdir -p /srv/shared/steam /srv/shared/media
chgrp -R shared /srv/shared
chmod 2775 /srv/shared /srv/shared/steam        # 2 = setgid，新文件继承组
setfacl -R -m g:shared:rwX -m d:g:shared:rwX /srv/shared
setfacl -R -m g:shared:rX  -m d:g:shared:rX  /srv/shared/media   # 媒体只读

# 两个账户的 umask 改 002，否则新文件默认 644 组内不可写
# /etc/login.defs: UMASK 002   （或 ~/.profile 里 umask 002）
```

Steam：两个账户各自在「设置 → 存储 → 添加驱动器」里加 `/srv/shared/steam`。**不要**去 symlink `~/.local/share/Steam`。

### 3. reflink（同起点、独立演化）

```bash
cp -a --reflink=always /home/alice/photos /home/bob/photos
# 瞬时完成，占 0 额外空间；之后任一边修改只额外占用改动块
```

### 4. 只读 symlink

```bash
ln -s /srv/shared/media /home/alice/Media
ln -s /srv/shared/media /home/bob/Media
# 前提：/srv/shared/media 对 other 或 shared 组可读可进入
```

### 5. 验证效果

```bash
btrfs filesystem du -s /home/alice /home/bob   # 看 Exclusive / Shared
compsize /home                                  # 看压缩率（含 shared）
btrfs filesystem usage /home                    # 看整体占用
```

## 坑与反直觉

1. **`chattr +C`（nodatacow）的文件无法去重。** Steam 库、虚拟机镜像、数据库文件常被设成 `+C`。查：`lsattr -R /home 2>/dev/null | awk '$1 ~ /C/ {print $2}'`。这类数据只能走共享目录，不能靠去重。
2. **`btrfs filesystem defragment` 会打断去重 / reflink 共享。** 去重和 reflink 用的是同一套 extent 引用机制，defrag 会重写 extent → 共享断掉 → 空间反弹。已去重的数据不要 defrag。
3. **硬链接别用在用户数据上。** 三个问题叠加：`fs.protected_hardlinks=1` 默认禁止跨用户建硬链接；硬链接共用 inode → 权限和属主只有一份，两个账户无法各自独立；编辑器 / `sed -i` / 大部分程序用「写临时文件再 rename」保存 → 硬链接静默断开，两边变成两份分歧副本，且没人会察觉。
4. **symlink 指进另一个 `0700` 的 home 必然失败。** 路径遍历权限在解析 symlink 时就检查了。`namei -l /home/alice/data` 一看就知道卡在哪一级。共享目标必须放在 home 之外。
5. **不要把 `~/.config`、`~/.local`、`~/.cache`、`~/.steam` 做成共享或 symlink。** 这些是 per-user 状态：属主错乱、DBus/session 冲突、XDG 基目录解析异常、应用写锁互相打架。
6. **btrfs qgroup 会把共享 extent 在每个子卷各算一次。** 开了 quota 后，"每用户用量"会虚高（同一份数据算两遍）。要精确计量得看 `btrfs filesystem du` 的 Exclusive，而不是 qgroup referenced。
7. **去重只对"完全相同的块"生效。** 128K 块级比较，文件头尾不同就整块不去重；小文件（< 块大小）基本无收益。真实收益集中在游戏资源、ISO、照片、源码依赖目录这类大块重复数据。文本配置文件的去重收益接近 0。
8. **bees 是常驻进程版去重（实时），duperemove 是批处理版。** 两个账户的量级用 duperemove 每周跑一次足够；bees 需要常驻内存维护哈希表（大容量文件系统上 GB 级），调参成本更高，收益只在"写入即去重"这一条。

## 未核实 / 存疑

- Steam 多账户共用同一个库目录：`steamapps/common` 共享没问题，但 `steamapps/compatdata`（Proton 前缀）按 appid 而非按用户区分，两个账户玩同一款 Proton 游戏可能共用存档前缀。属**社区实证**，未在本机验证。
- `duperemove` 对已压缩 extent 的去重效果：理论上同算法同级别压缩后字节相同即可去重，实际比例受内核版本与块对齐影响，未做定量测试。
- 去重带来的元数据开销（extent 引用数增加）在 10 万级文件规模下的实际影响，未测。
