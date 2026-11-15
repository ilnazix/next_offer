import { useEffect, useState } from 'react'

import { fetchClients } from '../api/clients'
import { describeError, isAbortError } from '../api/http'
import type { Client } from '../types'

interface UseClientsResult {
  clients: Client[]
  error: string | null
}

export function useClients(): UseClientsResult {
  const [clients, setClients] = useState<Client[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    const controller = new AbortController()

    async function load() {
      try {
        const nextClients = await fetchClients(controller.signal)
        if (cancelled) return
        setClients(nextClients)
        setError(null)
      } catch (cause) {
        if (cancelled || isAbortError(cause)) return
        setError(describeError(cause))
      }
    }

    void load()

    return () => {
      cancelled = true
      controller.abort()
    }
  }, [])

  return { clients, error }
}
