/**
 * Responsive Movie Grid with Pagination & Empty States
 */

import React from 'react';
import MovieCard from './MovieCard';
import { MovieGridSkeleton } from './LoadingSkeleton';
import { Film, ChevronLeft, ChevronRight } from 'lucide-react';

export default function MovieGrid({
  movies = [],
  loading = false,
  onSelectMovie,
  showExplanation = true,
  page = 1,
  total = 0,
  limit = 20,
  onPageChange = null,
  emptyMessage = "No movies found matching your criteria.",
}) {
  if (loading) {
    return <MovieGridSkeleton count={limit} />;
  }

  if (!movies || movies.length === 0) {
    return (
      <div
        className="glass-panel"
        style={{
          padding: '60px 20px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '20px 0',
        }}
      >
        <Film size={44} color="var(--text-subtle)" style={{ marginBottom: 16 }} />
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8 }}>
          {emptyMessage}
        </h3>
        <p style={{ color: 'var(--text-subtle)', fontSize: '0.9rem', maxWidth: 400 }}>
          Try clearing your filters, searching for a different title, or exploring popular movies.
        </p>
      </div>
    );
  }

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <div className="movie-grid">
        {movies.map((movie) => (
          <MovieCard
            key={movie.movieId}
            movie={movie}
            onSelectMovie={onSelectMovie}
            showExplanation={showExplanation}
          />
        ))}
      </div>

      {/* Pagination Bar */}
      {onPageChange && totalPages > 1 && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 16,
            marginTop: 40,
            marginBottom: 20,
          }}
        >
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="btn-secondary"
            style={{
              padding: '8px 16px',
              opacity: page <= 1 ? 0.4 : 1,
              cursor: page <= 1 ? 'not-allowed' : 'pointer',
            }}
          >
            <ChevronLeft size={16} /> Previous
          </button>

          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Page <strong style={{ color: '#ffffff' }}>{page}</strong> of{' '}
            <strong style={{ color: '#ffffff' }}>{totalPages}</strong> ({total} titles)
          </span>

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="btn-secondary"
            style={{
              padding: '8px 16px',
              opacity: page >= totalPages ? 0.4 : 1,
              cursor: page >= totalPages ? 'not-allowed' : 'pointer',
            }}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
