import type { EventAccepted } from '../types'
import { fetchJson } from './http'

export type EventPayload = Record<string, unknown>

export async function postClientEvent(
  clientId: number,
  eventType: string,
  payload: EventPayload = {},
  signal?: AbortSignal,
): Promise<EventAccepted> {
  return fetchJson<EventAccepted>('/api/v1/events', {
    method: 'POST',
    body: JSON.stringify({
      client_id: clientId,
      event_type: eventType,
      payload,
    }),
    signal,
  })
}
