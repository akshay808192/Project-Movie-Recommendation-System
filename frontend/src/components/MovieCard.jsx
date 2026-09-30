import React, { useState } from 'react';
import { Star, Sparkles, Eye, Film } from 'lucide-react';
import LikeButton from './LikeButton';
import WatchButton from './WatchButton';

export default function MovieCard({
  movie,
  onClick,
  onSelectMovie,
  showExplanation = true,
  isFavoriteInitial = false,
}) {
  const [isHovered, setIsHovered] = useState(false);
  const [imgError, setImgError] = useState(false);

  const title = movie.clean_title || movie.title;
  const year = movie.year;
  const rating = movie.mean_rating || 0;
  const votes = movie.vote_count || 0;
  const genres = movie.genres_list || [];
  const matchPct = movie.match_percentage || (movie.popularity_score ? Math.min(98, Math.round((movie.popularity_score / 4.4) * 98)) : 85);
  const explanation = movie.explanation;
  const primaryGenre = genres[0] || 'Movie';

  const handleClick = () => {
    if (onClick) onClick(movie);
    else if (onSelectMovie) onSelectMovie(movie);
  };

  return (
    <div
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
      tabIndex={0}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsHovered(true)}
      onBlur={() => setIsHovered(false)}
      className="glass-panel movie-card"
      style={{
        cursor: 'pointer',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        padding: '10px',
        borderRadius: '16px',
        transition: 'all 0.35s cubic-bezier(0.2, 0.8, 0.2, 1)',
        transform: isHovered ? 'translateY(-6px) scale(1.025)' : 'translateY(0) scale(1)',
        boxShadow: isHovered
          ? '0 20px 40px -15px rgba(0, 0, 0, 0.9), 0 0 25px rgba(6, 182, 212, 0.2)'
          : '0 8px 24px -10px rgba(0, 0, 0, 0.7)',
        borderColor: isHovered ? 'rgba(6, 182, 212, 0.4)' : 'rgba(255, 255, 255, 0.08)',
      }}
    >
      {/* Poster Image Container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          aspectRatio: '2/3',
          borderRadius: '12px',
          overflow: 'hidden',
          backgroundColor: '#07090e',
          boxShadow: '0 4px 16px rgba(0,0,0,0.6)',
        }}
      >
        {movie.poster_url && !imgError ? (
          <img
            src={movie.poster_url}
            alt={title}
            onError={() => setImgError(true)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transition: 'transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1)',
              transform: isHovered ? 'scale(1.08)' : 'scale(1)',
            }}
          />
        ) : (
          /* High-end Cinematic Fallback Visual Card */
          <div
            style={{
              width: '100%',
              height: '100%',
              background: 'linear-gradient(145deg, #131b2e 0%, #0d121d 60%, #07090e 100%)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '16px',
              border: '1px solid rgba(255, 255, 255, 0.05)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Film size={22} style={{ color: '#06b6d4', opacity: 0.8 }} />
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  color: '#f59e0b',
                  background: 'rgba(245, 158, 11, 0.15)',
                  padding: '2px 8px',
                  borderRadius: 99,
                }}
              >
                {primaryGenre}
              </span>
            </div>

            <div>
              <h4
                style={{
                  fontSize: '1rem',
                  fontWeight: 700,
                  color: '#ffffff',
                  lineHeight: 1.3,
                  marginBottom: 6,
                  textShadow: '0 2px 10px rgba(0,0,0,0.8)',
                }}
              >
                {title}
              </h4>
              {year && (
                <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>
                  {year}
                </span>
              )}
            </div>

            <div
              style={{
                height: 3,
                width: '35%',
                background: 'linear-gradient(90deg, #06b6d4, transparent)',
                borderRadius: 99,
              }}
            />
          </div>
        )}

        {/* Top Badges & Action Buttons Overlay */}
        <div
          style={{
            position: 'absolute',
            top: 8,
            left: 8,
            right: 8,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            zIndex: 3,
          }}
        >
          {/* Match % / Score Badge */}
          <div
            style={{
              background: 'rgba(7, 9, 14, 0.82)',
              backdropFilter: 'blur(8px)',
              padding: '3px 8px',
              borderRadius: '99px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              border: '1px solid rgba(6, 182, 212, 0.4)',
              boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
            }}
          >
            <Sparkles size={11} style={{ color: '#06b6d4' }} />
            <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#67e8f9' }}>
              {matchPct}% Match
            </span>
          </div>

          {/* Quick Action Buttons (Like & Watch) */}
          <div style={{ display: 'flex', gap: '6px' }}>
            <LikeButton
              movieId={movie.movieId}
              initialLiked={isFavoriteInitial}
              size={13}
            />
            <WatchButton
              movieId={movie.movieId}
              size={13}
            />
          </div>
        </div>

        {/* Hover Glass Overlay with "View Details" CTA */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(to top, rgba(7, 9, 14, 0.95) 0%, rgba(7, 9, 14, 0.4) 50%, transparent 100%)',
            opacity: isHovered ? 1 : 0,
            transition: 'opacity 0.25s ease',
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'center',
            paddingBottom: 14,
            zIndex: 2,
            pointerEvents: 'none',
          }}
        >
          <span
            style={{
              fontSize: '0.78rem',
              fontWeight: 700,
              color: '#ffffff',
              background: 'rgba(6, 182, 212, 0.25)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(6, 182, 212, 0.5)',
              padding: '6px 14px',
              borderRadius: 99,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              boxShadow: '0 4px 15px rgba(0,0,0,0.5)',
            }}
          >
            <Eye size={13} /> View Details
          </span>
        </div>
      </div>

      {/* Card Body Info */}
      <div style={{ padding: '10px 4px 4px 4px', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <h4
          title={title}
          style={{
            fontSize: '0.92rem',
            fontWeight: 700,
            color: '#f8fafc',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            marginBottom: 4,
          }}
        >
          {title}
        </h4>

        {/* Year & Genres */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.78rem',
            color: '#94a3b8',
            marginBottom: 8,
          }}
        >
          {year && <span>{year}</span>}
          {year && genres.length > 0 && <span>•</span>}
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {genres.slice(0, 2).join(', ')}
          </span>
        </div>

        {/* Rating and Reviews count */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: 'auto',
            paddingTop: 4,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Star size={14} style={{ color: '#f59e0b', fill: '#f59e0b' }} />
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#fbbf24' }}>
              {rating > 0 ? rating.toFixed(1) : 'NR'}
            </span>
          </div>

          {votes > 0 && (
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
              {votes} {votes === 1 ? 'review' : 'reviews'}
            </span>
          )}
        </div>

        {/* Transparent Recommender Explanation */}
        {showExplanation && explanation && (
          <div
            title={explanation}
            style={{
              marginTop: 8,
              padding: '5px 8px',
              borderRadius: 6,
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.07)',
              fontSize: '0.7rem',
              color: '#cbd5e1',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Sparkles size={11} style={{ color: '#f59e0b', flexShrink: 0 }} />
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{explanation}</span>
          </div>
        )}
      </div>
    </div>
  );
}
