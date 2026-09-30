import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import MovieCard from './MovieCard';
import { MovieCardSkeleton } from './LoadingSkeleton';

export default function MovieCarousel({
  title,
  subtitle,
  badge,
  movies = [],
  loading = false,
  onSelectMovie,
}) {
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const scrollAmount = clientWidth * 0.75;
      scrollRef.current.scrollTo({
        left: direction === 'left' ? scrollLeft - scrollAmount : scrollLeft + scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div style={{ position: 'relative', margin: '36px 0' }}>
      {/* Header with Title and Nav Controls */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          marginBottom: '16px',
        }}
      >
        <div>
          {badge && (
            <span
              style={{
                display: 'inline-block',
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                padding: '4px 10px',
                borderRadius: '9999px',
                marginBottom: '6px',
                background: 'rgba(6, 182, 212, 0.12)',
                color: '#67e8f9',
                border: '1px solid rgba(6, 182, 212, 0.3)',
              }}
            >
              {badge}
            </span>
          )}
          <h2
            style={{
              fontSize: '1.5rem',
              fontWeight: 800,
              color: '#f8fafc',
              fontFamily: 'var(--font-display)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            {title}
          </h2>
          {subtitle && (
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginTop: '2px' }}>
              {subtitle}
            </p>
          )}
        </div>

        {/* Carousel Arrow Controls */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => scroll('left')}
            className="carousel-nav-btn"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              background: 'rgba(15, 23, 42, 0.8)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#f8fafc',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            title="Scroll left"
          >
            <ChevronLeft size={20} />
          </button>
          <button
            onClick={() => scroll('right')}
            className="carousel-nav-btn"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              background: 'rgba(15, 23, 42, 0.8)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#f8fafc',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            title="Scroll right"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Horizontal Scrolling Track */}
      <div
        ref={scrollRef}
        className="carousel-track"
        style={{
          display: 'flex',
          gap: '20px',
          overflowX: 'auto',
          scrollSnapType: 'x mandatory',
          paddingBottom: '16px',
          paddingTop: '6px',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
      >
        {loading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} style={{ minWidth: '220px', flexShrink: 0 }}>
              <MovieCardSkeleton />
            </div>
          ))
        ) : movies.length > 0 ? (
          movies.map((movie) => (
            <div
              key={movie.movieId}
              style={{
                minWidth: '220px',
                maxWidth: '240px',
                flexShrink: 0,
                scrollSnapAlign: 'start',
              }}
            >
              <MovieCard movie={movie} onClick={() => onSelectMovie && onSelectMovie(movie.movieId)} />
            </div>
          ))
        ) : (
          <div style={{ padding: '24px', color: '#64748b' }}>No movies available.</div>
        )}
      </div>
    </div>
  );
}
