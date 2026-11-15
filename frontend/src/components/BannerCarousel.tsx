import type { Offer, OfferAction } from '../types'
import { OfferBanner } from './OfferBanner'

interface BannerCarouselProps {
  offers: Offer[]
  onRespond?: (offerId: number, action: OfferAction) => void
}

export function BannerCarousel({ offers, onRespond }: BannerCarouselProps) {
  if (offers.length === 0) {
    return (
      <p className="no-empty">
        Нет активных предложений. Новые появятся здесь автоматически.
      </p>
    )
  }

  return (
    <div className="no-carousel" aria-label="Активные персональные предложения">
      {offers.map((offer) => (
        <OfferBanner key={offer.id} offer={offer} onRespond={onRespond} />
      ))}
    </div>
  )
}
