import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from '../src/App'
import { makeOffer } from './factories'

function jsonResponse(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => body,
  } as Response
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('new offer toast', () => {
  it('appears from polling without a reload and stays in the carousel after closing', async () => {
    vi.useFakeTimers()
    const offer = makeOffer({ id: 2, title: 'Новый оффер из polling' })
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ client_id: 1, offers: [] }))
      .mockResolvedValue(jsonResponse({ client_id: 1, offers: [offer] }))
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

  it('removes the matching toast when the offer is declined from the carousel', async () => {
    vi.useFakeTimers()
    const offer = makeOffer({ id: 2, title: 'Оффер, который отклоняют' })
    let offerPolls = 0

    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/api/v1/offers/2/feedback')) {
        return jsonResponse({
          id: 2,
          status: 'declined',
          responded_at: '2026-11-14T10:00:00Z',
        })
      }
      offerPolls += 1
      return jsonResponse({
        client_id: 1,
        offers: offerPolls === 1 ? [] : [offer],
      })
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    await act(async () => {
      await Promise.resolve()
    })

    await act(async () => {
      vi.advanceTimersByTime(3000)
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(screen.getByTestId(`toast-${offer.id}`)).toBeInTheDocument()

    const carousel = screen.getByLabelText('Активные персональные предложения')
    fireEvent.click(within(carousel).getByRole('button', { name: 'Отклонить' }))

    expect(screen.queryByTestId(`toast-${offer.id}`)).toBeNull()

    await act(async () => {
      await Promise.resolve()
      await Promise.resolve()
    })
    expect(
      screen.queryByRole('heading', { name: offer.title }),
    ).not.toBeInTheDocument()
  })
})
