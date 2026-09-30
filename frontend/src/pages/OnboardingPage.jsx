import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, CheckCircle2, ChevronRight, Film } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import RatingStars from '../components/RatingStars';
import MovieCard from '../components/MovieCard';

export default function OnboardingPage({ onComplete }) {
  const { refreshSummary } = useAuth();
  const [step, setStep] = useState(1);
  const [allGenres, setAllGenres] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [moviesToRate, setMoviesToRate] = useState([]);
  const [loadingMovies, setLoadingMovies] = useState(false);
  const [ratingsCount, setRatingsCount] = useState(0);

  useEffect(() => {
    async function loadGenres() {
      try {
        const res = await api.movies.genres();
        setAllGenres(res || []);
      } catch (err) {
        console.error('Failed to load genres', err);
      }
    }
    loadGenres();
  }, []);

  const handleToggleGenre = (genre) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const handleNextStep = async () => {
    if (step === 1) {
      setStep(2);
      setLoadingMovies(true);
      try {
        // Fetch popular movies for selected genres
        let fetchedMovies = [];
        if (selectedGenres.length > 0) {
          for (const genre of selectedGenres.slice(0, 3)) {
            const res = await api.movies.popular({ genre, limit: 12 });
            fetchedMovies = [...fetchedMovies, ...(res.movies || [])];
          }
          // Remove duplicates
          fetchedMovies = Array.from(new Map(fetchedMovies.map(m => [m.movieId, m])).values());
        } else {
          const res = await api.movies.popular({ limit: 20 });
          fetchedMovies = res.movies || [];
        }
        setMoviesToRate(fetchedMovies);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingMovies(false);
      }
    } else if (step === 2) {
      handleFinish();
    }
  };

  const handleRate = async (movieId, rating) => {
    try {
      await api.interactions.rate(movieId, rating);
      setRatingsCount(prev => prev + 1);
    } catch (err) {
      console.error('Failed to rate', err);
    }
  };

  const handleFinish = async () => {
    await refreshSummary();
    if (onComplete) onComplete();
  };

  return (
    <div className="container" style={{ paddingTop: '60px', paddingBottom: '100px', maxWidth: '900px' }}>
      
      {/* Progress Indicator */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '40px', justifyContent: 'center' }}>
        <div style={{ flex: 1, height: '4px', borderRadius: '4px', background: 'var(--accent-cyan)' }} />
        <div style={{ flex: 1, height: '4px', borderRadius: '4px', background: step >= 2 ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.1)' }} />
      </div>

      <div className="glass-panel" style={{ padding: '40px 48px', borderRadius: '24px', position: 'relative', overflow: 'hidden' }}>
        {/* Step 1: Genres */}
        {step === 1 && (
          <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(6, 182, 212, 0.15)', marginBottom: '16px' }}>
                <Sparkles size={32} color="var(--accent-cyan)" />
              </div>
              <h1 className="font-display" style={{ fontSize: '2.4rem', fontWeight: 800, color: '#fff', marginBottom: '12px' }}>
                Welcome to CineMatch
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
                Let's personalize your movie recommendations. Select your favorite genres to get started.
              </p>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center', marginBottom: '48px' }}>
              {allGenres.filter(g => g !== 'All').map(genre => {
                const isSelected = selectedGenres.includes(genre);
                return (
                  <button
                    key={genre}
                    onClick={() => handleToggleGenre(genre)}
                    style={{
                      padding: '10px 20px',
                      borderRadius: '9999px',
                      border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.1)',
                      background: isSelected ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.03)',
                      color: isSelected ? '#fff' : 'var(--text-muted)',
                      fontSize: '0.95rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      transform: isSelected ? 'scale(1.05)' : 'scale(1)'
                    }}
                  >
                    {genre}
                  </button>
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button 
                onClick={handleFinish} 
                style={{ background: 'transparent', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer', fontSize: '0.95rem' }}
              >
                Skip for now
              </button>
              
              <button onClick={handleNextStep} className="btn-primary" style={{ padding: '12px 28px', fontSize: '1.05rem' }}>
                Continue <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Rate Movies */}
        {step === 2 && (
          <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <h1 className="font-display" style={{ fontSize: '2.2rem', fontWeight: 800, color: '#fff', marginBottom: '12px' }}>
                Rate a few movies
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>
                Rate at least 3 movies to unlock highly personalized recommendations.
              </p>
              
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 16px', borderRadius: '99px', marginTop: '16px' }}>
                <CheckCircle2 size={16} color="#10b981" />
                <span style={{ color: '#10b981', fontWeight: 700, fontSize: '0.9rem' }}>{ratingsCount} rated</span>
              </div>
            </div>

            {loadingMovies ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0', color: 'var(--text-subtle)' }}>
                Loading top movies...
              </div>
            ) : (
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', 
                gap: '20px', 
                maxHeight: '500px', 
                overflowY: 'auto',
                padding: '10px',
                marginBottom: '32px'
              }}>
                {moviesToRate.map(movie => (
                  <div key={movie.movieId} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ aspectRatio: '2/3', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 8px 20px rgba(0,0,0,0.6)' }}>
                      {movie.poster_url ? (
                        <img src={movie.poster_url} alt={movie.clean_title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      ) : (
                        <div style={{ width: '100%', height: '100%', background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Film size={32} color="var(--text-subtle)" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h4 style={{ color: '#fff', fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginBottom: '6px' }}>
                        {movie.clean_title}
                      </h4>
                      <RatingStars size={18} onRate={(rating) => handleRate(movie.movieId, rating)} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button 
                onClick={handleFinish} 
                style={{ background: 'transparent', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer', fontSize: '0.95rem' }}
              >
                I'll do this later
              </button>
              
              <button onClick={handleFinish} className="btn-primary" style={{ padding: '12px 28px', fontSize: '1.05rem' }}>
                Finish <ArrowRight size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}} />
    </div>
  );
}
