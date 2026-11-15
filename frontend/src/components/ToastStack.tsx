import type { Offer } from '../types'
import { OfferBanner } from './OfferBanner'

interface ToastStackProps {
  toasts: Offer[]
  onDismiss: (offerId: number) => void
}

export function ToastStack({ toasts, onDismiss }: ToastStackProps) {
  if (toasts.length === 0) return null

  return (
    <div
      className="no-toast-container"
      aria-label="Уведомления о новых предложениях"
      aria-live="polite"
    >
      {toasts.map((offer) => (
        <div
          key={offer.id}
          className="no-toast"
          data-testid={`toast-${offer.id}`}
          role="status"
        >
          <OfferBanner offer={offer} onClose={() => onDismiss(offer.id)} />
        </div>
      ))}
    </div>
  )
}
