import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderInput } from 'claude-code'

import type { PwdevModsDay, PwdevModsTurn } from '../types'
import { isActive, mergeAgents, spawnTypes } from './lib/agents'
import { bar, clip, compact, dayOf, duration, percent, shortModel, sparkline, tokensOf, usd } from './lib/format'
import { addToDay, crossedThreshold, DAY_PREFIX, emptyDay, expiredKeys, usdDelta } from './lib/history'
import { optionsOf, type Options } from './lib/options'
import { summaryText } from './lib/summary'
import { AGENT_STATUS, isTab, TABS } from './lib/tabs'
import { addTurn, cacheHitRate, EMPTY_TOTALS, fromUsage, pushTurn, type UsageCounts } from './lib/usage'

// Every function that reaches the engine through `$` lives in this file: the
// engine follows `$` only into functions declared beside the hooks.

// --- state ---
const PANE = 'pwdev-mods'

const tabState = atom({ plugin: 'pwdev-mods', key: 'tab' } as const, 'overview')
const turnsState = atom({ plugin: 'pwdev-mods', key: 'turns' } as const, [])
const totalsState = atom({ plugin: 'pwdev-mods', key: 'totals' } as const, EMPTY_TOTALS)
const agentsState = atom({ plugin: 'pwdev-mods', key: 'agents' } as const, [])
const agentMetaState = atom({ plugin: 'pwdev-mods', key: 'agentMeta' } as const, {})
const sessionState = atom({ plugin: 'pwdev-mods', key: 'session' } as const, null)
const lastUsdState = atom({ plugin: 'pwdev-mods', key: 'lastUsd' } as const, null)
const historyState = atom({ plugin: 'pwdev-mods', key: 'history' } as const, [])
const spawnTypeState = atom({ plugin: 'pwdev-mods', key: 'spawnType' } as const, 'general-purpose')
const spawnPromptState = atom({ plugin: 'pwdev-mods', key: 'spawnPrompt' } as const, '')
const agentTypesState = atom({ plugin: 'pwdev-mods', key: 'agentTypes' } as const, [])
const noticeState = atom({ plugin: 'pwdev-mods', key: 'notice' } as const, '')
const isBandHiddenState = atom({ plugin: 'pwdev-mods', key: 'isBandHidden' } as const, false)

// --- actions ---
/** Reads the live window, cost and rate limits; returns the session's USD so far. */
const refreshSession = async ($: EngineInterface): Promise<number> => {
  const u = await $.session.usage()
  const cost = u.cost?.usd ?? 0
  await update($, sessionState, () => ({
    ...(u.context.tokens === undefined ? {} : { contextTokens: u.context.tokens }),
    contextWindow: u.context.window,
    ...(u.context.percent === undefined ? {} : { contextPercent: u.context.percent }),
    usd: cost,
    rateLimits: u.rateLimits.map(r => ({
      kind: r.kind,
      percentUsed: r.percentUsed,
      ...(r.resetsAt === undefined ? {} : { resetsAt: r.resetsAt }),
    })),
  }))
  return cost
}

const refreshAgents = async ($: EngineInterface): Promise<void> => {
  const listed = await $.agent.list()
  const meta = await read($, agentMetaState)
  await update($, agentsState, previous => mergeAgents(listed, meta, previous))
}

/** The session's custom agent types, from the free local /context estimate. */
const refreshAgentTypes = async ($: EngineInterface): Promise<void> => {
  const u = await $.session.usage({ breakdown: 'summary' })
  const custom = u.context.breakdown?.agents.map(a => a.agentType) ?? []
  await update($, agentTypesState, () => custom)
}

const dayKey = (date: string): string => `${DAY_PREFIX}${date}`

const readDay = async ($: EngineInterface, date: string): Promise<PwdevModsDay> => {
  const stored = (await $.store.get(dayKey(date))) as PwdevModsDay | undefined
  return stored ?? emptyDay(date)
}

