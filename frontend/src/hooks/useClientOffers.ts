import { useCallback, useEffect, useRef, useState } from 'react'

import { fetchClientOffers, submitOfferFeedback } from '../api/offers'
import { config } from '../config'
import type { Offer, OfferAction } from '../types'

export type OffersStatus = 'loading' | 'ready' | 'error'

interface UseClientOffersOptions {
  intervalMs?: number
}

interface UseClientOffersResult {
  offers: Offer[]
  status: OffersStatus
  error: string | null
  loadedClientId: number | null
  respondToOffer: (offerId: number, action: OfferAction) => Promise<void>
}

export function useClientOffers(
  clientId: number,
  { intervalMs = config.pollingIntervalMs }: UseClientOffersOptions = {},
): UseClientOffersResult {
  const [offers, setOffers] = useState<Offer[]>([])
  const [status, setStatus] = useState<OffersStatus>('loading')
  const [error, setError] = useState<string | null>(null)
  const [loadedClientId, setLoadedClientId] = useState<number | null>(null)
  const hasLoaded = useRef(false)
  const respondedOfferIds = useRef(new Set<number>())

  useEffect(() => {
    let cancelled = false
    let controller: AbortController | null = null

    async function load() {
      controller?.abort()
      controller = new AbortController()

      try {
        const nextOffers = await fetchClientOffers(clientId, controller.signal)
        if (cancelled) return

        hasLoaded.current = true
        setOffers(
          nextOffers.filter((offer) => !respondedOfferIds.current.has(offer.id)),
        )
        setLoadedClientId(clientId)
        setError(null)
        setStatus('ready')
      } catch (cause) {
        if (cancelled || (cause as Error).name === 'AbortError') return

        setError(cause instanceof Error ? cause.message : 'unknown error')
        setStatus(hasLoaded.current ? 'ready' : 'error')
      }
    }

    void load()
    const timer = window.setInterval(() => {
      void load()
    }, intervalMs)

    return () => {
      cancelled = true
      controller?.abort()
      window.clearInterval(timer)
    }
  }, [clientId, intervalMs])

  const respondToOffer = useCallback(
    async (offerId: number, action: OfferAction) => {
      try {
        await submitOfferFeedback(offerId, action)
        respondedOfferIds.current.add(offerId)
        setOffers((current) =>
          current.filter((offer) => offer.id !== offerId),
        )
        setError(null)
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : 'unknown error')
      }
    },
    [],
  )

  const visibleOffers = loadedClientId === clientId ? offers : []

  return {
    offers: visibleOffers,
    status,
    error,
    loadedClientId,
    respondToOffer,
  }
}
