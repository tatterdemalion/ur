import { SWATCHES } from '../../lib/colors.js'
import ColorSwatches from './ColorSwatches.jsx'
import GameList from './GameList.jsx'

export default function Lobby({ state, dispatch, send }) {
  const { playerName, colorIdx, lobbyDisabled, lobbyStatus, games } = state

  function handleCreate() {
    send({ type: 'create', name: playerName || 'Player', color: SWATCHES[colorIdx] })
    dispatch({ type: 'LOBBY_DISABLE', value: true })
  }

  function handleJoin(g) {
    send({ type: 'join', game_id: g.game_id, name: playerName || 'Player', color: SWATCHES[colorIdx] })
    dispatch({ type: 'LOBBY_DISABLE', value: true })
  }

  return (
    <div className="lobby-view">
      <p className="title">The Royal Game of Ur</p>

      <div className="wrap">
        {/* Identity */}
        <div className="lobby-panel">
          <div className="lobby-panel-row">
            <span className="field-lbl">Name</span>
            <input
              className="player-name-input"
              type="text"
              placeholder="Your name"
              maxLength={20}
              value={playerName}
              onChange={(e) => dispatch({ type: 'SET_NAME', value: e.target.value })}
            />
          </div>
          <div className="lobby-panel-row">
            <span className="field-lbl">Color</span>
            <ColorSwatches
              colorIdx={colorIdx}
              onSelect={(i) => dispatch({ type: 'SET_COLOR_IDX', value: i })}
            />
          </div>
        </div>

        {/* Create */}
        <div className="lobby-panel" style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderTop: 'none' }}>
          <button className="create-btn" disabled={lobbyDisabled} onClick={handleCreate}>
            + Create Game
          </button>
          <span style={{ fontSize: '.75rem', color: 'var(--dim)' }}>or join one below</span>
        </div>

        <GameList games={games} disabled={lobbyDisabled} onJoin={handleJoin} />

        <div className="lobby-status-bar">
          <div>{lobbyStatus}</div>
        </div>
      </div>
    </div>
  )
}
