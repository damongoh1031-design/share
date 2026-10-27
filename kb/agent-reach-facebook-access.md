---
id: agent-reach-facebook-access
title: Agent Reach Facebook 接入与 Cookie 登录态
tags: [agent-reach, facebook, cookies, browser]
created: 2026-10-27
updated: 2026-10-27
version: 1.1
status: draft
source: 本机命令实测及 Agent Reach 1.6.0 本地操作说明
confidence: 已核实
---

## 一句话结论

【已核实】Facebook 浏览器路径可复用站点 Cookie；本机登录读取已成功，但渠道安装因 9222 端口冲突失败。安装渠道、登录与成功读取是三个独立步骤，不能相互替代。

## 接入与能力边界

| 项目 | 结论与口径（2026-10-27） |
|---|---|
| 本机程序 | 已安装 Agent Reach 1.6.0，安装方式 uv |
| Facebook 渠道安装 | 添加失败：9222 端口被程序认定为非托管浏览器占用；未关闭现有浏览器 |
| 浏览器归属限制 | 注入使用本机 9222 调试接口；后续安装结果表明不能将其确认为 Reach 托管的专用浏览器 |
| 浏览器登录实测 | 用户授权提供会话后，已导入关键 Cookie 并成功打开本人主页、读取页面文字；未遇验证码 |
| 声明的动作 | search、profile；实验级渠道 |
| 登录复用 | Chrome 已连接 OpenCLI 扩展时，可复制仅 Facebook 的 Cookie 到专用浏览器 |
| 无可用登录态 | 按实际错误决定是否打开专用窗口，由用户本人登录 |
| 公开路径 | 可先尝试公开搜索摘要，不应把所有访问一概判定为必须登录 |
| 正文和评论 | 不承诺独立帖文读取或完整评论导出 |

## 可复用操作

```bash
agent-reach version
agent-reach doctor
agent-reach add facebook
agent-reach browser status
agent-reach check facebook --text
```

真实动作返回 NEED_LOGIN 且任务需要站内路径时执行：

```bash
agent-reach login facebook
```

用户自行完成登录后，再执行原查询。不要在聊天、日志或版本库中存储 Cookie。

## 坑与反直觉

- Cookie 存在不等于登录有效；必须以真实动作结果为准。
- Chrome 里已登录不等于可以自动复用；复制依赖已连接的扩展。
- 安装成功不等于 Facebook 读取成功；实验渠道可能受改版影响。
- 不从 PyPI 安装同名 agent-reach 包；官方项目要求从其 GitHub 发布包安装。
- 遇到验证码、限流或登录要求应停止，不能靠换后端反复请求。

## 未核实项

- 渠道添加因本机 9222 非托管调试会话冲突而失败；须经用户确认后处理原会话，再继续添加。
- 已验证浏览器本人主页访问；尚未验收渠道 search/profile 命令或其他指定内容。

## 修订记录

- 1.1（2026-10-27）：补充本机 Cookie 登录验证成功；区分浏览器可用与渠道依赖安装完成。未收录任何凭据或个人主页信息。

## 参考

- https://github.com/Panniantong/Agent-Reach
- https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md
- 本机说明：C:/Users/Admin/.agents/skills/agent-reach/references/sessions.md
