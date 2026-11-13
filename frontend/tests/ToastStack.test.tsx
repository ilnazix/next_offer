import { fireEvent, render, screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ToastStack } from '../src/components/ToastStack'
import type { Offer } from '../src/types'

const offer: Offer = {
  id: 7,
  type: 'salary',
  title: 'Сохраните зарплату под 8%',
  subtitle: 'Отложите часть на накопительный счёт',
  background_color: 'linear-gradient(135deg, #7c3aed 0%, #db2777 100%)',
  icon: '💰',
  action_text: 'Открыть счёт',
  status: 'pending',
  created_at: null,
}

describe('ToastStack', () => {
  it('renders nothing when there are no toasts', () => {
    const { container } = render(<ToastStack toasts={[]} onDismiss={vi.fn()} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('renders a toast with the same banner visual as the carousel', () => {
    render(<ToastStack toasts={[offer]} onDismiss={vi.fn()} />)

    const toast = screen.getByTestId(`toast-${offer.id}`)
    expect(within(toast).getByText(offer.title)).toBeInTheDocument()
    expect(within(toast).getByText(offer.subtitle as string)).toBeInTheDocument()
    expect(within(toast).getByText(offer.icon as string)).toBeInTheDocument()

    const banner = within(toast).getByRole('article')
    expect(banner).toHaveAttribute('data-offer-type', 'salary')
    expect(banner.getAttribute('style')).toContain(offer.background_color)
    expect(banner).toHaveClass('no-banner')
  })

  it('calls onDismiss with the offer id when the close button is clicked', () => {
    const onDismiss = vi.fn()
    render(<ToastStack toasts={[offer]} onDismiss={onDismiss} />)

    const toast = screen.getByTestId(`toast-${offer.id}`)
    fireEvent.click(within(toast).getByRole('button', { name: /закрыть уведомление/i }))

    expect(onDismiss).toHaveBeenCalledWith(offer.id)
  })
})
