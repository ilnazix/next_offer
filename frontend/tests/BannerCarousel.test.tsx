import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { BannerCarousel } from '../src/components/BannerCarousel'
import { makeOffer } from './factories'

const offer = makeOffer({ id: 1 })

describe('BannerCarousel', () => {
  it('renders the empty state when there are no offers', () => {
    render(<BannerCarousel offers={[]} />)

    expect(screen.getByText(/Нет активных предложений/)).toBeInTheDocument()
  })

  it('renders the title, subtitle, icon and background of an offer', () => {
    render(<BannerCarousel offers={[offer]} />)

    expect(screen.getByText(offer.title)).toBeInTheDocument()
    expect(screen.getByText(offer.subtitle as string)).toBeInTheDocument()
    expect(screen.getByText(offer.icon as string)).toBeInTheDocument()

    const banner = screen.getByRole('article')
    expect(banner).toHaveAttribute('data-offer-type', 'salary')
    expect(banner.getAttribute('style')).toContain(offer.background_color)
  })
})
