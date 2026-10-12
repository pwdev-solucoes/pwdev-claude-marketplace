import type { PwdevModsTokens } from '../../types'

export const tokensOf = (t: PwdevModsTokens): number => t.input + t.output + t.cacheRead + t.cacheWrite

export const compact = (n: number): string => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n >= 10_000_000 ? 0 : 1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(n >= 10_000 ? 0 : 1)}k`
  return String(Math.round(n))
}

export const usd = (n: number): string => `$${n < 10 ? n.toFixed(2) : n.toFixed(1)}`

export const percent = (n: number | undefined): string => (n === undefined ? '—' : `${Math.round(n)}%`)

/** A horizontal bar of `width` cells, filled to `ratio` (0..1). */
export const bar = (ratio: number, width: number): string => {
  const cells = Math.max(0, Math.min(width, Math.round(Math.max(0, Math.min(1, ratio)) * width)))
  return '█'.repeat(cells) + '░'.repeat(width - cells)
}

const SPARKS = '▁▂▃▄▅▆▇█'

/** One block glyph per value, scaled to the largest. */
export const sparkline = (values: readonly number[]): string => {
  const max = Math.max(0, ...values)
  return values
    .map(v => (max === 0 ? SPARKS[0] : SPARKS[Math.min(SPARKS.length - 1, Math.floor((v / max) * (SPARKS.length - 1)))]))
    .join('')
}

export const duration = (ms: number): string => {
  const s = Math.max(0, Math.round(ms / 1000))
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m${String(s % 60).padStart(2, '0')}s`
  return `${Math.floor(m / 60)}h${String(m % 60).padStart(2, '0')}m`
}

/** The local calendar day of a timestamp, `YYYY-MM-DD`. */
export const dayOf = (ms: number): string => {
  const d = new Date(ms)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export const shortModel = (model: string): string => model.replace(/^claude-/, '').replace(/-\d{8}$/, '')

export const clip = (text: string, width: number): string => (text.length <= width ? text : `${text.slice(0, Math.max(1, width - 1))}…`)
