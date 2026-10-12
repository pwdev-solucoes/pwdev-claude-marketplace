export type PwdevModsTab = 'overview' | 'agents' | 'tokens' | 'history'

/** The four token counts a response reports, summed. */
export type PwdevModsTokens = {
  input: number
  output: number
  cacheRead: number
  cacheWrite: number
}

/** One finished turn: the main loop's (no agentId) or a subagent's. */
export type PwdevModsTurn = PwdevModsTokens & {
  turnId: string
  agentId?: string
  model: string
  at: number
}

/** Session totals: overall, per model and per agent loop ('main' for the main one). */
export type PwdevModsTotals = {
  all: PwdevModsTokens
  turns: number
  byModel: Record<string, PwdevModsTokens>
  byAgent: Record<string, PwdevModsTokens>
}

/** One subagent as the pane lists it: `$.agent.list()` plus what agent.spawn told us. */
export type PwdevModsAgent = {
  id: string
  type: string
  description: string
  status: string
  parentId?: string
  model?: string
  startedAt?: number
}

/** What the plugin learnt at agent.spawn, kept by agent id. */
export type PwdevModsAgentMeta = { model?: string; startedAt: number; type?: string; description?: string }

export type PwdevModsRateLimit = { kind: string; percentUsed: number; resetsAt?: string }

/** The live window, cost and rate limits, as `$.session.usage()` answered last. */
export type PwdevModsSession = {
  contextTokens?: number
  contextWindow: number
  contextPercent?: number
  usd: number
  rateLimits: PwdevModsRateLimit[]
}

/** One day of consumption, persisted in `$.store` under `daily:YYYY-MM-DD`. */
export type PwdevModsDay = PwdevModsTokens & {
  date: string
  usd: number
  turns: number
  byModel: Record<string, number>
}

declare module 'claude-code' {
  interface PluginState {
    'pwdev-mods': {
      tab: PwdevModsTab
      turns: PwdevModsTurn[]
      totals: PwdevModsTotals
      agents: PwdevModsAgent[]
      agentMeta: Record<string, PwdevModsAgentMeta>
      session: PwdevModsSession | null
      lastUsd: number | null
      history: PwdevModsDay[]
      spawnType: string
      spawnPrompt: string
      agentTypes: string[]
      notice: string
      isBandHidden: boolean
    }
  }
}
