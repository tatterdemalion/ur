export default function GameOver({ winnerIdx, myIdx }) {
  const won = winnerIdx === myIdx
  return (
    <div className="gameover-overlay">
      <div className={`go-text ${won ? 'win-text' : 'lose-text'}`}>
        {won ? 'VICTORY' : 'DEFEAT'}
      </div>
      <small>refresh to play again</small>
    </div>
  )
}
