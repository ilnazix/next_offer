import { config } from '../config'
import type { EventAccepted } from '../types'

export type EventPayload = Record<string, unknown>

export async function postClientEvent(
  clientId: number,
  eventType: string,
  payload: EventPayload = {},
  signal?: AbortSignal,
): Promise<EventAccepted> {
  const response = await fetch(`${config.apiBaseUrl}/api/v1/events`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      client_id: clientId,
      event_type: eventType,
      payload,
    }),
    signal,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return (await response.json()) as EventAccepted
}
