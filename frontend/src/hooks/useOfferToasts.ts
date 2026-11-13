import { useCallback, useEffect, useRef, useState } from 'react'

import type { Offer } from '../types'

interface UseOfferToastsResult {
  toasts: Offer[]
  dismissToast: (offerId: number) => void
}

export function useOfferToasts(
  offers: Offer[],
  loadedClientId: number | null,
): UseOfferToastsResult {
  const [toasts, setToasts] = useState<Offer[]>([])
  const seenIds = useRef<Set<number>>(new Set())
  const loadedClientRef = useRef<number | null>(null)

  useEffect(() => {
    if (loadedClientId === null) return

    if (loadedClientRef.current !== loadedClientId) {
      loadedClientRef.current = loadedClientId
      seenIds.current = new Set(offers.map((offer) => offer.id))
      setToasts([])
      return
    }

    const freshOffers = offers.filter((offer) => !seenIds.current.has(offer.id))
    if (freshOffers.length === 0) return

    freshOffers.forEach((offer) => seenIds.current.add(offer.id))
    setToasts((current) => [...freshOffers, ...current])
  }, [offers, loadedClientId])

  const dismissToast = useCallback((offerId: number) => {
    setToasts((current) => current.filter((offer) => offer.id !== offerId))
  }, [])

  return { toasts, dismissToast }
}
