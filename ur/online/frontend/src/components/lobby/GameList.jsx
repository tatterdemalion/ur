import { swatchGradient, hexVariants } from '../../lib/colors.js'

export default function GameList({ games, disabled, onJoin }) {
  return (
    <>
      <div className="games-hdr">
        <span>Open Games</span>
        <span className="games-count">
          {games.length}{games.length === 1 ? ' game' : ' games'}
        </span>
      </div>

      <div className="games-list">
        {games.map((g) => {
          const v = hexVariants(g.host_color)
          return (
            <div key={g.game_id} className="game-row">
              <div
                className="game-dot"
                style={{
                  background: swatchGradient(g.host_color),
                  boxShadow: `inset 0 1px 3px rgba(255,255,255,.5), 0 1px 4px ${v.shadow}`,
                }}
              />
              <div style={{ flex: 1 }}>
                <span className="game-host">{g.host_name}</span>
                <span className="game-name-txt">  ·  {g.game_name}</span>
              </div>
              <button
                className="join-btn"
                disabled={disabled}
                onClick={() => onJoin(g)}
              >
                Join
              </button>
            </div>
          )
        })}
      </div>

      {games.length === 0 && (
        <div className="no-games">No open games — be the first to create one</div>
      )}
    </>
  )
}
