import React, { useState, useEffect } from 'react';
import { ArrowLeft, Star, Heart, Film, ExternalLink, Sparkles, Check, Clock } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import RatingStars from '../components/RatingStars';
import LikeButton from '../components/LikeButton';
import WatchButton from '../components/WatchButton';
import MovieCarousel from '../components/MovieCarousel';

export default function MovieDetailsPage({ movieId, onBack, onSelectMovie }) {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userRating, setUserRating] = useState(0);
  const { user, refreshSummary } = useAuth();
  const { showToast } = useToast();

  const effectiveMovieId = movieId || 1;

  useEffect(() => {
    let isMounted = true;
    const fetchMovie = async () => {
      setLoading(true);
      try {
        const data = await api.movies.get(effectiveMovieId);
        if (isMounted) {
          setMovie(data);
          setUserRating(data.user_rating || 0);

          // Record watch history
          api.interactions.recordWatch(effectiveMovieId, user ? user.id : null).catch(() => {});
        }
      } catch (err) {
        console.error('Failed to load movie details:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchMovie();
    return () => {
      isMounted = false;
    };
  }, [effectiveMovieId, user]);

  const handleRate = async (ratingVal) => {
    try {
      await api.interactions.rate(movieId, ratingVal, user ? user.id : null);
      setUserRating(ratingVal);
      showToast(`Rated ${ratingVal} stars! Recommendations updated.`, 'rate');
      if (refreshSummary) refreshSummary();
    } catch (err) {
      showToast(err.message || 'Failed to submit rating', 'error');
    }
  };

  if (loading || !movie) {
    return (
      <div className="container" style={{ padding: '40px 0', textAlign: 'center' }}>
        <div className="skeleton" style={{ height: '360px', borderRadius: '24px', marginBottom: '24px' }} />
        <div className="skeleton" style={{ height: '40px', width: '50%', margin: '0 auto' }} />
      </div>
    );
  }

  const title = movie.clean_title || movie.title;
  const genres = movie.genres_list || [];
  const tags = movie.tags_list || [];

  return (
    <div className="container" style={{ paddingBottom: '80px', paddingTop: '20px' }}>
      {/* Back Button */}
      <button
        onClick={onBack}
        className="btn-secondary"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          marginBottom: '24px',
          fontSize: '0.85rem',
        }}
      >
        <ArrowLeft size={16} /> Back to Catalog
      </button>

      {/* Main Cinematic Header Card */}
      <div
        className="glass-panel"
        style={{
          borderRadius: '24px',
          overflow: 'hidden',
          padding: '40px',
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(7, 9, 14, 0.98))',
          boxShadow: '0 25px 60px -15px rgba(0,0,0,0.9)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          marginBottom: '48px',
        }}
      >
        <div style={{ display: 'flex', gap: '36px', flexWrap: 'wrap' }}>
          {/* Poster Container */}
          <div
            style={{
              flex: '0 0 260px',
              aspectRatio: '2/3',
              borderRadius: '16px',
              overflow: 'hidden',
              backgroundColor: '#07090e',
              boxShadow: '0 15px 40px rgba(0,0,0,0.8)',
            }}
          >
            {movie.poster_url ? (
              <img
                src={movie.poster_url}
                alt={title}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'linear-gradient(135deg, #1e293b, #0f172a)',
                }}
              >
                <Film size={48} style={{ color: '#06b6d4' }} />
              </div>
            )}
          </div>

          {/* Details & Actions */}
          <div style={{ flex: '1 1 400px' }}>
            {/* Meta Tags */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
              <span
                style={{
                  background: 'rgba(6, 182, 212, 0.15)',
                  border: '1px solid rgba(6, 182, 212, 0.35)',
                  color: '#67e8f9',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  padding: '3px 10px',
                  borderRadius: '9999px',
                }}
              >
                MovieLens #{movie.movieId}
              </span>

              {movie.imdb_id_str && (
                <a
                  href={`https://www.imdb.com/title/${movie.imdb_id_str}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    background: '#f5c518',
                    color: '#000000',
                    fontSize: '0.75rem',
                    fontWeight: 800,
                    padding: '3px 10px',
                    borderRadius: '9999px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    textDecoration: 'none',
                  }}
                >
                  IMDb <ExternalLink size={11} />
                </a>
              )}
            </div>

            {/* Title */}
            <h1
              style={{
                fontSize: 'clamp(2rem, 4vw, 2.8rem)',
                fontWeight: 800,
                color: '#ffffff',
                fontFamily: 'var(--font-display)',
                lineHeight: 1.15,
                marginBottom: '10px',
              }}
            >
              {title}
            </h1>

            {/* Release Year & Genres */}
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                alignItems: 'center',
                gap: '12px',
                fontSize: '0.9rem',
                color: '#94a3b8',
                marginBottom: '24px',
              }}
            >
              {movie.year && <span>{movie.year}</span>}
              <span>•</span>
              <div style={{ display: 'flex', gap: '6px' }}>
                {genres.map((g) => (
                  <span
                    key={g}
                    style={{
                      background: 'rgba(255, 255, 255, 0.08)',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '0.8rem',
                      color: '#cbd5e1',
                    }}
                  >
                    {g}
                  </span>
                ))}
              </div>
            </div>

            {/* Statistics Bar */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                gap: '16px',
                padding: '16px',
                borderRadius: '16px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.07)',
                marginBottom: '28px',
              }}
            >
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block' }}>Average Rating</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                  <Star size={16} style={{ color: '#f59e0b', fill: '#f59e0b' }} />
                  <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fbbf24' }}>
                    {movie.mean_rating ? movie.mean_rating.toFixed(2) : 'NR'}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>/ 5.0</span>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block' }}>Verified Reviews</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginTop: '2px', display: 'block' }}>
                  {movie.vote_count.toLocaleString()}
                </span>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block' }}>Bayesian Popularity</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#06b6d4', marginTop: '2px', display: 'block' }}>
                  {movie.popularity_score ? movie.popularity_score.toFixed(3) : '—'}
                </span>
              </div>
            </div>

            {/* Interactive Rating Section */}
            <div
              style={{
                padding: '18px 22px',
                borderRadius: '16px',
                background: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                marginBottom: '24px',
              }}
            >
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fef08a', display: 'block', marginBottom: '8px' }}>
                Your Star Rating (Helps personalize your recommendations)
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <RatingStars
                  initialRating={userRating}
                  onRate={handleRate}
                  size={24}
                  showScore={true}
                />
                {userRating > 0 && (
                  <span style={{ fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Check size={14} /> Rated {userRating} stars
                  </span>
                )}
              </div>
            </div>

            {/* Quick Actions (Favorite & Watch) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <LikeButton movieId={movie.movieId} size={18} />
              <WatchButton movieId={movie.movieId} size={18} />
              <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                Save to favorites or mark as watched
              </span>
            </div>

            {/* Semantic Tags */}
            {tags.length > 0 && (
              <div style={{ marginTop: '24px' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Community Tags
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                  {tags.map((t) => (
                    <span
                      key={t}
                      style={{
                        padding: '3px 10px',
                        borderRadius: '9999px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        fontSize: '0.75rem',
                        color: '#94a3b8',
                      }}
                    >
                      #{t}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Similar Movies Carousel (Item-Item Collaborative Filtering) */}
      {movie.similar_movies && movie.similar_movies.length > 0 && (
        <MovieCarousel
          title="More Like This"
          movies={movie.similar_movies}
          onSelectMovie={onSelectMovie}
        />
      )}
    </div>
  );
}
