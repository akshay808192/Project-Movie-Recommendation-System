/**
 * Movie Details Modal / View with Ratings, Favorites, and Similar Movies
 */

import React, { useState, useEffect } from 'react';
import { X, Star, Heart, ExternalLink, Film, Sparkles, CheckCircle2, Clock } from 'lucide-react';
import RatingComponent from './RatingComponent';
import MovieCard from './MovieCard';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function MovieDetails({ movieId, onClose, onSelectMovie, onViewFullPage }) {
  const { isAuthenticated, refreshSummary } = useAuth();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userRating, setUserRating] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [ratingSavedMsg, setRatingSavedMsg] = useState('');
  const [isSubmittingRating, setIsSubmittingRating] = useState(false);

  useEffect(() => {
    async function fetchDetails() {
      setLoading(true);
      try {
        const data = await api.movies.get(movieId);
        setMovie(data);
        setUserRating(data.user_rating || 0);
        setIsFavorite(data.is_favorite || false);

        // Also record in watch history when opened
        if (isAuthenticated) {
          api.interactions.recordHistory(movieId).catch(() => {});
        }
      } catch (err) {
        console.error('Failed to load movie details:', err);
      } finally {
        setLoading(false);
      }
    }
    if (movieId) {
      fetchDetails();
    }
  }, [movieId, isAuthenticated]);

  const handleRate = async (newRating) => {
    if (!isAuthenticated) {
      alert('Please sign in or register to submit ratings and personalize your recommendation feed!');
      return;
    }
    setIsSubmittingRating(true);
    try {
      await api.interactions.rate(movieId, newRating);
      setUserRating(newRating);
      setRatingSavedMsg('Rating recorded! Your collaborative profile has been updated.');
      await refreshSummary();
      setTimeout(() => setRatingSavedMsg(''), 4000);
    } catch (err) {
      console.error('Failed to rate movie:', err);
    } finally {
      setIsSubmittingRating(false);
    }
  };

  const handleToggleFavorite = async () => {
    if (!isAuthenticated) {
      alert('Please sign in to save movies to your favorites!');
      return;
    }
    try {
      const res = await api.interactions.toggleFavorite(movieId);
      setIsFavorite(res.is_favorite);
      await refreshSummary();
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  if (!movieId) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        overflowY: 'auto',
      }}
      onClick={onClose}
    >
      <div
        className="glass-panel"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '920px',
          maxHeight: '90vh',
          overflowY: 'auto',
          borderRadius: 'var(--radius-lg)',
          position: 'relative',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          background: '#0d121d',
          boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.95)',
        }}
      >
        {/* Full Page View Button */}
        {onViewFullPage && (
          <button
            onClick={() => {
              onClose();
              onViewFullPage(movieId);
            }}
            title="Expand to Full Page"
            style={{
              position: 'absolute',
              top: 20,
              right: 68,
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '50%',
              width: 38,
              height: 38,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: '#ffffff',
              zIndex: 10,
              transition: 'background 0.2s',
            }}
          >
            <ExternalLink size={18} />
          </button>
        )}

        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(255, 255, 255, 0.1)',
            border: 'none',
            borderRadius: '50%',
            width: 38,
            height: 38,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            color: '#ffffff',
            zIndex: 10,
            transition: 'background 0.2s',
          }}
        >
          <X size={20} />
        </button>

        {loading || !movie ? (
          <div style={{ padding: '60px 40px', textAlign: 'center' }}>
            <div className="skeleton" style={{ height: 40, width: '60%', margin: '0 auto 20px auto' }} />
            <div className="skeleton" style={{ height: 250, width: '100%', borderRadius: 16 }} />
          </div>
        ) : (
          <div style={{ padding: '36px 36px 40px 36px' }}>
            {/* Top Grid: Poster + Main Info */}
            <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
              {/* Poster Card */}
              <div
                style={{
                  flex: '0 0 240px',
                  aspectRatio: '2/3',
                  borderRadius: 14,
                  overflow: 'hidden',
                  backgroundColor: '#07090e',
                  boxShadow: '0 15px 35px rgba(0,0,0,0.7)',
                }}
              >
                {movie.poster_url ? (
                  <img
                    src={movie.poster_url}
                    alt={movie.clean_title}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: 'linear-gradient(135deg, #1e293b, #0f172a)',
                      padding: 20,
                      textAlign: 'center',
                    }}
                  >
                    <Film size={40} color="var(--accent-cyan)" style={{ marginBottom: 12 }} />
                    <h3 style={{ fontSize: '1rem', color: '#fff' }}>{movie.clean_title}</h3>
                  </div>
                )}
              </div>

              {/* Title & Metadata */}
              <div style={{ flex: '1 1 380px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                  <span
                    style={{
                      background: 'rgba(6, 182, 212, 0.15)',
                      color: 'var(--accent-cyan)',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      padding: '3px 10px',
                      borderRadius: 99,
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                    }}
                  >
                    MovieLens ID #{movie.movieId}
                  </span>
                  {movie.year && (
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                      Released: {movie.year}
                    </span>
                  )}
                </div>

                <h1
                  className="font-display"
                  style={{
                    fontSize: 'clamp(1.6rem, 3.5vw, 2.3rem)',
                    fontWeight: 800,
                    color: '#ffffff',
                    lineHeight: 1.2,
                    marginBottom: 14,
                  }}
                >
                  {movie.clean_title}
                </h1>

                {/* Genres Pills */}
                {movie.genres_list && movie.genres_list.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 20 }}>
                    {movie.genres_list.map((g) => (
                      <span
                        key={g}
                        style={{
                          background: 'rgba(255, 255, 255, 0.08)',
                          border: '1px solid rgba(255, 255, 255, 0.12)',
                          padding: '3px 10px',
                          borderRadius: 99,
                          fontSize: '0.8rem',
                          color: '#e2e8f0',
                          fontWeight: 500,
                        }}
                      >
                        {g}
                      </span>
                    ))}
                  </div>
                )}

                {/* Rating Overview Stats */}
                <div
                  className="glass-panel"
                  style={{
                    padding: '16px 20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 24,
                    gap: 16,
                  }}
                >
                  <div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>
                      Community Rating
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                      <Star size={18} fill="#f59e0b" color="#f59e0b" />
                      <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fbbf24' }}>
                        {movie.mean_rating > 0 ? movie.mean_rating.toFixed(1) : 'NR'}
                      </span>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        / 5.0 ({movie.vote_count} reviews)
                      </span>
                    </div>
                  </div>

                  <div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>
                      Popularity Metric
                    </span>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: 4 }}>
                      {movie.popularity_score > 0 ? movie.popularity_score.toFixed(2) : 'N/A'}
                    </div>
                  </div>
                </div>

                {/* User Interactive Rating Box */}
                <div
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px 20px',
                    marginBottom: 20,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffffff' }}>
                      Your Rating (Personalize your recommendations):
                    </span>
                    {userRating > 0 && (
                      <span style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)', fontWeight: 700 }}>
                        ✓ Rated {userRating} Stars
                      </span>
                    )}
                  </div>

                  <RatingComponent
                    rating={userRating}
                    onRate={handleRate}
                    size={26}
                    readOnly={isSubmittingRating}
                  />

                  {ratingSavedMsg && (
                    <div
                      style={{
                        marginTop: 10,
                        fontSize: '0.82rem',
                        color: '#6ee7b7',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <CheckCircle2 size={15} color="var(--accent-emerald)" />
                      {ratingSavedMsg}
                    </div>
                  )}
                </div>

                {/* External Links & Favorite Buttons */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                  <button
                    onClick={handleToggleFavorite}
                    className="btn-secondary"
                    style={{
                      borderColor: isFavorite ? 'var(--accent-rose)' : 'var(--surface-glass-border)',
                      color: isFavorite ? '#fda4af' : '#ffffff',
                    }}
                  >
                    <Heart size={16} fill={isFavorite ? 'var(--accent-rose)' : 'none'} color={isFavorite ? 'var(--accent-rose)' : '#ffffff'} />
                    {isFavorite ? 'In Favorites' : 'Add to Favorites'}
                  </button>

                  {movie.imdb_id_str && (
                    <a
                      href={`https://www.imdb.com/title/${movie.imdb_id_str}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary"
                    >
                      <ExternalLink size={15} /> IMDb Webpage
                    </a>
                  )}

                  {movie.tmdb_id_int && (
                    <a
                      href={`https://www.themoviedb.org/movie/${movie.tmdb_id_int}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary"
                    >
                      <ExternalLink size={15} /> TMDb Info
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Tags Cloud if any */}
            {movie.tags_list && movie.tags_list.length > 0 && (
              <div style={{ marginTop: 32 }}>
                <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 10, fontWeight: 700 }}>
                  Community User Tags:
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {movie.tags_list.map((tag, idx) => (
                    <span
                      key={idx}
                      style={{
                        background: 'rgba(6, 182, 212, 0.08)',
                        border: '1px solid rgba(6, 182, 212, 0.2)',
                        padding: '3px 10px',
                        borderRadius: 6,
                        fontSize: '0.75rem',
                        color: '#67e8f9',
                      }}
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* "More Like This" Collaborative Filtering Section */}
            {movie.similar_movies && movie.similar_movies.length > 0 && (
              <div style={{ marginTop: 40, borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: 28 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}>
                  <Sparkles size={18} color="var(--accent-cyan)" />
                  <h3 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff' }}>
                    More Like This
                  </h3>
                </div>
                <div className="movie-grid">
                  {movie.similar_movies.map((simMovie) => (
                    <MovieCard
                      key={simMovie.movieId}
                      movie={simMovie}
                      onSelectMovie={(m) => {
                        onSelectMovie(m);
                      }}
                      showExplanation={false}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
