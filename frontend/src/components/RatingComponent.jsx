/**
 * Interactive 5-Star Rating Component
 */

import React, { useState } from 'react';
import { Star } from 'lucide-react';

export default function RatingComponent({
  rating = 0,
  onRate = null,
  readOnly = false,
  size = 18,
  showLabel = true,
}) {
  const [hoverRating, setHoverRating] = useState(0);

  const displayRating = hoverRating > 0 ? hoverRating : rating;

  const handleClick = (value) => {
    if (readOnly || !onRate) return;
    onRate(value);
  };

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      <div
        style={{ display: 'inline-flex', gap: 3, cursor: readOnly ? 'default' : 'pointer' }}
        onMouseLeave={() => !readOnly && setHoverRating(0)}
      >
        {[1, 2, 3, 4, 5].map((starValue) => {
          const isFilled = displayRating >= starValue;
          const isHalf = !isFilled && displayRating >= starValue - 0.5;

          return (
            <span
              key={starValue}
              onClick={() => handleClick(starValue)}
              onMouseEnter={() => !readOnly && setHoverRating(starValue)}
              style={{
                transition: 'transform 0.15s ease',
                display: 'inline-flex',
                alignItems: 'center',
                transform: !readOnly && hoverRating === starValue ? 'scale(1.2)' : 'scale(1)',
              }}
              title={readOnly ? `${rating} stars` : `Rate ${starValue} stars`}
            >
              <Star
                size={size}
                fill={isFilled ? '#f59e0b' : isHalf ? '#fbbf24' : 'none'}
                color={isFilled || isHalf ? '#f59e0b' : '#475569'}
                strokeWidth={isFilled ? 1.5 : 2}
                style={{
                  filter: isFilled ? 'drop-shadow(0 0 6px rgba(245, 158, 11, 0.45))' : 'none',
                }}
              />
            </span>
          );
        })}
      </div>

      {showLabel && (
        <span
          style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            color: displayRating > 0 ? '#fbbf24' : 'var(--text-subtle)',
            marginLeft: 4,
          }}
        >
          {displayRating > 0 ? Number(displayRating).toFixed(1) : 'Not rated'}
        </span>
      )}
    </div>
  );
}
