// Copy the exported replay files (../models/replays) into public/replays so the
// replay view works on any static host, with no API.
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const source = resolve(here, '../../models/replays')
const target = resolve(here, '../public/replays')

if (!existsSync(resolve(source, 'index.json'))) {
  console.error(
    `No replay files at ${source}. Create them from the repo root with:\n` +
      '  uv run python -m keyframe.experiments replay',
  )
  process.exit(1)
}
rmSync(target, { recursive: true, force: true })
mkdirSync(target, { recursive: true })
cpSync(source, target, { recursive: true })
console.log(`Copied replays to ${target}`)
