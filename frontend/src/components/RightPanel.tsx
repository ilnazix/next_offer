import { SIMULATOR_EVENTS } from '../events'
import type { SimulatedEventRecord, SimulatorEvent } from '../events'
import type { Client, Offer } from '../types'

interface RightPanelProps {
  clients: Client[]
  clientsError: string | null
  selectedClientId: number
  onSelectClient: (clientId: number) => void
  onSimulateEvent: (event: SimulatorEvent) => void
  pendingEventType: string | null
  eventError: string | null
  lastEvent: SimulatedEventRecord | null
  lastOffer: Offer | null
  offerCount: number
}

function formatEventTime(record: SimulatedEventRecord): string {
  const date = new Date(record.at)
  return Number.isNaN(date.getTime())
    ? record.at
    : date.toLocaleTimeString('ru-RU')
}

export function RightPanel({
  clients,
  clientsError,
  selectedClientId,
  onSelectClient,
  onSimulateEvent,
  pendingEventType,
  eventError,
  lastEvent,
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
              {lastEvent
                ? `${lastEvent.label} · ${formatEventTime(lastEvent)}`
                : '—'}
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
