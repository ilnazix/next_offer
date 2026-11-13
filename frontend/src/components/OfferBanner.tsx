import type { Offer } from '../types'

const FALLBACK_GRADIENT = 'linear-gradient(135deg, #059669 0%, #10b981 100%)'

interface OfferBannerProps {
  offer: Offer
  onClose?: () => void
}

export function OfferBanner({ offer, onClose }: OfferBannerProps) {
  return (
    <article
      className="no-banner"
      data-offer-type={offer.type}
      style={{ background: offer.background_color ?? FALLBACK_GRADIENT }}
    >
      {onClose ? (
        <button
          type="button"
          className="no-banner__close"
          aria-label="Закрыть уведомление"
          onClick={onClose}
        >
          ×
        </button>
      ) : null}
      <div>
        <h3 className="no-banner__title">{offer.title}</h3>
        {offer.subtitle ? (
          <p className="no-banner__subtitle">{offer.subtitle}</p>
        ) : null}
      </div>
      {offer.icon ? (
        <span className="no-banner__icon" aria-hidden="true">
          {offer.icon}
        </span>
      ) : null}
    </article>
  )
}
