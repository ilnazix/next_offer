import { useEffect, useRef, useState } from 'react'

import { fetchClientOffers } from '../api/offers'
import { config } from '../config'
import type { Offer } from '../types'

export type OffersStatus = 'loading' | 'ready' | 'error'

interface UseClientOffersOptions {
  intervalMs?: number
}

interface UseClientOffersResult {
  offers: Offer[]
  status: OffersStatus
  error: string | null
}

export function useClientOffers(
  clientId: number,
  { intervalMs = config.pollingIntervalMs }: UseClientOffersOptions = {},
): UseClientOffersResult {
  const [offers, setOffers] = useState<Offer[]>([])
  const [status, setStatus] = useState<OffersStatus>('loading')
  const [error, setError] = useState<string | null>(null)
  const hasLoaded = useRef(false)

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
        setOffers(nextOffers)
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

  return { offers, status, error }
}
