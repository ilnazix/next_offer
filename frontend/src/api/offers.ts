import type { FeedbackResponse, Offer, OfferAction, OffersResponse } from '../types'
import { fetchJson } from './http'

export async function fetchClientOffers(
  clientId: number,
  signal?: AbortSignal,
): Promise<Offer[]> {
  const body = await fetchJson<OffersResponse>(
    `/api/v1/clients/${clientId}/offers`,
    { signal },
  )
  return body.offers
}

export async function submitOfferFeedback(
  offerId: number,
  action: OfferAction,
): Promise<FeedbackResponse> {
  return fetchJson<FeedbackResponse>(`/api/v1/offers/${offerId}/feedback`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  })
}
