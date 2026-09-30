import React, { useState } from 'react';
import { Star } from 'lucide-react';

export default function RatingStars({
  initialRating = 0,
  onRate,
  maxStars = 5,
  size = 18,
  readOnly = false,
  showScore = true,
}) {
  const [hoverRating, setHoverRating] = useState(0);
  const [currentRating, setCurrentRating] = useState(initialRating);

  const displayRating = hoverRating > 0 ? hoverRating : currentRating;

  const handleClick = (starIndex) => {
    if (readOnly) return;
    setCurrentRating(starIndex);
    if (onRate) {
      onRate(starIndex);
    }
  };

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '2px' }}
        onMouseLeave={() => !readOnly && setHoverRating(0)}
      >
        {Array.from({ length: maxStars }, (_, i) => {
          const starValue = i + 1;
          const isFilled = displayRating >= starValue;
          const isHalf = !isFilled && displayRating >= starValue - 0.5;

          return (
            <button
              key={starValue}
              type="button"
              disabled={readOnly}
              onClick={() => handleClick(starValue)}
              onMouseEnter={() => !readOnly && setHoverRating(starValue)}
              style={{
                background: 'none',
                border: 'none',
                padding: '2px',
                cursor: readOnly ? 'default' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'transform 0.15s ease',
                transform: hoverRating === starValue ? 'scale(1.25)' : 'scale(1)',
              }}
              title={readOnly ? `${displayRating.toFixed(1)} stars` : `Rate ${starValue} stars`}
            >
              <Star
                size={size}
                className={
                  isFilled
                    ? 'text-amber-400 fill-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]'
                    : isHalf
                    ? 'text-amber-400 fill-amber-400/50'
                    : 'text-slate-600'
                }
                style={{
                  color: isFilled || isHalf ? '#fbbf24' : '#475569',
                  fill: isFilled ? '#fbbf24' : isHalf ? 'rgba(251, 191, 36, 0.5)' : 'none',
                  filter: isFilled ? 'drop-shadow(0 0 6px rgba(251, 191, 36, 0.4))' : 'none',
                }}
              />
            </button>
          );
        })}
      </div>
      {showScore && (
        <span
          style={{
            fontSize: `${Math.max(11, size - 4)}px`,
            fontWeight: 700,
            color: displayRating > 0 ? '#fbbf24' : '#94a3b8',
            marginLeft: '4px',
          }}
        >
          {displayRating > 0 ? Number(displayRating).toFixed(1) : '—'}
        </span>
      )}
    </div>
  );
}
