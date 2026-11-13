import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from '../src/App'
import type { Offer } from '../src/types'

const offer: Offer = {
  id: 7,
  type: 'salary',
  title: 'Сохраните зарплату под 8%',
  subtitle: 'Отложите часть на накопительный счёт',
  background_color: 'linear-gradient(135deg, #7c3aed 0%, #db2777 100%)',
  icon: '💰',
  action_text: 'Открыть счёт',
  status: 'pending',
  created_at: null,
}

function jsonResponse(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => body,
  } as Response
}

function installFetchMock() {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)

    if (url.endsWith('/api/v1/offers/7/feedback')) {
      const body = JSON.parse(String(init?.body)) as { action: string }
      return jsonResponse({
        id: 7,
        status: body.action,
        responded_at: '2026-11-14T10:00:00Z',
      })
    }

    return jsonResponse({ client_id: 1, offers: [offer] })
  })

  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('offer feedback', () => {
  it.each([
    { button: 'Открыть счёт', action: 'accepted' },
    { button: 'Отклонить', action: 'declined' },
    { button: 'Закрыть предложение', action: 'dismissed' },
  ])('sends "$action" and removes the offer from the carousel', async ({ button, action }) => {
    const fetchMock = installFetchMock()

    render(<App />)

    expect(
      await screen.findByRole('heading', { name: offer.title }),
    ).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: button }))

    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: offer.title }),
      ).not.toBeInTheDocument()
    })

    const feedbackCall = fetchMock.mock.calls.find(([input]) =>
      String(input).endsWith('/api/v1/offers/7/feedback'),
    )

    expect(feedbackCall).toBeDefined()
    expect(feedbackCall?.[1]).toMatchObject({
      method: 'POST',
      body: JSON.stringify({ action }),
    })
  })
})
