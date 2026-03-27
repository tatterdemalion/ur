import { SWATCHES, swatchGradient, hexVariants } from '../../lib/colors.js'

export default function ColorSwatches({ colorIdx, onSelect }) {
  return (
    <div className="swatches">
      {SWATCHES.map((hex, i) => {
        const v = hexVariants(hex)
        return (
          <div
            key={hex}
            className={`swatch${i === colorIdx ? ' sel' : ''}`}
            style={{
              background: swatchGradient(hex),
              boxShadow: `inset 0 1px 3px rgba(255,255,255,.5), 0 1px 5px ${v.shadow}`,
            }}
            onClick={() => onSelect(i)}
          />
        )
      })}
    </div>
  )
}
