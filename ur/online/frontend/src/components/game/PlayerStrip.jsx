/**
 * PlayerStrip — shown above (opponent) and below (you) the board.
 *
 * Props:
 *   isYou       — true for the bottom strip (you), false for top (opponent)
 *   name        — display name
 *   score       — number of scored pieces
 *   waiting     — number of pieces still on bench
 *   benchCount  — total pieces on bench (progress === 0)
 *   validBench  — true when a bench piece is a valid move (you-strip only)
 *   onBenchClick — callback when a bench piece is clicked (you-strip only)
 */
export default function PlayerStrip({ isYou, name, score, waiting, benchCount, validBench, onBenchClick }) {
  const stripClass = `player-strip ${isYou ? 'you-strip' : 'opp-strip'}`
  const dotClass   = `dot-sm ${isYou ? 'you-dot' : 'opp-dot'}`
  const bpClass    = isYou ? 'myc' : 'oppc'

  const benchPieces = Array.from({ length: benchCount })

  const bench = (
    <div className="pbench">
      <span className="bench-lbl">bench</span>
      {benchPieces.map((_, i) => {
        const isValid = isYou && validBench && i === 0
        return (
          <div
            key={i}
            className={`bp ${bpClass}${isValid ? ' valid' : ''}`}
            onClick={isValid ? onBenchClick : undefined}
          />
        )
      })}
    </div>
  )

  const info = (
    <div className="pinfo">
      <div className={dotClass} />
      <span className="pname">{name.toUpperCase().slice(0, 6)}</span>
      <span className="ppts">{score} pts</span>
      {waiting > 0 && <span className="pbtxt">· {waiting} waiting</span>}
    </div>
  )

  return (
    <div className={stripClass}>
      {isYou ? bench : info}
      {isYou ? info : bench}
    </div>
  )
}
