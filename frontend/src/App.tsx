import { useState } from 'react'

import { postClientEvent } from './api/events'
import { BannerCarousel } from './components/BannerCarousel'
import { Header } from './components/Header'
import { RightPanel } from './components/RightPanel'
import { Sidebar } from './components/Sidebar'
import { ToastStack } from './components/ToastStack'
import { config } from './config'
import type { SimulatedEventRecord, SimulatorEvent } from './events'
import { useClientOffers } from './hooks/useClientOffers'
import { useClients } from './hooks/useClients'
import { useOfferToasts } from './hooks/useOfferToasts'

export default function App() {
  const [selectedClientId, setSelectedClientId] = useState(config.clientId)
  const [pendingEventType, setPendingEventType] = useState<string | null>(null)
  const [eventError, setEventError] = useState<string | null>(null)
  const [lastEvent, setLastEvent] = useState<SimulatedEventRecord | null>(null)

  const { offers, status, error, loadedClientId, respondToOffer } =
    useClientOffers(selectedClientId)
  const { clients, error: clientsError } = useClients()
  const { toasts, dismissToast } = useOfferToasts(offers, {
    ready: status === 'ready' && loadedClientId === selectedClientId,
    clientId: selectedClientId,
  })

  const initialLoading = status === 'loading' && offers.length === 0
  const pollLabel = error
    ? 'Нет связи с API'
    : `Обновляется каждые ${Math.round(config.pollingIntervalMs / 1000)} секунды`
  const selectedClient = clients.find(
    (client) => client.id === selectedClientId,
  )

  function handleSelectClient(clientId: number) {
    if (clientId === selectedClientId) return
    setSelectedClientId(clientId)
    setLastEvent(null)
    setEventError(null)
  }

  async function handleSimulateEvent(event: SimulatorEvent) {
    setPendingEventType(event.type)
    setEventError(null)

    try {
      const accepted = await postClientEvent(
        selectedClientId,
        event.type,
        event.payload,
      )
      setLastEvent({
        type: event.type,
        label: event.label,
        eventId: accepted.event_id,
        at: new Date().toISOString(),
      })
    } catch (cause) {
      setEventError(cause instanceof Error ? cause.message : 'unknown error')
    } finally {
      setPendingEventType(null)
    }
  }

  return (
    <>
      <Header
        clientId={selectedClientId}
        clientName={selectedClient?.full_name ?? null}
      />

      <div className="no-layout">
        <Sidebar />

        <main className="no-main">
          <section>
            <div className="no-section-header">
              <h2 className="no-section-title">Персональные предложения</h2>
              <span
                className="no-poll-status"
                data-status={error ? 'error' : status}
                aria-live="polite"
              >
                {pollLabel}
              </span>
            </div>

            {error ? (
              <p className="no-alert" role="alert">
                Не удалось получить предложения ({error}). Повторяем попытки…
              </p>
            ) : null}

            {initialLoading ? (
              <p className="no-empty">Загрузка предложений…</p>
            ) : (
              <BannerCarousel offers={offers} onRespond={respondToOffer} />
            )}
          </section>

          <section>
            <h2 className="no-section-title">Мои финансы</h2>
            <div className="no-balance-grid">
              <div className="no-card">
                <h3 className="no-card__label">Остаток на счёте</h3>
                <div className="no-card__value">10 134,10 ₽</div>
              </div>
              <div className="no-card">
                <h3 className="no-card__label">Кешбэк и бонусы</h3>
                <div className="no-card__value">351 ₽</div>
              </div>
            </div>
          </section>
        </main>

        <RightPanel
          clients={clients}
          clientsError={clientsError}
          selectedClientId={selectedClientId}
          onSelectClient={handleSelectClient}
          onSimulateEvent={handleSimulateEvent}
          pendingEventType={pendingEventType}
          eventError={eventError}
          lastEvent={lastEvent}
          lastOffer={offers[0] ?? null}
          offerCount={offers.length}
        />
      </div>

      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </>
  )
}
