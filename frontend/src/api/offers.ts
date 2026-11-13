import { config } from '../config'
import type { FeedbackResponse, Offer, OfferAction, OffersResponse } from '../types'

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

export async function submitOfferFeedback(
  offerId: number,
  action: OfferAction,
): Promise<FeedbackResponse> {
  const response = await fetch(
    `${config.apiBaseUrl}/api/v1/offers/${offerId}/feedback`,
    {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ action }),
    },
  )

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return (await response.json()) as FeedbackResponse
}
