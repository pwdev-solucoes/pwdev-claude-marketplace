import type { PwdevModsAgent, PwdevModsAgentMeta } from '../../types'

export const BUILTIN_TYPES = ['general-purpose', 'Explore', 'Plan'] as const

export const ACTIVE = new Set(['pending', 'running', 'waiting'])

export const isActive = (agent: Pick<PwdevModsAgent, 'status'>): boolean => ACTIVE.has(agent.status)

export type ListedAgent = {
  id: string
  type: string
  description: string
  status: string
  parentId?: string
}

/**
 * `$.agent.list()` rows joined with what agent.spawn recorded; active ones first.
 *
 * The engine drops a finished subagent from its list, so an agent seen before
 * (in `previous`) or spawned (in `meta`) and no longer listed is kept, marked
 * completed when it was last seen active.
 */
export const mergeAgents = (
  listed: readonly ListedAgent[],
  meta: Readonly<Record<string, PwdevModsAgentMeta>>,
  previous: readonly PwdevModsAgent[] = [],
): PwdevModsAgent[] => {
  const ids = new Set(listed.map(a => a.id))
  const gone: ListedAgent[] = [
    ...previous.filter(a => !ids.has(a.id)).map(a => ({ ...a, status: isActive(a) ? 'completed' : a.status })),
    ...Object.entries(meta)
      .filter(([id]) => !ids.has(id) && !previous.some(a => a.id === id))
      .map(([id, m]) => ({ id, type: m.type ?? 'subagente', description: m.description ?? '', status: 'completed' })),
  ]
  return [...listed, ...gone]
    .map(a => ({
      id: a.id,
      type: a.type,
      description: a.description,
      status: a.status,
      ...(a.parentId === undefined ? {} : { parentId: a.parentId }),
      ...(meta[a.id]?.model === undefined ? {} : { model: meta[a.id]?.model }),
      ...(meta[a.id] === undefined ? {} : { startedAt: meta[a.id]?.startedAt }),
    }))
    .sort((a, b) => Number(isActive(b)) - Number(isActive(a)) || (b.startedAt ?? 0) - (a.startedAt ?? 0))
    .slice(0, MAX_AGENTS)
}

export const MAX_AGENTS = 50

/** Agent types to offer for a spawn: the built-ins, then the session's custom ones. */
export const spawnTypes = (custom: readonly string[]): string[] => [...new Set([...BUILTIN_TYPES, ...custom])]
