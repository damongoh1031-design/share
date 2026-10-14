# experts-bundle — 专家包跨 IDE 迁移恢复手册

打包日期：2026-10-14
来源：`C:\Users\Admin\.workbuddy-ai\`（win32 / WorkBuddy AI）

## 包结构（镜像新机落位路径）

```
experts-bundle/
├── README.md                          ← 本文件
├── manifest.json                      ← 清单
├── cache-experts/                     → 复制到 ~/.workbuddy-ai/plugins/cache/experts/
│   ├── deep-research/1.0.0/                   （123K）
│   ├── gpt-researcher-team/2.0.0/             （157K，6-agent 专家团）
│   ├── operations-customer-experts/1.0.0/     （777K，5 专家）
│   ├── education-training-experts/1.0.0/      （2.0M，专家+skills）
│   └── quality-testing-experts/1.0.0/         （2.0M，7 专家）
├── cache-my-experts/                  → 复制到 ~/.workbuddy-ai/plugins/cache/my-experts/
│   └── rimworld-mod-guardian/1.0.0/           （1.8M，自建专家，含头像）
├── marketplace-experts/plugins/       → 复制到 ~/.workbuddy-ai/plugins/marketplaces/experts/plugins/
│   └── <上述 5 包名的目录>/                     （只含已安装的 5 个，未含 208M 全量目录）
├── marketplace-my-experts/            → 复制到 ~/.workbuddy-ai/plugins/marketplaces/my-experts/
│   └── <my-experts 市场全量>                    （含 rimworld-mod-guardian 市场定义）
├── registration/
│   ├── installed-entries.json         ← 合并进新机 plugins/installed_plugins.json 的 plugins 映射
│   └── experts-custom/<用户A|用户B>/experts.json   ← 自建专家注册表（本机两个账号都有）
└── marketplace-defs/
    ├── experts.json                   ← known_marketplaces.json 的 experts 条目
    └── my-experts.json                 ← known_marketplaces.json 的 my-experts 条目
```

已剔除：所有 `.in_use/<pid>` 运行时标记、`github-sync/_work` 不涉及本包。

## 恢复步骤（新机 / 新 IDE）

1. 解压 `experts-bundle`（或从 GitHub 仓库 `workbuddy-migration/experts-bundle/` 拉取，内容一致且无密钥）。
2. 按目录名原样复制（保持 `plugins/<包名>/<版本>/` 层级）：
   ```bash
   cp -r experts-bundle/cache-experts/*      ~/.workbuddy-ai/plugins/cache/experts/
   cp -r experts-bundle/cache-my-experts/*   ~/.workbuddy-ai/plugins/cache/my-experts/
   cp -r experts-bundle/marketplace-experts/plugins/*   ~/.workbuddy-ai/plugins/marketplaces/experts/plugins/
   cp -r experts-bundle/marketplace-my-experts/.        ~/.workbuddy-ai/plugins/marketplaces/my-experts/
   ```
3. 注册市场定义：把 `marketplace-defs/experts.json`、`my-experts.json` 两个条目合并进
   新机的 `~/.workbuddy-ai/plugins/known_marketplaces.json`（`source.path` 若是绝对路径，
   改成新机的用户目录）。
4. 注册安装记录：把 `registration/installed-entries.json` 的 `plugins` 六个条目合并进新机
   `plugins/installed_plugins.json` 的 `plugins` 对象；`installPath` 里的
   `C:\Users\Admin\...` 若新机用户名不同，需全局替换。
5. 自建专家注册：按新机登录账号的 user-id 建目录，复制 `registration/experts-custom/<任一>/experts.json`：
   `~/.workbuddy-ai/experts/custom/<新账号user-id>/experts.json`（内容为 `["rimworld-mod-guardian"]`）。
   user-id 在 Expert Center 添加过自建专家后可从该目录名看出，直接照抄即可。
6. 重启 IDE，进 Expert Center 验证 6 个专家/专家团可见。

## 注意

- 5 个市场专家包在新机**也可以直接从专家市场重新安装**（包内含完整定义，本包是离线兜底）；
  自建的 `rimworld-mod-guardian` 只能随本包迁移，市场里没有。
- `gpt-researcher-team` 是 6-agent 专家团（planner/chief-editor/writer/reviewer/reviser/publisher）。
- 本包无任何真实密钥（已扫：命中的 password/apiKey 字样均为文档示例占位），可安全推 public 仓库。
