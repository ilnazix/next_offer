import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from '../src/App'
import type { Offer } from '../src/types'

function makeOffer(id: number, title: string): Offer {
  return {
    id,
    type: 'salary',
    title,
    subtitle: 'Отложите часть на накопительный счёт',
    background_color: 'linear-gradient(135deg, #7c3aed 0%, #db2777 100%)',
    icon: '💰',
    action_text: null,
    status: 'pending',
    created_at: null,
  }
}

function response(offers: Offer[]) {
  return {
    ok: true,
    status: 200,
    json: async () => ({ client_id: 1, offers }),
  } as Response
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('new offer toast', () => {
  it('appears from polling without a reload and stays in the carousel after closing', async () => {
    vi.useFakeTimers()
    const offer = makeOffer(2, 'Новый оффер из polling')
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response([]))
      .mockResolvedValue(response([offer]))
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.queryByTestId(`toast-${offer.id}`)).toBeNull()

    await act(async () => {
      vi.advanceTimersByTime(3000)
      await Promise.resolve()
      await Promise.resolve()
    })

    const toast = screen.getByTestId(`toast-${offer.id}`)
    expect(toast).toBeInTheDocument()

    const carousel = screen.getByLabelText('Активные персональные предложения')
    expect(within(carousel).getByText(offer.title)).toBeInTheDocument()

    fireEvent.click(within(toast).getByRole('button', { name: /закрыть/i }))

    expect(screen.queryByTestId(`toast-${offer.id}`)).toBeNull()
    expect(within(carousel).getByText(offer.title)).toBeInTheDocument()
  })
})