/** Loads the kept days into the drawing state and drops the expired ones. */
const loadHistory = async ($: EngineInterface, keep: number): Promise<void> => {
  const keys = await $.store.keys()
  for (const key of expiredKeys(keys, keep)) await $.store.delete(key)
  const kept = keys
    .filter(k => k.startsWith(DAY_PREFIX))
    .sort()
    .slice(-keep)
  const days: PwdevModsDay[] = []
  for (const key of kept) {
    const day = (await $.store.get(key)) as PwdevModsDay | undefined
    if (day) days.push(day)
  }
  await update($, historyState, () => days)
}

/** Folds a finished turn into the session totals, today's bucket and the budget check. */
const recordTurn = async (
  $: EngineInterface,
  e: { turnId: string; agentId?: string; usage?: UsageCounts & { model: string } },
  options: Options,
): Promise<void> => {
  if (e.usage === undefined) return
  const now = await $.clock.now()
  const turn: PwdevModsTurn = {
    ...fromUsage(e.usage),
    turnId: e.turnId,
    ...(e.agentId === undefined ? {} : { agentId: e.agentId }),
    model: e.usage.model,
    at: now,
  }
  await update($, turnsState, list => pushTurn(list, turn))
  const agentId = e.agentId
  if (agentId !== undefined) {
    // A subagent the agent.spawn hook did not see (spawned before this load) still gets a row.
    await update($, agentMetaState, meta => (meta[agentId] === undefined ? { ...meta, [agentId]: { model: turn.model, startedAt: now } } : meta))
  }
  await update($, totalsState, t => addTurn(t, turn))

  const cost = await refreshSession($)
  const last = await read($, lastUsdState)
  const delta = usdDelta(last, cost)
  await update($, lastUsdState, () => cost)

  const date = dayOf(now)
  const day = addToDay(await readDay($, date), turn, turn.model, delta)
  await $.store.set(dayKey(date), day)
  await update($, historyState, days => [...days.filter(d => d.date !== date), day].sort((a, b) => a.date.localeCompare(b.date)).slice(-options.historyDays))

  const announcedKey = `budget:${date}`
  const announced = ((await $.store.get(announcedKey)) as number | undefined) ?? 0
  const crossed = crossedThreshold(day.usd, options.dailyBudgetUsd, announced)
  if (crossed !== undefined) {
    await $.store.set(announcedKey, crossed)
    $.ui.toast(
      crossed >= 1
        ? `pwdev-mods: orçamento diário estourado — ${usd(day.usd)} de ${usd(options.dailyBudgetUsd)}`
        : `pwdev-mods: 80% do orçamento diário — ${usd(day.usd)} de ${usd(options.dailyBudgetUsd)}`,
    )
  }
}

const stopAgent = async ($: EngineInterface, id: string): Promise<void> => {
  const ran = await $.tool.call({ tool: 'TaskStop', task_id: id })
  const message =
    ran.deny !== undefined
      ? `Parada recusada: ${ran.deny}`
      : ran.isError === true
        ? `Falha ao parar ${id}: ${clip(ran.text ?? '', 120)}`
        : `Subagente ${id} parado.`
  await update($, noticeState, () => message)
  await refreshAgents($)
}

const spawnAgent = async ($: EngineInterface, promptText?: string): Promise<void> => {
  const prompt = (promptText ?? (await read($, spawnPromptState))).trim()
  if (prompt === '') {
    await update($, noticeState, () => 'Escreva o prompt do subagente antes de disparar.')
    return
  }
  const subagentType = await read($, spawnTypeState)
  const started = await $.agent.spawn({ prompt, subagentType, description: `pwdev-mods: ${clip(prompt, 40)}` })
  const message =
    started.deny !== undefined
      ? `Disparo recusado: ${started.deny}`
      : `Subagente ${subagentType} disparado${started.agentId === undefined ? '' : ` (${started.agentId})`}.`
  await update($, noticeState, () => message)
  if (started.deny === undefined) await update($, spawnPromptState, () => '')
  $.ui.toast(`pwdev-mods: ${message}`)
  await refreshAgents($)
}

