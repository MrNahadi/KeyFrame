import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

// Manifesto Part 14: "No raw hex values in components." Colours live in tokens.css only.
const SRC = join(__dirname, '..')
const RAW_COLOUR = /#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(/

function files(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name)
    return statSync(path).isDirectory() ? files(path) : [path]
  })
}

describe('design tokens', () => {
  it('keeps raw colours out of every file except tokens.css', () => {
    const offenders = files(SRC)
      .filter((f) => /\.(css|tsx?)$/.test(f) && !f.endsWith('tokens.css') && !f.endsWith('.test.ts'))
      .filter((f) => RAW_COLOUR.test(readFileSync(f, 'utf8')))
      .map((f) => relative(SRC, f))
    expect(offenders).toEqual([])
  })
})
