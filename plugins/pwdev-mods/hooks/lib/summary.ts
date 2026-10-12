import type { PwdevModsAgent, PwdevModsDay, PwdevModsSession, PwdevModsTotals } from '../../types'
import { isActive } from './agents'
import { compact, percent, shortModel, sparkline, tokensOf, usd } from './format'

/** The pane's content as markdown, for surfaces that draw no pane (VS Code, -p). */
export const summaryText = (
  session: PwdevModsSession | null,
  totals: PwdevModsTotals,
  agents: readonly PwdevModsAgent[],
  days: readonly PwdevModsDay[],
): string => {
  const lines = ['## pwdev-mods', '']
  if (session !== null) {
    lines.push(`- Contexto: ${percent(session.contextPercent)} (${compact(session.contextTokens ?? 0)} de ${compact(session.contextWindow)})`)
    lines.push(`- Custo da sessão: ${usd(session.usd)}`)
    for (const r of session.rateLimits) lines.push(`- Limite ${r.kind}: ${percent(r.percentUsed)}`)
  }
  lines.push(`- Turnos: ${totals.turns} · tokens ${compact(tokensOf(totals.all))}`)
  for (const [model, t] of Object.entries(totals.byModel)) lines.push(`  - ${shortModel(model)}: ${compact(tokensOf(t))}`)
  const active = agents.filter(isActive)
  lines.push(`- Subagentes: ${active.length} ativos de ${agents.length}`)
  for (const a of active) lines.push(`  - \`${a.id}\` ${a.type} — ${a.description} (${a.status})`)
  if (days.length > 0) {
    const today = days[days.length - 1]
    lines.push(`- Hoje: ${usd(today?.usd ?? 0)} · ${compact(today === undefined ? 0 : tokensOf(today))} tokens`)
    lines.push(`- Histórico (${days.length} dias): ${sparkline(days.map(tokensOf))}`)
  }
  return lines.join('\n')
}
