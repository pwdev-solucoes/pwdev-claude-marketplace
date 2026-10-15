import type { PwdevModsDay, PwdevModsTokens } from '../../types'
import { tokensOf } from './format'

export const DAY_PREFIX = 'daily:'

export const emptyDay = (date: string): PwdevModsDay => ({
  date,
  input: 0,
  output: 0,
  cacheRead: 0,
  cacheWrite: 0,
  usd: 0,
  turns: 0,
  byModel: {},
})

/** Folds one turn (its tokens, model and the cost it added) into a day. */
export const addToDay = (day: PwdevModsDay, tokens: PwdevModsTokens, model: string, usdDelta: number): PwdevModsDay => ({
  ...day,
  input: day.input + tokens.input,
  output: day.output + tokens.output,
  cacheRead: day.cacheRead + tokens.cacheRead,
  cacheWrite: day.cacheWrite + tokens.cacheWrite,
  usd: day.usd + Math.max(0, usdDelta),
  turns: day.turns + 1,
  byModel: { ...day.byModel, [model]: (day.byModel[model] ?? 0) + tokensOf(tokens) },
})

/** The day keys to drop so that only the newest `keep` remain. */
export const expiredKeys = (keys: readonly string[], keep: number): string[] =>
  keys
    .filter(k => k.startsWith(DAY_PREFIX))
    .sort()
    .reverse()
    .slice(Math.max(1, keep))

/** The usd delta since the last reading; a drop (a new session's ledger) counts as zero. */
export const usdDelta = (last: number | null, now: number): number => (last === null ? 0 : Math.max(0, now - last))

/** The budget threshold just crossed (0.8 or 1), if any, given the highest already announced. */
export const crossedThreshold = (spent: number, budget: number, announced: number): number | undefined => {
  if (budget <= 0) return undefined
  const ratio = spent / budget
  const reached = ratio >= 1 ? 1 : ratio >= 0.8 ? 0.8 : 0
  return reached > announced ? reached : undefined
}