// --- pane ---
const drawPane = async ($: EngineInterface, e: RenderInput<'Pane'>) => {
  const { Box, Text, Button } = $.ui.resolve(e)
  const width = Math.max(30, e.props.bodyColumns)
  const current = await read($, tabState)
  const message = await read($, noticeState)

  const header = (
    <Box flexDirection="row" gap={1} flexWrap="wrap">
      {TABS.map(t => (
        <Button
          key={`tab-${t.id}`}
          label={t.label}
          hotkey={t.hotkey}
          variant={t.id === current ? 'primary' : 'secondary'}
          onPress={() => update($, tabState, () => t.id)}
        />
      ))}
    </Box>
  )

  const body = await (async () => {
    if (current === 'overview') {
      const s = await read($, sessionState)
      const totals = await read($, totalsState)
      const list = await read($, agentsState)
      const days = await read($, historyState)
      const date = dayOf(await $.clock.now())
      const today = days.find(d => d.date === date)
      const ctxRatio = (s?.contextPercent ?? 0) / 100
      return (
        <Box flexDirection="column">
          <Text bold>Contexto</Text>
          <Text color={ctxRatio >= 0.8 ? 'error' : ctxRatio >= 0.6 ? 'warning' : 'success'}>
            {bar(ctxRatio, Math.min(30, width - 20))} {percent(s?.contextPercent)}
          </Text>
          <Text dimColor>
            {compact(s?.contextTokens ?? 0)} de {compact(s?.contextWindow ?? 0)} tokens
          </Text>
          <Text bold>Custo</Text>
          <Text>
            Sessão {usd(s?.usd ?? 0)} · Hoje {usd(today?.usd ?? 0)} · {totals.turns} turnos · {compact(tokensOf(totals.all))} tokens
          </Text>
          {(s?.rateLimits.length ?? 0) > 0 && <Text bold>Limites</Text>}
          {(s?.rateLimits ?? []).map(r => (
            <Text color={r.percentUsed >= 80 ? 'warning' : 'text'}>
              {r.kind.padEnd(10)} {bar(r.percentUsed / 100, 20)} {percent(r.percentUsed)}
            </Text>
          ))}
          <Text bold>Subagentes</Text>
          <Text>
            {list.filter(isActive).length} ativos · {list.length} na sessão
          </Text>
        </Box>
      )
    }

    if (current === 'agents') {
      const list = await read($, agentsState)
      const totals = await read($, totalsState)
      const now = await $.clock.now()
      const rows = list.map(a => {
        const spent = totals.byAgent[a.id]
        const age = a.startedAt === undefined || !isActive(a) ? '' : ` · ${duration(now - a.startedAt)}`
        const model = a.model === undefined ? '' : ` · ${shortModel(a.model)}`
        const used = spent === undefined ? '' : ` · ${compact(tokensOf(spent))} tok`
        return (
          <Box key={`agent-${a.id}`} flexDirection="row" gap={1}>
            <Text color={isActive(a) ? 'success' : 'inactive'}>{AGENT_STATUS[a.status] ?? a.status}</Text>
            <Text>
              {clip(`${a.type}${a.description === '' ? '' : ` — ${a.description}`}${model}${age}${used}`, Math.max(10, width - 24))}
            </Text>
            {isActive(a) && <Button key={`stop-${a.id}`} label="Parar" onPress={() => stopAgent($, a.id)} />}
          </Box>
        )
      })

      const form =
        e.surface === 'mobile'
          ? null
          : await (async () => {
              const { Input, Select } = $.ui.resolve(e)
              const types = spawnTypes(await read($, agentTypesState))
              const chosen = await read($, spawnTypeState)
              const draft = await read($, spawnPromptState)
              return (
                <Box flexDirection="column" marginTop={1}>
                  <Text bold>Disparar subagente</Text>
                  <Select
                    key="spawn-type"
                    label="Tipo"
                    value={chosen}
                    options={types.map(t => ({ value: t }))}
                    onSelect={value => update($, spawnTypeState, () => value)}
                  />
                  <Input
                    key="spawn-prompt"
                    label="Prompt"
                    placeholder="O que o subagente deve fazer"
                    value={draft}
                    submitLabel="Disparar"
                    onInput={value => update($, spawnPromptState, () => value)}
                    onSubmit={value => spawnAgent($, value)}
                  />
                </Box>
              )
            })()

      return (
        <Box flexDirection="column">
          {rows.length === 0 && <Text dimColor>Nenhum subagente nesta sessão.</Text>}
          {rows}
          {form}
        </Box>
      )
    }

    if (current === 'tokens') {
      const totals = await read($, totalsState)
      const recent = (await read($, turnsState)).slice(-Math.max(3, (e.viewport?.rows ?? 24) - 18)).reverse()
      const hit = cacheHitRate(totals.all)
      return (
        <Box flexDirection="column">
          <Text bold>Sessão</Text>
          <Text>
            entrada {compact(totals.all.input)} · saída {compact(totals.all.output)} · cache lido {compact(totals.all.cacheRead)} · cache escrito{' '}
            {compact(totals.all.cacheWrite)}
          </Text>
          <Text dimColor>cache hit {hit === undefined ? '—' : percent(hit * 100)}</Text>
          <Text bold>Por modelo</Text>
          {Object.entries(totals.byModel).map(([model, t]) => (
            <Text>
              {shortModel(model).padEnd(18)} {compact(tokensOf(t)).padStart(7)} · saída {compact(t.output)}
            </Text>
          ))}
          <Text bold>Por loop</Text>
          {Object.entries(totals.byAgent).map(([agent, t]) => (
            <Text>
              {clip(agent === 'main' ? 'principal' : agent, 18).padEnd(18)} {compact(tokensOf(t)).padStart(7)}
            </Text>
          ))}
          <Text bold>Últimos turnos</Text>
          {recent.length === 0 && <Text dimColor>Nenhum turno ainda.</Text>}
          {recent.map(t => (
            <Text dimColor={t.agentId !== undefined}>
              {shortModel(t.model).padEnd(16)} in {compact(t.input).padStart(6)} out {compact(t.output).padStart(6)} cr{' '}
              {compact(t.cacheRead).padStart(6)} cw {compact(t.cacheWrite).padStart(6)}
              {t.agentId === undefined ? '' : ' · sub'}
            </Text>
          ))}
        </Box>
      )
    }

    const days = await read($, historyState)
    const shown = days.slice(-Math.max(7, Math.min(days.length, width - 10)))
    return (
      <Box flexDirection="column">
        {days.length === 0 && <Text dimColor>Sem histórico ainda: ele começa no primeiro turno.</Text>}
        {days.length > 0 && (
          <Box flexDirection="column">
            <Text bold>Tokens por dia ({shown.length} dias)</Text>
            <Text color="claude">{sparkline(shown.map(tokensOf))}</Text>
            <Text bold>Custo por dia</Text>
            <Text color="suggestion">{sparkline(shown.map(d => d.usd))}</Text>
            <Text dimColor>
              Total do período {usd(shown.reduce((sum, d) => sum + d.usd, 0))} · {compact(shown.reduce((sum, d) => sum + tokensOf(d), 0))} tokens
            </Text>
          </Box>
        )}
        {shown
          .slice(-10)
          .reverse()
          .map(d => (
            <Text>
              {d.date} {usd(d.usd).padStart(8)} {compact(tokensOf(d)).padStart(7)} tok {String(d.turns).padStart(4)} turnos
            </Text>
          ))}
      </Box>
    )
  })()

  return (
    <Box flexDirection="column" gap={1}>
      {header}
      {body}
      {message !== '' && <Text color="suggestion">{message}</Text>}
    </Box>
  )
}

