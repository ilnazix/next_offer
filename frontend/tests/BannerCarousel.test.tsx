import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { BannerCarousel } from '../src/components/BannerCarousel'
import type { Offer } from '../src/types'

const offer: Offer = {
  id: 1,
  type: 'salary',
  title: 'Сохраните зарплату под 8%',
  subtitle: 'Отложите часть на накопительный счёт',
  background_color: 'linear-gradient(135deg, #7c3aed 0%, #db2777 100%)',
  icon: '💰',
  action_text: 'Открыть счёт',
  status: 'pending',
  created_at: null,
}

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
