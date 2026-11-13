import type { EventPayload } from './api/events'

export type SimulatorEventType =
  | 'salary'
  | 'purchase'
  | 'deposit_view'
  | 'high_balance'

export interface SimulatorEvent {
  type: SimulatorEventType
  label: string
  payload: EventPayload
  secondary?: boolean
}

export const SIMULATOR_EVENTS: SimulatorEvent[] = [
  {
    type: 'salary',
    label: 'Пришла зарплата +150 000 ₽',
    payload: { amount: 150000 },
  },
  {
    type: 'purchase',
    label: 'Крупная покупка −80 000 ₽',
    payload: { amount: 80000, category: 'home_improvement' },
  },
  {
    type: 'deposit_view',
    label: 'Смотрел вклады',
    payload: { product_category: 'deposit' },
    secondary: true,
  },
  {
    type: 'high_balance',
    label: 'Высокий остаток',
    payload: { balance: 250000 },
    secondary: true,
  },
]
