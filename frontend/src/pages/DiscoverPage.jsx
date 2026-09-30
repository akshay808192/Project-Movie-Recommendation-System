import React, { useState, useEffect } from 'react';
import { Compass, Sparkles, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../services/api';
import MovieGrid from '../components/MovieGrid';

const ALL_GENRES = [
  'All',
  'Action',
  'Adventure',
  'Animation',
  'Children',
  'Comedy',
  'Crime',
  'Documentary',
  'Drama',
  'Fantasy',
  'Film-Noir',
  'Horror',
  'Musical',
  'Mystery',
  'Romance',
  'Sci-Fi',
  'Thriller',
  'War',
  'Western',
];

export default function DiscoverPage({ onSelectMovie }) {
  const [selectedGenre, setSelectedGenre] = useState('All');
  const [page, setPage] = useState(1);
  const [movies, setMovies] = useState([]);
  const [total, setTotal] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => {
    let isMounted = true;
    const fetchMovies = async () => {
      setLoading(true);
      try {
        const genreParam = selectedGenre === 'All' ? null : selectedGenre;
        const res = await api.movies.popular({
          genre: genreParam,
          page,
          limit,
        });
        if (isMounted) {
          setMovies(res.movies || []);
          setTotal(res.total || 0);
          setHasNext(res.has_next || false);
        }
      } catch (err) {
        console.error('Failed to discover movies:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchMovies();
    return () => {
      isMounted = false;
    };
  }, [selectedGenre, page]);

  const handleGenreChange = (genre) => {
    setSelectedGenre(genre);
    setPage(1);
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="container" style={{ paddingBottom: '60px', paddingTop: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <Compass size={28} style={{ color: '#06b6d4' }} />
          <h1
            style={{
              fontSize: '2.2rem',
              fontWeight: 800,
              color: '#ffffff',
              fontFamily: 'var(--font-display)',
            }}
          >
            Discover Movies
          </h1>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', maxWidth: '650px' }}>
          Explore 9,700+ critically reviewed films from the MovieLens dataset, ranked by verified review confidence and Bayesian scores.
        </p>
      </div>

      {/* Genre Filter Pills */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '16px',
          marginBottom: '28px',
          scrollbarWidth: 'none',
        }}
      >
        {ALL_GENRES.map((g) => {
          const isActive = selectedGenre === g;
          return (
            <button
              key={g}
              onClick={() => handleGenreChange(g)}
              style={{
                padding: '8px 18px',
                borderRadius: '9999px',
                fontSize: '0.85rem',
                fontWeight: 600,
                whiteSpace: 'nowrap',
                cursor: 'pointer',
                border: isActive ? '1px solid #06b6d4' : '1px solid rgba(255, 255, 255, 0.08)',
                background: isActive ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                color: isActive ? '#67e8f9' : '#cbd5e1',
                boxShadow: isActive ? '0 0 15px rgba(6, 182, 212, 0.3)' : 'none',
                transition: 'all 0.2s ease',
              }}
            >
              {g}
            </button>
          );
        })}
      </div>

      {/* Results Count & Current Filter */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          fontSize: '0.85rem',
          color: '#94a3b8',
        }}
      >
        <span>
          Showing {movies.length > 0 ? (page - 1) * limit + 1 : 0} –{' '}
          {Math.min(page * limit, total)} of {total.toLocaleString()} movies
        </span>
        <span>Page {page} of {totalPages}</span>
      </div>

      {/* Movies Grid */}
      <MovieGrid
        movies={movies}
        loading={loading}
        onSelectMovie={onSelectMovie}
        skeletonCount={limit}
      />

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '16px',
            marginTop: '48px',
          }}
        >
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="btn-secondary"
            style={{ opacity: page === 1 ? 0.5 : 1, padding: '10px 18px' }}
          >
            <ChevronLeft size={18} /> Previous
          </button>
          <span style={{ fontSize: '0.9rem', color: '#e2e8f0', fontWeight: 600 }}>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNext || loading}
            className="btn-secondary"
            style={{ opacity: !hasNext ? 0.5 : 1, padding: '10px 18px' }}
          >
            Next <ChevronRight size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
