import React, { useState, useEffect } from 'react';
import { Flame, Sparkles, Filter } from 'lucide-react';
import { api } from '../services/api';
import MovieGrid from './MovieGrid';

const POPULAR_GENRES = [
  'All',
  'Action',
  'Drama',
  'Sci-Fi',
  'Comedy',
  'Crime',
  'Thriller',
  'Animation',
  'Adventure',
];

export default function PopularSection({ onSelectMovie, limit = 12 }) {
  const [selectedGenre, setSelectedGenre] = useState('All');
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchPopular = async () => {
      setLoading(true);
      try {
        const genreParam = selectedGenre === 'All' ? null : selectedGenre;
        const res = await api.movies.popular({ genre: genreParam, limit });
        if (isMounted) {
          setMovies(res.movies || []);
        }
      } catch (err) {
        console.error('Failed to load popular movies:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchPopular();
    return () => {
      isMounted = false;
    };
  }, [selectedGenre, limit]);

  return (
    <div style={{ margin: '48px 0' }}>
      {/* Section Header */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Flame size={22} style={{ color: '#f59e0b' }} />
            <h2
              style={{
                fontSize: '1.6rem',
                fontWeight: 800,
                color: '#ffffff',
                fontFamily: 'var(--font-display)',
              }}
            >
              Trending & Critically Acclaimed
            </h2>
          </div>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
            Top-rated blockbusters based on community reviews and overall popularity.
          </p>
        </div>

        {/* Genre Filter Chips */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          {POPULAR_GENRES.map((g) => {
            const isActive = selectedGenre === g;
            return (
              <button
                key={g}
                onClick={() => setSelectedGenre(g)}
                style={{
                  padding: '6px 14px',
                  borderRadius: '9999px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: isActive ? '1px solid #f59e0b' : '1px solid rgba(255, 255, 255, 0.08)',
                  background: isActive ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                  color: isActive ? '#fef08a' : '#cbd5e1',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? '0 0 12px rgba(245, 158, 11, 0.25)' : 'none',
                }}
              >
                {g}
              </button>
            );
          })}
        </div>
      </div>

      {/* Movies Grid */}
      <MovieGrid
        movies={movies}
        loading={loading}
        onSelectMovie={onSelectMovie}
        skeletonCount={limit}
      />
    </div>
  );
}