// --- band ---
/** The one-line band above the prompt, or undefined to leave the band to the engine. */
const drawBand = async ($: EngineInterface, e: RenderInput<'AbovePrompt'>) => {
  if (e.props.hasSurvey || (await read($, isBandHiddenState))) return undefined
  const s = await read($, sessionState)
  if (s === null) return undefined
  const date = dayOf(await $.clock.now())
  const today = (await read($, historyState)).find(d => d.date === date)
  const active = (await read($, agentsState)).filter(isActive).length
  const ctx = s.contextPercent ?? 0
  const { Box, Text, Button } = $.ui.resolve(e)

  return (
    <Box flexDirection="row" gap={1}>
      <Text dimColor>pwdev-mods</Text>
      <Text color={ctx >= 80 ? 'error' : ctx >= 60 ? 'warning' : 'text'}>ctx {percent(s.contextPercent)}</Text>
      <Text dimColor>·</Text>
      <Text>sessão {usd(s.usd)}</Text>
      <Text dimColor>·</Text>
      <Text>hoje {usd(today?.usd ?? 0)}</Text>
      <Text dimColor>·</Text>
      <Text color={active > 0 ? 'success' : 'inactive'}>{active} subagentes ativos</Text>
      <Button key="band-hide" plain label="ocultar" onPress={() => update($, isBandHiddenState, () => true)} />
    </Box>
  )
}

