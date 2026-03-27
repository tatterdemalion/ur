import { useEffect, useRef, useCallback } from 'react'

export function useWebSocket(dispatch) {
  const wsRef = useRef(null)

  const send = useCallback((msg) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg))
    }
  }, [])

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.host}/ws`)
    wsRef.current = ws

    ws.onclose = () => dispatch({ type: 'WS_DISCONNECTED' })
    ws.onerror = () => dispatch({ type: 'WS_ERROR' })
    ws.onmessage = (e) => dispatch({ type: 'WS_MESSAGE', payload: JSON.parse(e.data) })

    return () => ws.close()
  }, [dispatch])

  return send
}
