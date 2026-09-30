import React from 'react';
import { Star, Sparkles, Play, Info, Heart } from 'lucide-react';
import LikeButton from './LikeButton';
import WatchButton from './WatchButton';

export default function HeroBanner({
  movie,
  onSelectMovie,
}) {
  if (!movie) return null;

  const title = movie.clean_title || movie.title;
  const year = movie.year;
  const rating = movie.mean_rating || 0;
  const votes = movie.vote_count || 0;
  const genres = movie.genres_list || [];
  const matchPct = movie.match_percentage || 98;
  const explanation = movie.explanation || 'Critically acclaimed blockbuster from MovieLens dataset';

  return (
    <div
      className="hero-enter"
      style={{
        position: 'relative',
        borderRadius: '24px',
        overflow: 'hidden',
        minHeight: '480px',
        marginBottom: '40px',
        display: 'flex',
        alignItems: 'flex-end',
        padding: '56px 48px',
        background: movie.poster_url
          ? `linear-gradient(to right, rgba(7, 9, 14, 0.95) 0%, rgba(7, 9, 14, 0.75) 45%, rgba(7, 9, 14, 0.4) 100%), linear-gradient(to top, #07090e 10%, transparent 60%), url(${movie.poster_url}) right 25% / cover no-repeat`
          : 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #07090e 100%)',
        boxShadow: '0 24px 60px -15px rgba(0, 0, 0, 0.9), inset 0 0 120px rgba(0, 0, 0, 0.8)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <div style={{ maxWidth: '780px', zIndex: 2 }}>
        {/* Recommendation explanation chip */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '16px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(6, 182, 212, 0.18)',
              border: '1px solid rgba(6, 182, 212, 0.4)',
              padding: '6px 16px',
              borderRadius: '9999px',
              backdropFilter: 'blur(10px)',
            }}
          >
            <Sparkles size={14} style={{ color: '#06b6d4' }} />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#67e8f9' }}>
              {explanation}
            </span>
          </div>
        </div>

        {/* Title */}
        <h1
          style={{
            fontSize: 'clamp(2.2rem, 5vw, 3.8rem)',
            fontWeight: 800,
            lineHeight: 1.12,
            color: '#ffffff',
            marginBottom: '16px',
            fontFamily: 'var(--font-display)',
            textShadow: '0 4px 24px rgba(0, 0, 0, 0.9)',
          }}
        >
          {title}
        </h1>

        {/* Meta badges row */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: '14px',
            marginBottom: '24px',
          }}
        >
          <div
            style={{
              background: 'rgba(16, 185, 129, 0.2)',
              border: '1px solid #10b981',
              padding: '4px 12px',
              borderRadius: '9999px',
              fontWeight: 800,
              fontSize: '0.82rem',
              color: '#6ee7b7',
            }}
          >
            {matchPct}% Match
          </div>

          {year && (
            <span style={{ fontSize: '0.95rem', color: '#cbd5e1', fontWeight: 600 }}>
              {year}
            </span>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Star size={16} style={{ color: '#f59e0b', fill: '#f59e0b' }} />
            <span style={{ fontWeight: 800, color: '#fbbf24', fontSize: '0.95rem' }}>
              {rating > 0 ? rating.toFixed(1) : 'NR'}
            </span>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
              ({votes.toLocaleString()} ratings)
            </span>
          </div>

          {genres.length > 0 && (
            <div style={{ display: 'flex', gap: '6px' }}>
              {genres.slice(0, 3).map((g) => (
                <span
                  key={g}
                  style={{
                    background: 'rgba(255, 255, 255, 0.08)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    padding: '3px 10px',
                    borderRadius: '6px',
                    fontSize: '0.78rem',
                    color: '#e2e8f0',
                  }}
                >
                  {g}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '14px' }}>
          <button
            onClick={() => onSelectMovie && onSelectMovie(movie.movieId)}
            className="btn-primary"
            style={{ padding: '12px 28px', fontSize: '1rem' }}
          >
            <Play size={18} fill="#ffffff" />
            Watch Trailer & Details
          </button>

          <button
            onClick={() => onSelectMovie && onSelectMovie(movie.movieId)}
            className="btn-secondary"
            style={{ padding: '12px 22px' }}
          >
            <Info size={18} />
            More Info
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '6px' }}>
            <LikeButton movieId={movie.movieId} size={18} />
            <WatchButton movieId={movie.movieId} size={18} />
          </div>
        </div>
      </div>
    </div>
  );
}
