import { ROSETTAS, MISSING } from '../../lib/board.js'

/**
 * Board renders the 3×8 grid.
 *
 * Props:
 *   board       — snapshot dict (has myKey / oppKey piece maps)
 *   myKey       — e.g. 'p1_pieces' or 'p2_pieces'
 *   oppKey      — the other player's key
 *   myPath      — progress → [row, col] for the current player
 *   oppPath     — progress → [row, col] for the opponent
 *   flipped     — boolean — flip board for player 0
 *   validMoves  — array of piece ids that are valid to move
 *   onPick      — callback(pieceId) when a valid piece/cell is clicked
 */
export default function Board({ board, myKey, oppKey, myPath, oppPath, flipped, validMoves, onPick }) {
  if (!board) return <div className="board" />

  const myPieces  = board[myKey]  || {}
  const oppPieces = board[oppKey] || {}

  // Build coord → { myPieceId, oppPresent } lookup
  const coordMap = {}

  for (const [idStr, prog] of Object.entries(oppPieces)) {
    const coord = oppPath[+prog]
    if (!coord) continue
    const key = `${coord[0]},${coord[1]}`
    if (!coordMap[key]) coordMap[key] = {}
    coordMap[key].oppPresent = true
  }

  for (const [idStr, prog] of Object.entries(myPieces)) {
    const coord = myPath[+prog]
    if (!coord) continue
    const key = `${coord[0]},${coord[1]}`
    if (!coordMap[key]) coordMap[key] = {}
    coordMap[key].myPieceId = +idStr
  }

  // Which piece ids are valid (and their current progress)
  const validSet = new Set(validMoves)

  // Determine bench valid: any valid piece with progress === 0
  const benchValidId = validMoves.find((id) => (myPieces[String(id)] ?? -1) === 0) ?? null

  // Build valid coord set for board cells
  const validCoords = new Set()
  for (const id of validMoves) {
    const prog = myPieces[String(id)]
    if (prog === 0 || prog === undefined) continue
    const coord = myPath[prog]
    if (!coord) continue
    validCoords.add(`${coord[0]},${coord[1]}`)
  }

  // Render cells: rows 2→0, cols 0→7
  const cells = []
  for (let r = 2; r >= 0; r--) {
    for (let c = 0; c < 8; c++) {
      const k = `${r},${c}`
      const isMissing  = MISSING.has(k)
      const isRosetta  = ROSETTAS.has(k)
      const isValid    = validCoords.has(k)
      const entry      = coordMap[k] || {}

      let cellClass = 'cell'
      if (isMissing)  cellClass += ' missing'
      else if (isRosetta) cellClass += ' rosetta'
      if (isValid)    cellClass += ' valid'

      const handleClick = isValid ? () => {
        const pieceId = entry.myPieceId
        if (pieceId != null) onPick(pieceId)
      } : undefined

      cells.push(
        <div key={k} className={cellClass} onClick={handleClick}>
          {entry.oppPresent && (
            <div className={`piece p1${isRosetta ? ' lit' : ''}`} />
          )}
          {entry.myPieceId != null && (
            <div className={`piece p2${isRosetta ? ' lit' : ''}`} />
          )}
        </div>
      )
    }
  }

  return (
    <div className={`board${flipped ? ' flipped' : ''}`}>
      {cells}
    </div>
  )
}

// Export benchValidId helper for Game to pass to PlayerStrip
export function getBenchValidId(validMoves, myPieces) {
  return validMoves.find((id) => (myPieces[String(id)] ?? -1) === 0) ?? null
}
