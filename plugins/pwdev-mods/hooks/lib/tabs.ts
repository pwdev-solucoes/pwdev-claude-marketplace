import type { PwdevModsTab } from '../../types'

export const TABS: readonly { id: PwdevModsTab; label: string; hotkey: string }[] = [
  { id: 'overview', label: 'Visão geral', hotkey: 'v' },
  { id: 'agents', label: 'Subagentes', hotkey: 's' },
  { id: 'tokens', label: 'Tokens', hotkey: 't' },
  { id: 'history', label: 'Histórico', hotkey: 'h' },
]

export const isTab = (value: string): value is PwdevModsTab => TABS.some(t => t.id === value)

export const AGENT_STATUS: Readonly<Record<string, string>> = {
  pending: 'pendente',
  running: 'rodando',
  waiting: 'aguardando',
  idle: 'ocioso',
  completed: 'concluído',
  failed: 'falhou',
  killed: 'parado',
}
