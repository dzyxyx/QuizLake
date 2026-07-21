import { ref } from 'vue'
import { wsUrl } from '@/api/client'
import type { WsMessage } from '@/types'

type HandlerMap = Partial<{
  [K in WsMessage['type']]: (payload: Extract<WsMessage, { type: K }>['payload']) => void
}>

export function useQuizSocket(sessionId: number, handlers: HandlerMap) {
  const connected = ref(false)
  let socket: WebSocket | null = null
  let closedByUser = false
  let reconnectTimer: number | undefined

  function connect() {
    closedByUser = false
    socket = new WebSocket(wsUrl(`/ws/sessions/${sessionId}`))

    socket.onopen = () => {
      connected.value = true
    }

    socket.onmessage = (event) => {
      let message: WsMessage
      try {
        message = JSON.parse(event.data)
      } catch {
        return
      }
      const handler = handlers[message.type] as ((payload: unknown) => void) | undefined
      handler?.(message.payload)
    }

    socket.onclose = () => {
      connected.value = false
      socket = null
      if (!closedByUser) {
        reconnectTimer = window.setTimeout(connect, 2000)
      }
    }

    socket.onerror = () => {
      socket?.close()
    }
  }

  function disconnect() {
    closedByUser = true
    if (reconnectTimer) window.clearTimeout(reconnectTimer)
    socket?.close()
    socket = null
  }

  return { connect, disconnect, connected }
}
