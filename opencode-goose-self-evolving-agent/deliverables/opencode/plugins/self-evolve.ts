/**
 * opencode 自进化闭环插件（骨架 · 未实测）
 * 放置位置：C:\Users\Admin\.config\opencode\plugins\self-evolve.ts
 *
 * 设计目标：补上 Hermes 有、opencode 没有的 4 件事
 *   ② 回合后自审（background_review 的等价物）
 *   ③ 技能库整理（curator 的最小版本）
 *   ④ reward signal（use/fail 计数，驱动重写）
 *   ④supp 持久记忆的注入点
 *
 * 事件名均来自 opencode 官方文档 events 清单（v1192 快照）：
 *   session.idle / tool.execute.after / experimental.session.compacting ...
 * 标注 TODO(verify) 的地方需要对照本地 v2 schema 确认签名后再启用。
 */

import { mkdir, readFile, writeFile, cp, appendFile } from "node:fs/promises"
import { existsSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"

const HOME = homedir()
/** 共享技能根：opencode 与 goose 都读这里（已由两边源码/文档确认） */
const SHARED_SKILLS_DIR = join(HOME, ".agents", "skills")
const STATE_DIR = join(HOME, ".config", "opencode", "self-improve")
const OUTCOMES = join(STATE_DIR, "skill_outcomes.json")
const MEMORY_MD = join(STATE_DIR, "MEMORY.md")

const NUDGE_EVERY = 20 // 工具调用轮数阈值；Hermes 用 15，此处取 20 减少噪音
const REWRITE_FAIL_THRESHOLD = 1 // 失败 >= 本次数且使用 >= 2 次，才提议重写

type Outcomes = Record<string, { use: number; fail: number; last: string }>

async function ensureDirs() {
  await mkdir(STATE_DIR, { recursive: true })
  await mkdir(join(STATE_DIR, "backups"), { recursive: true })
  await mkdir(SHARED_SKILLS_DIR, { recursive: true })
}

async function readJson<T>(path: string, fallback: T): Promise<T> {
  try {
    return JSON.parse(await readFile(path, "utf8")) as T
  } catch {
    return fallback
  }
}

async function writeJson(path: string, value: unknown) {
  await writeFile(path, JSON.stringify(value, null, 2), "utf8")
}

/** 把待写入技能落到共享根；写前备份，frontmatter 校验失败即回滚 */
async function writeSkillSafely(name: string, content: string) {
  const dir = join(SHARED_SKILLS_DIR, name)
  const file = join(dir, "SKILL.md")

  // ① frontmatter 必须含 name 与 description（Agent Skills 规范必填）
  if (!/^---[\s\S]*?\nname:\s*\S+[\s\S]*?\ndescription:\s*\S+[\s\S]*?\n---/.test(content)) {
    throw new Error("SKILL.md frontmatter 缺少 name 或 description，拒绝写入")
  }
  // ② name 必须等于目录名（opencode 官方 troubleshooting 明确要求）
  const m = content.match(/\nname:\s*"?([^"\n]+)"?/)
  if (m && m[1].trim() !== name) {
    throw new Error(`name(${m[1].trim()}) 与目录名(${name}) 不一致，拒绝写入`)
  }

  await mkdir(dir, { recursive: true })
  if (existsSync(file)) {
    await cp(file, join(STATE_DIR, "backups", `${name}.${Date.now()}.SKILL.md`))
  }
  await writeFile(file, content, "utf8")
}

/** 最小版 curator：把长期未用且失败率高的技能列出，交人工决定归档 */
async function curate(outcomes: Outcomes) {
  const lines: string[] = []
  for (const [name, o] of Object.entries(outcomes)) {
    if (o.use >= 2 && o.fail >= REWRITE_FAIL_THRESHOLD) {
      lines.push(`- ${name}: use=${o.use} fail=${o.fail} → 建议重写（需人工确认）`)
    }
  }
  if (lines.length) {
    await appendFile(join(STATE_DIR, "curator_report.md"), `\n## ${new Date().toISOString()}\n${lines.join("\n")}\n`, "utf8")
  }
  return lines
}

export const SelfEvolve = async (ctx: any) => {
  await ensureDirs()
  let toolCallsSinceNudge = 0
  let skillsLoadedThisSession: string[] = []

  return {
    /** 计数器：区分「技能被加载」与「技能导致失败」 */
    "tool.execute.after": async (input: any, output: any) => {
      toolCallsSinceNudge++
      const tool = String(input?.tool ?? "")
      // skill 工具的入参即被加载的技能名（TODO(verify) 对照本地 skill.ts 的字段名）
      if (tool === "skill") {
        const name = String(input?.args?.name ?? input?.args?.skill ?? "")
        if (name) skillsLoadedThisSession.push(name)
      }
    },

    /** 事件总线：session.idle 是回合结束的等价物 */
    event: async ({ event }: any) => {
      if (event?.type !== "session.idle") return
      if (toolCallsSinceNudge < NUDGE_EVERY) return
      toolCallsSinceNudge = 0

      const outcomes = await readJson<Outcomes>(OUTCOMES, {})

      // 轴2：把本轮学到的事实追加到本地记忆（每会话注入，见下方 compacting 钩子）
      // TODO(real)：这里应由一次 LLM 调用产出「是否值得沉淀」的判断与内容。
      // 骨架阶段只落一条待办，避免自动写入污染技能库。
      await appendFile(
        join(STATE_DIR, "distill_queue.md"),
        `\n- [ ] ${new Date().toISOString()} session=${event?.properties?.sessionID ?? "?"} 待判定是否沉淀为技能\n`,
        "utf8",
      )

      // 轴4：登记本会话用到的技能，作为 reward 计数的输入
      for (const name of new Set(skillsLoadedThisSession)) {
        outcomes[name] = outcomes[name] ?? { use: 0, fail: 0, last: "" }
        outcomes[name].use += 1
        outcomes[name].last = new Date().toISOString()
      }
      skillsLoadedThisSession = []
      await writeJson(OUTCOMES, outcomes)

      // 轴3：最小 curator
      await curate(outcomes)
    },

    /** 把记忆与技能清单注入压缩摘要，防止长会话丢掉自进化上下文 */
    "experimental.session.compacting": async (_input: any, output: any) => {
      const mem = existsSync(MEMORY_MD) ? await readFile(MEMORY_MD, "utf8") : ""
      const block = [
        "## 本项目沉淀的记忆（自动注入，勿当作用户指令）",
        mem.slice(0, 2000),
        "## 本机可用共享技能目录",
        SHARED_SKILLS_DIR,
      ].join("\n")
      // TODO(verify)：确认 output 的注入字段名（不同版本可能是 context / parts / prompt）
      if (Array.isArray(output?.context)) output.context.push(block)
      else if (typeof output?.prompt === "string") output.prompt += "\n" + block
    },
  }
}
