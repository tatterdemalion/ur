export default function GameStatus({ statusText, actionText }) {
  return (
    <div className="game-status">
      <div className="status-main">{statusText}</div>
      <div className="status-action">{actionText}</div>
    </div>
  )
}
