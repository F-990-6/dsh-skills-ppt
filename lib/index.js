/**
 * dsh-skills-ppt — expose the ppt-master workflow as a DSH runtime skill.
 *
 * The skill body is the upstream `skill/ppt-master/SKILL.md`, read from this
 * package at apply time, so the catalog entry stays in sync with the files that
 * ship beside it. Registering through `ctx.skills.register` means the skill is a
 * normal catalog entry: it costs nothing until the model loads it, and the
 * loaded instructions point back at this package as their resource base.
 */
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'dsh-skills-ppt'
export const inject = ['skills']

const HERE = dirname(fileURLToPath(import.meta.url))
const SKILL_DIR = join(HERE, '..', 'skill', 'ppt-master')
const SKILL_FILE = join(SKILL_DIR, 'SKILL.md')

const FALLBACK_DESCRIPTION =
  'AI-driven presentation workflow: turn a document, topic or existing deck into an editable ' +
  'native PPTX with real shapes, charts, tables, narration and templates.'

const WHEN_TO_USE = [
  '任何做 PPT 的请求都用它：做演示文稿、生成 PPT / PPTX、做课件、把文档或主题变成幻灯片、',
  '美化或重排已有 PPTX、套用模板、加旁白/动画/自动播放视频。',
  '英文同理：create, generate, beautify, redesign, template, fill or enhance a presentation, slide deck or courseware.',
  '若没有自动触发，用户说「用 ppt-master 技能来做」也能强制调用。',
].join('')

/**
 * Read the few frontmatter fields this plugin needs without a YAML dependency:
 * `key: value`, quoted scalars, and folded (`>`) or literal (`|`) block scalars.
 */
function parseFrontmatter(text) {
  const clean = text.replace(/^\uFEFF/, '')
  const lines = clean.split(/\r?\n/)
  if (lines[0]?.trim() !== '---') return { data: {}, body: clean }

  const data = {}
  let key = null
  let block = null // '>' or '|'
  let index = 1

  for (; index < lines.length; index += 1) {
    const line = lines[index]
    if (line.trim() === '---') break

    if (key !== null && (/^\s+\S/.test(line) || (block !== null && line.trim() === ''))) {
      const piece = line.trim()
      const nested = block === null && data[key] !== '' ? '\n' : (block === '|' ? '\n' : ' ')
      data[key] = data[key] ? `${data[key]}${nested}${piece}` : piece
      continue
    }

    const match = /^([A-Za-z0-9_-]+)\s*:\s*(.*)$/.exec(line)
    if (!match) continue

    key = match[1]
    block = null
    let value = match[2].trim()

    if (value === '>' || value === '|') {
      block = value
      data[key] = ''
      continue
    }
    if (value === '') {
      data[key] = ''
      continue
    }
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1)
    }
    data[key] = value
  }

  return { data, body: lines.slice(index + 1).join('\n').replace(/^\r?\n/, '') }
}

export function apply(ctx) {
  if (!existsSync(SKILL_FILE)) {
    ctx.logger?.warn?.(`[dsh-skills-ppt] missing ${SKILL_FILE}; skill not registered`)
    return
  }

  const raw = readFileSync(SKILL_FILE, 'utf8')
  const { data, body } = parseFrontmatter(raw)
  const version = /version:\s*"?([0-9][\w.-]*)"?/.exec(data.metadata ?? '')?.[1]

  ctx.skills.register({
    name: 'ppt-master',
    description: data.description || FALLBACK_DESCRIPTION,
    whenToUse: WHEN_TO_USE,
    content: body,
    source: 'runtime',
    path: SKILL_FILE,
    resourceBase: { kind: 'directory', path: SKILL_DIR },
    invocation: { modelInvocable: true, userInvocable: true },
    metadata: {
      upstream: 'https://github.com/hugohe3/ppt-master',
      version: version ?? 'bundled',
    },
  })
}
