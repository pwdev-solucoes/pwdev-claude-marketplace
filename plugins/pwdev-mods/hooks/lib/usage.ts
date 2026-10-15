import type { PwdevModsTokens, PwdevModsTotals, PwdevModsTurn } from '../../types'

export const MAX_TURNS = 50

export const ZERO: PwdevModsTokens = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }

export const EMPTY_TOTALS: PwdevModsTotals = { all: ZERO, turns: 0, byModel: {}, byAgent: {} }

export type UsageCounts = {
  input_tokens: number
  output_tokens: number
  cache_read_input_tokens: number
  cache_creation_input_tokens: number
}

export const fromUsage = (u: UsageCounts): PwdevModsTokens => ({
  input: u.input_tokens,
  output: u.output_tokens,
  cacheRead: u.cache_read_input_tokens,
  cacheWrite: u.cache_creation_input_tokens,
})

export const add = (a: PwdevModsTokens, b: PwdevModsTokens): PwdevModsTokens => ({
  input: a.input + b.input,
  output: a.output + b.output,
  cacheRead: a.cacheRead + b.cacheRead,
  cacheWrite: a.cacheWrite + b.cacheWrite,
})

/** The agent key a turn is totalled under: its loop's id, or 'main'. */
export const agentKey = (turn: Pick<PwdevModsTurn, 'agentId'>): string => turn.agentId ?? 'main'

export const addTurn = (totals: PwdevModsTotals, turn: PwdevModsTurn): PwdevModsTotals => {
  const key = agentKey(turn)
  return {
    all: add(totals.all, turn),
    turns: totals.turns + 1,
    byModel: { ...totals.byModel, [turn.model]: add(totals.byModel[turn.model] ?? ZERO, turn) },
    byAgent: { ...totals.byAgent, [key]: add(totals.byAgent[key] ?? ZERO, turn) },
  }
}

export const pushTurn = (turns: readonly PwdevModsTurn[], turn: PwdevModsTurn): PwdevModsTurn[] =>
  [...turns, turn].slice(-MAX_TURNS)

/** Share of input served from the prompt cache, 0..1; undefined with no input yet. */
export const cacheHitRate = (t: PwdevModsTokens): number | undefined => {
  const input = t.input + t.cacheRead + t.cacheWrite
  return input === 0 ? undefined : t.cacheRead / input
}
