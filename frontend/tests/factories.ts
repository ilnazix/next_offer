import type { Offer } from '../src/types'

export function makeOffer(overrides: Partial<Offer> = {}): Offer {
  return {
    id: 7,
    type: 'salary',
    title: 'Сохраните зарплату под 8%',
    subtitle: 'Отложите часть на накопительный счёт',
    background_color: 'linear-gradient(135deg, #7c3aed 0%, #db2777 100%)',
    icon: '💰',
    action_text: 'Открыть счёт',
    status: 'pending',
    created_at: null,
    ...overrides,
  }
}
