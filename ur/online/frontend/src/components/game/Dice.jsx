export default function Dice({ roll }) {
  if (roll == null) {
    return <div className="dice-row" />
  }
  return (
    <div className="dice-row">
      {Array.from({ length: 4 }, (_, i) => (
        <div key={i} className={`die ${i < roll ? 'filled' : 'empty'}`} />
      ))}
    </div>
  )
}
