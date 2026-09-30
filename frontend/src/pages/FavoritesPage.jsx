import React, { useState, useEffect } from 'react';
import { Heart, Film, ArrowRight, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import MovieGrid from '../components/MovieGrid';

export default function FavoritesPage({ onSelectMovie, onNavigateTab }) {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchFavorites = async () => {
      setLoading(true);
      try {
        const data = await api.interactions.getFavorites();
        if (isMounted) {
          // Normalize to movie format for MovieGrid
          const formatted = data.map((item) => ({
            movieId: item.movie_id,
            title: item.title,
            clean_title: item.title,
            year: item.year,
            poster_url: item.poster_url,
            genres_list: item.genres_list || [],
            mean_rating: 4.5,
            vote_count: 100,
            popularity_score: 4.2,
          }));
          setFavorites(formatted);
        }
      } catch (err) {
        console.error('Failed to load favorites:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchFavorites();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="container" style={{ paddingBottom: '60px', paddingTop: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <Heart size={28} style={{ color: '#f43f5e', fill: '#f43f5e' }} />
          <h1
            style={{
              fontSize: '2.2rem',
              fontWeight: 800,
              color: '#ffffff',
              fontFamily: 'var(--font-display)',
            }}
          >
            My Favorites
          </h1>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
          Your curated collection of loved titles. These contribute to your collaborative filtering profile.
        </p>
      </div>

      {/* Content */}
      {loading ? (
        <MovieGrid movies={[]} loading={true} skeletonCount={8} />
      ) : favorites.length > 0 ? (
        <div>
          <div style={{ marginBottom: '18px', fontSize: '0.9rem', color: '#cbd5e1' }}>
            <strong>{favorites.length}</strong> {favorites.length === 1 ? 'movie' : 'movies'} in your collection
          </div>
          <MovieGrid
            movies={favorites}
            loading={false}
            onSelectMovie={onSelectMovie}
          />
        </div>
      ) : (
        /* Empty State */
        <div
          className="glass-panel"
          style={{
            padding: '60px 24px',
            textAlign: 'center',
            borderRadius: '24px',
            maxWidth: '520px',
            margin: '40px auto',
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'rgba(244, 63, 94, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto',
            }}
          >
            <Heart size={30} style={{ color: '#f43f5e' }} />
          </div>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
            No favorites added yet
          </h3>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '24px', lineHeight: 1.5 }}>
            Explore trending blockbusters and click the heart icon on any movie to build your personalized taste collection.
          </p>
          <button
            onClick={() => onNavigateTab && onNavigateTab('discover')}
            className="btn-primary"
          >
            Explore Movies <ArrowRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
