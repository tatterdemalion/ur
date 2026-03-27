import { useReducer } from 'react'
import { reducer, initialState } from './store/reducer.js'
import { useWebSocket } from './hooks/useWebSocket.js'
import ConnectionDot from './components/ConnectionDot.jsx'
import Lobby from './components/lobby/Lobby.jsx'
import Game from './components/game/Game.jsx'

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)
  const send = useWebSocket(dispatch)

  const showGame = state.phase === 'game' || state.phase === 'gameover'

  return (
    <>
      <ConnectionDot wsStatus={state.wsStatus} />
      {showGame
        ? <Game state={state} send={send} dispatch={dispatch} />
        : <Lobby state={state} dispatch={dispatch} send={send} />
      }
    </>
  )
}
