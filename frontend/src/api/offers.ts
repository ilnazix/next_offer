import { config } from '../config'
import type { Offer, OffersResponse } from '../types'

export async function fetchClientOffers(
  clientId: number,
  signal?: AbortSignal,
): Promise<Offer[]> {
  const response = await fetch(
    `${config.apiBaseUrl}/api/v1/clients/${clientId}/offers`,
    {
      headers: { Accept: 'application/json' },
      signal,
    },
  )

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  const body = (await response.json()) as OffersResponse
  return body.offers
}
