import type { Offer, OfferAction } from '../types'

const FALLBACK_GRADIENT = 'linear-gradient(135deg, #059669 0%, #10b981 100%)'

interface OfferBannerProps {
  offer: Offer
  onRespond?: (offerId: number, action: OfferAction) => void
}

export function OfferBanner({ offer, onRespond }: OfferBannerProps) {
  return (
    <article
      className="no-banner"
      data-offer-type={offer.type}
      style={{ background: offer.background_color ?? FALLBACK_GRADIENT }}
    >
      <button
        type="button"
        className="no-banner__close"
        aria-label="Закрыть предложение"
        onClick={() => onRespond?.(offer.id, 'dismissed')}
      >
        ×
      </button>

      <div>
        <h3 className="no-banner__title">{offer.title}</h3>
        {offer.subtitle ? (
          <p className="no-banner__subtitle">{offer.subtitle}</p>
        ) : null}
      </div>

      <div className="no-banner__actions">
        <button
          type="button"
          className="no-banner__action no-banner__action--primary"
          onClick={() => onRespond?.(offer.id, 'accepted')}
        >
          {offer.action_text ?? 'Принять'}
        </button>
        <button
          type="button"
          className="no-banner__action"
          onClick={() => onRespond?.(offer.id, 'declined')}
        >
          Отклонить
        </button>
      </div>

      {offer.icon ? (
        <span className="no-banner__icon" aria-hidden="true">
          {offer.icon}
        </span>
      ) : null}
    </article>
  )
}
