import { SIMULATOR_EVENTS } from '../events'
import type { SimulatorEvent } from '../events'
import type { Client, Offer } from '../types'

interface RightPanelProps {
  clients: Client[]
  clientsError: string | null
  selectedClientId: number
  onSelectClient: (clientId: number) => void
  onSimulateEvent: (event: SimulatorEvent) => void
  pendingEventType: string | null
  eventError: string | null
  lastOffer: Offer | null
  offerCount: number
}

function formatTimestamp(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleTimeString('ru-RU')
}

function describeProcessedOffer(offer: Offer): string {
  const meta = SIMULATOR_EVENTS.find((event) => event.type === offer.type)
  const label = meta?.label ?? offer.type
  return offer.created_at
    ? `${label} · ${formatTimestamp(offer.created_at)}`
    : label
}

export function RightPanel({
  clients,
  clientsError,
  selectedClientId,
  onSelectClient,
  onSimulateEvent,
  pendingEventType,
  eventError,
  lastOffer,
  offerCount,
}: RightPanelProps) {
  const selectedClient = clients.find((client) => client.id === selectedClientId)
  const isBusy = pendingEventType !== null

  return (
    <aside className="no-right-panel" aria-label="Панель оператора">
      <div className="no-card">
        <h2 className="no-section-title">Симулятор событий</h2>

        <label className="no-field">
          <span className="no-field__label">Клиент для демонстрации</span>
          <select
            className="no-select"
            value={selectedClientId}
            onChange={(event) => onSelectClient(Number(event.target.value))}
          >
            {clients.length === 0 ? (
              <option value={selectedClientId}>
                Клиент #{selectedClientId}
              </option>
            ) : null}
            {clients.map((client) => (
              <option key={client.id} value={client.id}>
                {client.full_name ?? `Клиент #${client.id}`}
              </option>
            ))}
            {selectedClient === undefined && clients.length > 0 ? (
              <option value={selectedClientId}>
                Клиент #{selectedClientId}
              </option>
            ) : null}
          </select>
        </label>

        {clientsError ? (
          <p className="no-alert" role="alert">
            Не удалось загрузить список клиентов ({clientsError}).
          </p>
        ) : null}

        <div className="no-event-buttons">
          {SIMULATOR_EVENTS.map((event) => (
            <button
              key={event.type}
              type="button"
              className={
                event.secondary
                  ? 'no-event-btn no-event-btn--secondary'
                  : 'no-event-btn'
              }
              onClick={() => onSimulateEvent(event)}
              disabled={isBusy}
            >
              {pendingEventType === event.type ? 'Отправка…' : event.label}
            </button>
          ))}
        </div>

        {eventError ? (
          <p className="no-alert" role="alert">
            Не удалось отправить событие ({eventError}).
          </p>
        ) : null}
      </div>

      <div className="no-card">
        <h2 className="no-section-title">Состояние</h2>
        <dl className="no-debug">
          <div className="no-debug__row">
            <dt>Офферов</dt>
            <dd>{offerCount}</dd>
          </div>
          <div className="no-debug__row">
            <dt>Последнее событие</dt>
            <dd>
              {lastOffer ? describeProcessedOffer(lastOffer) : '—'}
            </dd>
          </div>
          <div className="no-debug__row">
            <dt>Последний оффер</dt>
            <dd>{lastOffer ? lastOffer.title : '—'}</dd>
          </div>
        </dl>
      </div>
    </aside>
  )
}
