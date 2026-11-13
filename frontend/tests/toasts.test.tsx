import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useOfferToasts } from '../src/hooks/useOfferToasts'
import type { Offer } from '../src/types'

function makeOffer(id: number, title: string): Offer {
  return {
    id,
    type: 'salary',
    title,
    subtitle: null,
    background_color: null,
    icon: null,
    action_text: null,
    status: 'pending',
    created_at: null,
  }
}

const first = makeOffer(1, 'Первый оффер')
const second = makeOffer(2, 'Второй оффер')

afterEach(() => {
  vi.useRealTimers()
})

describe('useOfferToasts', () => {
  it('seeds offers that were already present and toasts only new ones', () => {
    const { result, rerender } = renderHook(
      ({ offers, ready }: { offers: Offer[]; ready: boolean }) =>
        useOfferToasts(offers, { ready, timeoutMs: 5000 }),
      { initialProps: { offers: [] as Offer[], ready: false } },
    )

    rerender({ offers: [first], ready: true })
    expect(result.current.toasts).toHaveLength(0)

    rerender({ offers: [second, first], ready: true })
    expect(result.current.toasts.map((toast) => toast.id)).toEqual([second.id])
  })

  it('does not duplicate a toast on repeated polls with the same offer', () => {
    const { result, rerender } = renderHook(
      ({ offers }: { offers: Offer[] }) =>
        useOfferToasts(offers, { ready: true, timeoutMs: 5000 }),
      { initialProps: { offers: [first] } },
    )

    rerender({ offers: [second, first] })
    rerender({ offers: [second, first] })
    rerender({ offers: [second, first] })

    expect(result.current.toasts.map((toast) => toast.id)).toEqual([second.id])
  })

  it('dismisses a toast manually and never shows it again', () => {
    const { result, rerender } = renderHook(
      ({ offers }: { offers: Offer[] }) =>
        useOfferToasts(offers, { ready: true, timeoutMs: 5000 }),
      { initialProps: { offers: [first] } },
    )

    rerender({ offers: [second, first] })
    expect(result.current.toasts).toHaveLength(1)

    act(() => {
      result.current.dismissToast(second.id)
    })
    expect(result.current.toasts).toHaveLength(0)

    rerender({ offers: [second, first] })
    expect(result.current.toasts).toHaveLength(0)
  })

  it('auto-dismisses a toast after the configured timeout', () => {
    vi.useFakeTimers()

    const { result, rerender } = renderHook(
      ({ offers }: { offers: Offer[] }) =>
        useOfferToasts(offers, { ready: true, timeoutMs: 1000 }),
      { initialProps: { offers: [first] } },
    )

    rerender({ offers: [second, first] })
    expect(result.current.toasts).toHaveLength(1)

    act(() => {
      vi.advanceTimersByTime(999)
    })
    expect(result.current.toasts).toHaveLength(1)

    act(() => {
      vi.advanceTimersByTime(1)
    })
    expect(result.current.toasts).toHaveLength(0)
  })
})
