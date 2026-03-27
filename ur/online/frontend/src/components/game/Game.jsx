import Dice from './Dice.jsx'
import GameStatus from './GameStatus.jsx'
import Board, { getBenchValidId } from './Board.jsx'
import PlayerStrip from './PlayerStrip.jsx'
import GameOver from './GameOver.jsx'

export default function Game({ state, send, dispatch }) {
  const {
    phase, board, dice, validMoves,
    myIdx, myName, oppName,
    myKey, oppKey, myPath, oppPath,
    myScoreKey, myWaitKey, oppScoreKey, oppWaitKey,
    flipped,
    statusText, actionText,
    winnerIdx,
  } = state

  const myPieces  = board?.[myKey]  || {}
  const oppPieces = board?.[oppKey] || {}
  const stats     = board?.stats    || {}

  const myScore   = stats[myScoreKey]  ?? 0
  const myWaiting = stats[myWaitKey]   ?? 0
  const oppScore  = stats[oppScoreKey] ?? 0
  const oppWaiting = stats[oppWaitKey] ?? 0

  const myBenchCount  = Object.values(myPieces).filter(p => p === 0).length
  const oppBenchCount = Object.values(oppPieces).filter(p => p === 0).length

  const benchValidId = getBenchValidId(validMoves, myPieces)

  function handlePick(pieceId) {
    dispatch({ type: 'MOVE_SENT' })
    send({ type: 'move', piece_id: pieceId })
  }

  function handleBenchClick() {
    if (benchValidId != null) handlePick(benchValidId)
  }

  return (
    <div className="game-view">
      <p className="title">The Royal Game of Ur</p>

      <Dice roll={dice} />

      <GameStatus statusText={statusText} actionText={actionText} />

      <div className="wrap">
        <PlayerStrip
          isYou={false}
          name={oppName}
          score={oppScore}
          waiting={oppWaiting}
          benchCount={oppBenchCount}
          validBench={false}
          onBenchClick={null}
        />

        <Board
          board={board}
          myKey={myKey}
          oppKey={oppKey}
          myPath={myPath}
          oppPath={oppPath}
          flipped={flipped}
          validMoves={validMoves}
          onPick={handlePick}
        />

        <PlayerStrip
          isYou={true}
          name={myName}
          score={myScore}
          waiting={myWaiting}
          benchCount={myBenchCount}
          validBench={benchValidId != null}
          onBenchClick={handleBenchClick}
        />
      </div>

      {phase === 'gameover' && (
        <GameOver winnerIdx={winnerIdx} myIdx={myIdx} />
      )}
    </div>
  )
}