// --- hooks ---
const POLL_MS = 2000

const summary = async ($: EngineInterface): Promise<string> =>
  summaryText(await read($, sessionState), await read($, totalsState), await read($, agentsState), await read($, historyState))

export const register: Register = (on, rawOptions) => {
  const options = optionsOf(rawOptions)
  // Whether a surface draws panes in this session (false under -p, the SDK, VS Code).
  let draws = true

  on('session.start', async ($, e, next) => {
    draws = e.isInteractive && (e.surface === 'terminal' || e.surface === 'desktop')
    await $.command.register({
      name: 'pwdev-mods',
      description: 'Painel de gestão: subagentes, tokens, custo e histórico',
      argumentHint: TABS.map(t => t.id).join('|'),
      immediate: true,
    })

    const cost = await refreshSession($)
    if ((await read($, lastUsdState)) === null) await update($, lastUsdState, () => cost)
    await loadHistory($, options.historyDays)
    await refreshAgents($)

    $.clock.every(POLL_MS, () => {
      void (async () => {
        const panes = await $.ui.panes()
        const isShown = panes.some(p => p.id === PANE && p.isShown)
        const hasActive = (await read($, agentsState)).some(isActive)
        if (isShown || hasActive) {
          await refreshAgents($)
          await refreshSession($)
        }
      })().catch(() => undefined)
    })

    if (options.autoOpenPane && draws) void $.ui.open({ id: PANE, title: 'pwdev-mods' })

    return next(e)
  })

  on('command.run', { command: 'pwdev-mods' }, async ($, e) => {
    const wanted = e.args.trim().toLowerCase()
    if (wanted !== '' && !isTab(wanted)) {
      return { text: `Aba desconhecida "${wanted}". Use: ${TABS.map(t => t.id).join(', ')}.` }
    }
    if (isTab(wanted)) await update($, tabState, () => wanted)

    await refreshSession($)
    await refreshAgents($)

    if (!draws) return { text: await summary($) }

    await refreshAgentTypes($)
    const opened = await $.ui.open({ id: PANE, title: 'pwdev-mods', focus: true })
    if (!opened.isPlaced) return { text: `${await summary($)}\n\n_Painel aguardando espaço: ${opened.reason}_` }
    return { text: 'Painel pwdev-mods aberto (ctrl+x x fecha).' }
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    await recordTurn($, e, options)
    return result
  }).catch(($, e, next) => next(e))

  on('agent.spawn', async ($, e, next) => {
    const started = await next(e)
    if (started.deny === undefined && started.agentId !== undefined) {
      const id = started.agentId
      const startedAt = await $.clock.now()
      await update($, agentMetaState, meta => ({ ...meta, [id]: { model: started.model, startedAt, type: e.subagentType, description: e.description } }))
      await refreshAgents($)
    }
    return started
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => drawPane($, e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (!options.showBand) return next(e)
    return (await drawBand($, e)) ?? next(e)
  })
}
