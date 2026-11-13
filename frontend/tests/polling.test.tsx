import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useClientOffers } from '../src/hooks/useClientOffers'
import type { Offer } from '../src/types'

function makeOffer(id: number, title: string): Offer {
  return {
    id,
    type: 'salary',
    title,
    subtitle: null,
    background_color: null,
    icon: null,
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

function OffersProbe({ clientId }: { clientId: number }) {
  const { offers } = useClientOffers(clientId, { intervalMs: 20 })
  return (
    <ul>
      {offers.map((offer) => (
        <li key={offer.id}>{offer.title}</li>
      ))}
    </ul>
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('useClientOffers', () => {
  it('replaces offers on the next poll without a reload', async () => {
    const first = makeOffer(1, 'Первый оффер')
    const second = makeOffer(2, 'Второй оффер')
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response([first]))
      .mockResolvedValue(response([second, first]))
    vi.stubGlobal('fetch', fetchMock)

    render(<OffersProbe clientId={1} />)

    expect(await screen.findByText(first.title)).toBeInTheDocument()
    expect(await screen.findByText(second.title)).toBeInTheDocument()
    expect(fetchMock.mock.calls[0][0]).toBe(
      'http://localhost:8000/api/v1/clients/1/offers',
    )
  })
})
