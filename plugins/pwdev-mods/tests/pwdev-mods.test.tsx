import { describe, expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import { mergeAgents, spawnTypes } from '../hooks/lib/agents'
import { bar, compact, dayOf, sparkline } from '../hooks/lib/format'
import { addToDay, crossedThreshold, emptyDay, expiredKeys, usdDelta } from '../hooks/lib/history'
import { optionsOf } from '../hooks/lib/options'
import { addTurn, cacheHitRate, EMPTY_TOTALS } from '../hooks/lib/usage'

const PLUGIN = 'pwdev-mods'
const SURFACES = ['terminal', 'desktop'] as const
// 2026-10-12 12:00 local time
const NOON = new Date(2026, 9, 12, 12).getTime()

type Fake = { toasts: string[]; usd: number; agents: { id: string; type: string; description: string; status: 'running' | 'completed' }[]; stopped: string[]; spawned: string[] }

/** The engine beneath the plugin: usage, agents, panes, commands, the store and the clock. */
const engine = (on: On, fake: Fake) => {
  mock.store(on)
  const clock = mock.clock(on, { now: NOON })
  on('session.usage', () => ({
    value: {
      startedAt: NOON,
      context: { tokens: 42_000, window: 200_000, percent: 21 },
      rateLimits: [{ kind: 'five_hour', percentUsed: 35, source: 'api' }],
      cost: { usd: fake.usd },
    },
  }))
  on('agent.list', () => ({ value: fake.agents }))
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('ui.toast', ($, e) => {
    fake.toasts.push(e.text)
    return { value: undefined }
  })
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('command.register', ($, e) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('ui.panes', () => ({ value: [] }))
  on('tool.call', { tool: 'TaskStop' }, ($, e) => {
    fake.stopped.push(String(e.task_id))
    return { result: { message: 'stopped', task_id: String(e.task_id), task_type: 'local_agent' } }
  })
  on('agent.spawn', ($, e) => {
    // The kit raises a plugin's spawn in the Agent tool's spelling (subagent_type).
    const type = (e as { subagent_type?: string }).subagent_type ?? e.subagentType
    fake.spawned.push(`${type}:${e.prompt}`)
    return { model: 'claude-haiku-5-5', agentId: 'a-new' }
  })
  return clock
}

const RUN = { command: 'pwdev-mods', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } } as const

const freshFake = (): Fake => ({ toasts: [], usd: 0, agents: [], stopped: [], spawned: [] })

const usage = (input: number, output: number, model = 'claude-opus-5-5') => ({
  input_tokens: input,
  output_tokens: output,
  cache_read_input_tokens: 0,
  cache_creation_input_tokens: 0,
  model,
})

const PANE = { plugin: PLUGIN, component: 'Pane', requestId: PLUGIN, props: { title: 'pwdev-mods', isFocused: true, bodyColumns: 100, placement: 'dock', scroll: { offset: 0, bodyRows: 40 }, view: {} } } as const

describe('pure helpers', () => {
  test('formats tokens, bars and sparklines', () => {
    expect(compact(950)).toBe('950')
    expect(compact(1_500)).toBe('1.5k')
    expect(compact(2_500_000)).toBe('2.5M')
    expect(bar(0.5, 10)).toBe('█████░░░░░')
    expect(sparkline([0, 5, 10])).toBe('▁▄█')
    expect(dayOf(NOON)).toBe('2026-10-12')
  })

  test('totals turns per model and per agent loop', () => {
    const turn = (agentId?: string) => ({ turnId: 't', model: 'm', at: 0, input: 10, output: 5, cacheRead: 30, cacheWrite: 0, ...(agentId ? { agentId } : {}) })
    const t = addTurn(addTurn(EMPTY_TOTALS, turn()), turn('a1'))
    expect(t.turns).toBe(2)
    expect(t.byAgent.main?.input).toBe(10)
    expect(t.byAgent.a1?.output).toBe(5)
    expect(t.byModel.m?.cacheRead).toBe(60)
    expect(cacheHitRate(t.all)).toBe(0.75)
  })

  test('keeps the newest days and announces each budget threshold once', () => {
    expect(expiredKeys(['daily:2026-10-10', 'daily:2026-10-12', 'budget:x', 'daily:2026-10-11'], 2)).toEqual(['daily:2026-10-10'])
    expect(usdDelta(null, 3)).toBe(0)
    expect(usdDelta(1, 3)).toBe(2)
    expect(usdDelta(5, 1)).toBe(0)
    expect(crossedThreshold(8, 10, 0)).toBe(0.8)
    expect(crossedThreshold(9, 10, 0.8)).toBeUndefined()
    expect(crossedThreshold(10, 10, 0.8)).toBe(1)
    expect(crossedThreshold(10, 0, 0)).toBeUndefined()
    const day = addToDay(emptyDay('2026-10-12'), { input: 1, output: 2, cacheRead: 3, cacheWrite: 4 }, 'm', 0.5)
    expect(day.byModel.m).toBe(10)
    expect(day.usd).toBe(0.5)
  })

  test('lists active agents first and offers built-in types before custom ones', () => {
    const merged = mergeAgents(
      [
        { id: 'old', type: 'Explore', description: 'x', status: 'completed' },
        { id: 'live', type: 'Plan', description: 'y', status: 'running' },
      ],
      { live: { model: 'claude-opus-5-5', startedAt: 1 } },
    )
    expect(merged.map(a => a.id)).toEqual(['live', 'old'])
    expect(merged[0]?.model).toBe('claude-opus-5-5')
    expect(spawnTypes(['Explore', 'pwdev-code:executor'])).toEqual(['general-purpose', 'Explore', 'Plan', 'pwdev-code:executor'])
  })

  test('keeps subagents the engine stopped listing, marked completed', () => {
    const seen = mergeAgents([{ id: 'a1', type: 'Explore', description: 'busca', status: 'running' }], {})
    const later = mergeAgents([], { a2: { startedAt: 5, type: 'Plan', description: 'plano' } }, seen)
    expect(later.map(a => `${a.id}:${a.type}:${a.status}`)).toEqual(['a2:Plan:completed', 'a1:Explore:completed'])
  })

  test('reads options with defaults', () => {
    expect(optionsOf({})).toEqual({ dailyBudgetUsd: 0, historyDays: 30, showBand: true, autoOpenPane: false })
    expect(optionsOf({ dailyBudgetUsd: 5, historyDays: 7.9, showBand: false })).toEqual({ dailyBudgetUsd: 5, historyDays: 7, showBand: false, autoOpenPane: false })
  })
})

describe('the mod in a session', () => {
  test('records turns into the session totals and today\'s history', async ($, on) => {
    const fake = freshFake()
    engine(on, fake)
    await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

    fake.usd = 0.4
    await $.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer', usage: usage(1_000, 200) })
    fake.usd = 0.5
    await $.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't2', agentId: 'a1', reason: 'answer', usage: usage(500, 100, 'claude-haiku-5-5') })


    for (const surface of SURFACES) {
      const ui = await $.ui.mount({ ...PANE, surface })
      expect(await ui.find({ type: 'Text', text: /Sessão \$0\.50/ })).toBeDefined()
      await ui.press({ key: 'tab-tokens' })
      expect(await ui.find({ type: 'Text', text: /haiku-5-5/ })).toBeDefined()
      await ui.press({ key: 'tab-history' })
      expect(await ui.find({ type: 'Text', text: /2026-10-12 +\$0\.50 +1\.8k tok +2 turnos/ })).toBeDefined()
      await ui.press({ key: 'tab-overview' })
      await ui.unmount()
    }
  })

  test('warns once at 80% of the daily budget', { options: { dailyBudgetUsd: 1 } }, async ($, on) => {
    const fake = freshFake()
    engine(on, fake)
    await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
    fake.usd = 0.85
    await $.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer', usage: usage(10, 10) })
    fake.usd = 0.9
    await $.turn.complete({ answer: 'ok', durationMs: 1, isAborted: false, turnId: 't2', reason: 'answer', usage: usage(10, 10) })
    expect(fake.toasts.filter(t => t.includes('80%'))).toHaveLength(1)
  })

  test('stops a running subagent and spawns a new one from the pane', async ($, on) => {
    const fake = freshFake()
    fake.agents = [{ id: 'a1', type: 'Explore', description: 'procura testes', status: 'running' }]
    engine(on, fake)
    await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

    for (const surface of SURFACES) {
      fake.stopped.length = 0
      fake.spawned.length = 0
      const ui = await $.ui.mount({ ...PANE, surface })
      await ui.press({ key: 'tab-agents' })
      expect(await ui.find({ type: 'Text', text: /procura testes/ })).toBeDefined()
      await ui.press({ key: 'stop-a1' })
      expect(fake.stopped).toEqual(['a1'])
      await ui.select({ key: 'spawn-type', value: 'Plan' })
      await ui.input({ key: 'spawn-prompt', text: 'planeje a migração' })
      expect(fake.spawned).toEqual(['Plan:planeje a migração'])
      expect(await ui.find({ type: 'Text', text: /Subagente Plan disparado/ })).toBeDefined()
      await ui.press({ key: 'tab-overview' })
      await ui.unmount()
    }
  })

  test('answers the command with a text summary where nothing draws panes', async ($, on) => {
    engine(on, freshFake())
    await $.session.start({ cwd: '/', surface: null, isInteractive: false })
    const ran = await $.command.run({ ...RUN, args: '' })
    expect(ran.text).toContain('## pwdev-mods')
    expect(ran.text).toContain('Contexto: 21%')
    const wrong = await $.command.run({ ...RUN, args: 'nada' })
    expect(wrong.text).toContain('Aba desconhecida')
  })
})
