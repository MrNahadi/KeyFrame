import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

// MY-DESIGN §3: tokens for every colour and size, no emoji. Colours live in tokens.css only.
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

  it('only uses tokens that tokens.css defines', () => {
    const defined = new Set(
      [...readFileSync(join(SRC, 'styles', 'tokens.css'), 'utf8').matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]),
    )
    // Set per element by a component (the sensor group's colour), not a global token.
    const local = new Set(['--group'])
    const unknown = files(SRC)
      .filter((f) => /\.(css|tsx?)$/.test(f) && !f.includes('.test.'))
      .flatMap((f) =>
        [...readFileSync(f, 'utf8').matchAll(/var\((--[\w-]+)/g)]
          .map((m) => m[1])
          .filter((name) => !defined.has(name) && !local.has(name))
          .map((name) => `${relative(SRC, f)}: ${name}`),
      )
    expect(unknown).toEqual([])
  })

  it('sizes type with tokens, never px font sizes', () => {
    const offenders = files(SRC)
      .filter((f) => /\.css$/.test(f) && !f.endsWith('tokens.css'))
      .filter((f) => /font-size:\s*\d+(\.\d+)?px/.test(readFileSync(f, 'utf8')))
      .map((f) => relative(SRC, f))
    expect(offenders).toEqual([])
  })

  it('has no emoji anywhere in the interface', () => {
    const offenders = files(SRC)
      .filter((f) => /\.(css|tsx?|json)$/.test(f))
      .filter((f) => /\p{Extended_Pictographic}/u.test(readFileSync(f, 'utf8').replace(/[©®™]/g, '')))
      .map((f) => relative(SRC, f))
    expect(offenders).toEqual([])
  })
})
