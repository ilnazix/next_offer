import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { RightPanel } from '../src/components/RightPanel'
import type { SimulatedEventRecord } from '../src/events'
import type { Client, Offer } from '../src/types'

const clients: Client[] = [
  { id: 1, full_name: 'Иван Петров' },
  { id: 2, full_name: 'Мария Смирнова' },
]

const offer: Offer = {
  id: 7,
  type: 'purchase',
  title: 'Накопите на крупную покупку',
  subtitle: 'Откройте накопительный счёт для ремонта или отпуска',
  background_color: 'linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)',
  icon: '🏠',
  action_text: 'Открыть счёт',
  status: 'pending',
  created_at: null,
}

const lastEvent: SimulatedEventRecord = {
  type: 'purchase',
  label: 'Крупная покупка −80 000 ₽',
  eventId: 'event-1',
  at: '2026-11-14T10:00:00+00:00',
}

function renderPanel() {
  const onSelectClient = vi.fn()
  const onSimulateEvent = vi.fn()

  render(
    <RightPanel
      clients={clients}
      clientsError={null}
      selectedClientId={1}
      onSelectClient={onSelectClient}
      onSimulateEvent={onSimulateEvent}
      pendingEventType={null}
      eventError={null}
      lastEvent={lastEvent}
      lastOffer={offer}
      offerCount={3}
    />,
  )

  return { onSelectClient, onSimulateEvent }
}

describe('RightPanel event simulator', () => {
  it('offers buttons for all four simulator event types', () => {
    renderPanel()

    expect(screen.getByRole('button', { name: /зарплата/i })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /крупная покупка/i }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /смотрел вклады/i }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /высокий остаток/i }),
    ).toBeInTheDocument()
  })

  it('lets the operator choose a client and simulate an event', () => {
    const { onSelectClient, onSimulateEvent } = renderPanel()

    fireEvent.change(
      screen.getByRole('combobox', { name: /клиент для демонстрации/i }),
      { target: { value: '2' } },
    )
    expect(onSelectClient).toHaveBeenCalledWith(2)

    fireEvent.click(screen.getByRole('button', { name: /смотрел вклады/i }))
    expect(onSimulateEvent).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'deposit_view' }),
    )
  })

  it('shows the offer count and the last processed event', () => {
    renderPanel()

    expect(screen.getByText('Офферов').nextElementSibling).toHaveTextContent('3')
    expect(screen.getByText('Последнее событие').nextElementSibling).toHaveTextContent(
      'Крупная покупка −80 000 ₽',
    )
    expect(screen.getByText('Последний оффер').nextElementSibling).toHaveTextContent(
      offer.title,
    )
  })
})
