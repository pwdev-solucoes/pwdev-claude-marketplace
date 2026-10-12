import type { PluginOptions } from 'claude-code'

export type Options = { dailyBudgetUsd: number; historyDays: number; showBand: boolean; autoOpenPane: boolean }

export const optionsOf = (o: PluginOptions): Options => ({
  dailyBudgetUsd: typeof o.dailyBudgetUsd === 'number' && o.dailyBudgetUsd > 0 ? o.dailyBudgetUsd : 0,
  historyDays: typeof o.historyDays === 'number' && o.historyDays >= 1 ? Math.floor(o.historyDays) : 30,
  showBand: o.showBand !== false,
  autoOpenPane: o.autoOpenPane === true,
})
