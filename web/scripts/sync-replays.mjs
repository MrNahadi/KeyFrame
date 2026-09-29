// Copy the exported replay files (../models/replays) into public/replays so the
// replay view works on any static host, with no API. Also copy the model card and
// its confusion matrix figure for the model card page.
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

const files = [
  ['../../reports/model_card.md', '../public/model_card.md'],
  ['../../reports/figures/07_confusion.png', '../public/figures/07_confusion.png'],
]
for (const [from, to] of files) {
  const src = resolve(here, from)
  if (!existsSync(src)) {
    console.error(`Missing ${src}. Run the evaluation notebook (notebooks/07_evaluation.py) to create it.`)
    process.exit(1)
  }
  mkdirSync(dirname(resolve(here, to)), { recursive: true })
  cpSync(src, resolve(here, to))
  console.log(`Copied ${src}`)
}
