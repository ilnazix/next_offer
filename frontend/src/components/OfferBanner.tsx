import type { Offer, OfferAction } from '../types'

const FALLBACK_GRADIENT = 'linear-gradient(135deg, #059669 0%, #10b981 100%)'

interface OfferBannerProps {
  offer: Offer
  onClose?: () => void
  closeLabel?: string
  onRespond?: (offerId: number, action: OfferAction) => void
}

export function OfferBanner({
  offer,
  onClose,
  closeLabel,
  onRespond,
}: OfferBannerProps) {
  const handleClose =
    onClose ?? (onRespond ? () => onRespond(offer.id, 'dismissed') : undefined)
  const resolvedCloseLabel =
    closeLabel ?? (onClose ? 'Закрыть уведомление' : 'Закрыть предложение')

  return (
    <article
      className="no-banner"
      data-offer-type={offer.type}
      style={{ background: offer.background_color ?? FALLBACK_GRADIENT }}
    >
      {handleClose ? (
        <button
          type="button"
          className="no-banner__close"
          aria-label={resolvedCloseLabel}
          onClick={handleClose}
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

      {onRespond ? (
        <div className="no-banner__actions">
          <button
            type="button"
            className="no-banner__action no-banner__action--primary"
            onClick={() => onRespond(offer.id, 'accepted')}
          >
            {offer.action_text ?? 'Принять'}
          </button>
          <button
            type="button"
            className="no-banner__action"
            onClick={() => onRespond(offer.id, 'declined')}
          >
            Отклонить
          </button>
        </div>
      ) : null}

      {offer.icon ? (
        <span className="no-banner__icon" aria-hidden="true">
          {offer.icon}
        </span>
      ) : null}
    </article>
  )
}
