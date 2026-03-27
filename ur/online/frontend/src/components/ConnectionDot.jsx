export default function ConnectionDot({ wsStatus }) {
  const isOk = wsStatus === 'connected'
  return (
    <div className={`dot-conn ${isOk ? 'ok' : 'err'}`}>
      {isOk ? '⬤ connected' : wsStatus === 'connecting' ? '⬤ connecting' : '⬤ disconnected'}
    </div>
  )
}
