import { useEffect } from 'react'

import type { Offer } from '../types'
import { OfferBanner } from './OfferBanner'

const DEFAULT_TIMEOUT_MS = 8000

interface ToastContainerProps {
  offers: Offer[]
  onDismiss: (offerId: number) => void
  timeoutMs?: number
}

export function ToastContainer({
  offers,
  onDismiss,
  timeoutMs = DEFAULT_TIMEOUT_MS,
}: ToastContainerProps) {
  if (offers.length === 0) return null

  return (
    <div
      className="no-toast-container"
      aria-label="Новые предложения"
      aria-live="polite"
    >
      {offers.map((offer) => (
        <ToastItem
          key={offer.id}
          offer={offer}
          onDismiss={onDismiss}
          timeoutMs={timeoutMs}
        />
      ))}
    </div>
  )
}

interface ToastItemProps {
  offer: Offer
  onDismiss: (offerId: number) => void
  timeoutMs: number
}

function ToastItem({ offer, onDismiss, timeoutMs }: ToastItemProps) {
  useEffect(() => {
    const timer = window.setTimeout(() => onDismiss(offer.id), timeoutMs)
    return () => window.clearTimeout(timer)
  }, [offer.id, onDismiss, timeoutMs])

  return (
    <div className="no-toast">
      <OfferBanner
        offer={offer}
        onClose={() => onDismiss(offer.id)}
        closeLabel="Закрыть уведомление"
      />
    </div>
  )
}
