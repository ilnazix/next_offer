import { useCallback, useEffect, useRef, useState } from 'react'

import { config } from '../config'
import type { Offer } from '../types'

interface UseOfferToastsOptions {
  ready?: boolean
  timeoutMs?: number
  clientId?: number | null
}

interface UseOfferToastsResult {
  toasts: Offer[]
  dismissToast: (offerId: number) => void
}

export function useOfferToasts(
  offers: Offer[],
  {
    ready = true,
    timeoutMs = config.toastTimeoutMs,
    clientId,
  }: UseOfferToastsOptions = {},
): UseOfferToastsResult {
  const [toasts, setToasts] = useState<Offer[]>([])
  const seenOfferIds = useRef<Set<number>>(new Set())
  const hasSeeded = useRef(false)
  const loadedClientRef = useRef<number | null>(null)
  const timers = useRef<Map<number, number>>(new Map())

  useEffect(() => {
    if (!ready) return

    if (clientId != null && loadedClientRef.current !== clientId) {
      loadedClientRef.current = clientId
      seenOfferIds.current = new Set(offers.map((offer) => offer.id))
      hasSeeded.current = true
      setToasts([])
      return
    }

    if (!hasSeeded.current) {
      hasSeeded.current = true
      offers.forEach((offer) => seenOfferIds.current.add(offer.id))
      return
    }

    const freshOffers = offers.filter((offer) => !seenOfferIds.current.has(offer.id))
    if (freshOffers.length === 0) return

    freshOffers.forEach((offer) => seenOfferIds.current.add(offer.id))
    setToasts((current) => {
      const currentIds = new Set(current.map((toast) => toast.id))
      return [
        ...current,
        ...freshOffers.filter((offer) => !currentIds.has(offer.id)),
      ]
    })
  }, [offers, ready, clientId])

  useEffect(() => {
    toasts.forEach((toast) => {
      if (timers.current.has(toast.id)) return

      const timer = window.setTimeout(() => {
        timers.current.delete(toast.id)
        setToasts((current) => current.filter((item) => item.id !== toast.id))
      }, timeoutMs)

      timers.current.set(toast.id, timer)
    })
  }, [toasts, timeoutMs])

  useEffect(() => {
    const activeTimers = timers.current
    return () => {
      activeTimers.forEach((timer) => window.clearTimeout(timer))
      activeTimers.clear()
    }
  }, [])

  const dismissToast = useCallback((offerId: number) => {
    const timer = timers.current.get(offerId)
    if (timer !== undefined) {
      window.clearTimeout(timer)
      timers.current.delete(offerId)
    }

    setToasts((current) => current.filter((toast) => toast.id !== offerId))
  }, [])

  return { toasts, dismissToast }
}
