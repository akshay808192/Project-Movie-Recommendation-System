/**
 * User Profile Dashboard with Recommendation Maturity Meter, Demo Taste Seeder & Lists
 */

import React, { useState, useEffect } from 'react';
import { User, Star, Heart, History, Sparkles, CheckCircle2, Shield, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import MovieGrid from './MovieGrid';

export default function UserProfile({ onSelectMovie }) {
  const { user, summary, refreshSummary } = useAuth();
  const [activeTab, setActiveTab] = useState('ratings');
  const [ratingsList, setRatingsList] = useState([]);
  const [favoritesList, setFavoritesList] = useState([]);
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seedingMsg, setSeedingMsg] = useState('');

  useEffect(() => {
    async function loadUserData() {
      setLoading(true);
      try {
        const [rData, fData, hData] = await Promise.all([
          api.interactions.getRatings(),
          api.interactions.getFavorites(),
          api.interactions.getHistory(),
        ]);
        setRatingsList(rData);
        setFavoritesList(fData);
        setHistoryList(hData);
      } catch (err) {
        console.error('Failed to load user data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadUserData();
  }, []);

  const handleSeedProfile = async (profileKey) => {
    try {
      setSeedingMsg('Adding demo ratings to personalize your feed...');
      await api.recommendations.seedDemo(profileKey);
      await refreshSummary();
      const updatedRatings = await api.interactions.getRatings();
      setRatingsList(updatedRatings);
      setSeedingMsg(`✓ Successfully added 5 ratings! Your recommendations are now personalized to your taste!`);
      setTimeout(() => setSeedingMsg(''), 5000);
    } catch (err) {
      console.error(err);
      setSeedingMsg('Failed to seed profile.');
    }
  };

  const handleDeleteRating = async (e, movieId) => {
    e.stopPropagation();
    try {
      await api.interactions.deleteRating(movieId);
      setRatingsList(ratingsList.filter((r) => r.movie_id !== movieId));
      await refreshSummary();
    } catch (err) {
      console.error(err);
    }
  };

  const totalInteractions = (summary?.total_ratings || 0) + (summary?.total_favorites || 0);
  const maturityPct = Math.min(100, Math.round((totalInteractions / 5) * 100));

  return (
    <div className="container" style={{ paddingBottom: 60 }}>
      {/* Header Banner */}
      <div
        className="glass-panel"
        style={{
          padding: '36px 40px',
          marginBottom: 36,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 24,
          borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(13, 18, 29, 0.9))',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-cyan))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.8rem',
              fontWeight: 800,
              color: '#fff',
              boxShadow: '0 0 25px rgba(6, 182, 212, 0.4)',
            }}
          >
            {user?.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="font-display" style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff' }}>
              {user?.username}
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{user?.email}</p>
          </div>
        </div>

        {/* Quick Stats Pill Counters */}
        <div style={{ display: 'flex', gap: 16 }}>
          <div
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '12px 20px',
              borderRadius: 14,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-amber)' }}>
              {summary?.total_ratings || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>
              Ratings
            </div>
          </div>

          <div
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '12px 20px',
              borderRadius: 14,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-rose)' }}>
              {summary?.total_favorites || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>
              Favorites
            </div>
          </div>

          <div
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '12px 20px',
              borderRadius: 14,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
              {summary?.total_history || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>
              Watched
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation Engine Maturity Gauge */}
      <div
        className="glass-panel"
        style={{
          padding: '24px 28px',
          marginBottom: 36,
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(6, 182, 212, 0.25)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Shield size={18} color="var(--accent-cyan)" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff' }}>
                Profile Personalization Level
              </h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
              Rate or watch more movies to help us curate better recommendations for you.
            </p>
          </div>
          <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
            {maturityPct}%
          </span>
        </div>

        {/* Progress Bar */}
        <div
          style={{
            height: 10,
            width: '100%',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: 99,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${maturityPct}%`,
              background:
                maturityPct >= 100
                  ? 'linear-gradient(90deg, #10b981, #06b6d4)'
                  : maturityPct > 0
                  ? 'linear-gradient(90deg, #f59e0b, #06b6d4)'
                  : '#475569',
              transition: 'width 0.5s ease',
              borderRadius: 99,
            }}
          />
        </div>
      </div>

      {/* Quick Taste Seeder Section */}
      <div
        className="glass-panel"
        style={{
          padding: '24px 28px',
          marginBottom: 36,
          background: 'rgba(139, 92, 246, 0.08)',
          border: '1px solid rgba(139, 92, 246, 0.25)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <Sparkles size={18} color="var(--accent-purple)" />
          <h3 className="font-display" style={{ fontSize: '1.15rem', fontWeight: 800, color: '#ffffff' }}>
            Jumpstart Your Recommendations
          </h3>
        </div>
        <p style={{ color: '#cbd5e1', fontSize: '0.88rem', marginBottom: 16 }}>
          Select a flavor profile below to instantly populate your taste preferences:
        </p>

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button
            onClick={() => handleSeedProfile('action_scifi')}
            className="btn-secondary"
            style={{ fontSize: '0.85rem' }}
          >
            🚀 Seed Sci-Fi / Action Fan (Star Wars, Matrix, Terminator 2)
          </button>
          <button
            onClick={() => handleSeedProfile('drama_crime')}
            className="btn-secondary"
            style={{ fontSize: '0.85rem' }}
          >
            🎬 Seed Crime / Drama Fan (Godfather, Goodfellas, Pulp Fiction)
          </button>
          <button
            onClick={() => handleSeedProfile('comedy_animation')}
            className="btn-secondary"
            style={{ fontSize: '0.85rem' }}
          >
            🎨 Seed Animation / Comedy Fan (Toy Story, Aladdin, Forrest Gump)
          </button>
        </div>

        {seedingMsg && (
          <div
            style={{
              marginTop: 14,
              color: '#a7f3d0',
              fontSize: '0.85rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <CheckCircle2 size={16} color="#10b981" /> {seedingMsg}
          </div>
        )}
      </div>

      {/* Tabs Navigation: Ratings / Favorites / History */}
      <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: 14, marginBottom: 28 }}>
        <button
          onClick={() => setActiveTab('ratings')}
          style={{
            background: activeTab === 'ratings' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            color: activeTab === 'ratings' ? '#ffffff' : 'var(--text-muted)',
            border: 'none',
            padding: '8px 18px',
            borderRadius: 99,
            cursor: 'pointer',
            fontWeight: 700,
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <Star size={15} color="var(--accent-amber)" /> My Ratings ({ratingsList.length})
        </button>

        <button
          onClick={() => setActiveTab('favorites')}
          style={{
            background: activeTab === 'favorites' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            color: activeTab === 'favorites' ? '#ffffff' : 'var(--text-muted)',
            border: 'none',
            padding: '8px 18px',
            borderRadius: 99,
            cursor: 'pointer',
            fontWeight: 700,
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <Heart size={15} color="var(--accent-rose)" /> My Favorites ({favoritesList.length})
        </button>

        <button
          onClick={() => setActiveTab('history')}
          style={{
            background: activeTab === 'history' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            color: activeTab === 'history' ? '#ffffff' : 'var(--text-muted)',
            border: 'none',
            padding: '8px 18px',
            borderRadius: 99,
            cursor: 'pointer',
            fontWeight: 700,
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <History size={15} color="var(--accent-cyan)" /> Watch History ({historyList.length})
        </button>
      </div>

      {/* Tab Content Display */}
      {activeTab === 'ratings' && (
        ratingsList.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>
            You haven't rated any movies yet. Search or browse movies and rate them with 1-5 stars!
          </p>
        ) : (
          <div className="movie-grid">
            {ratingsList.map((item) => (
              <div
                key={item.movie_id}
                onClick={() => onSelectMovie({ movieId: item.movie_id })}
                className="glass-panel glass-panel-hover"
                style={{ padding: 12, cursor: 'pointer', position: 'relative' }}
              >
                <div style={{ width: '100%', aspectRatio: '2/3', borderRadius: 8, overflow: 'hidden', background: '#0a0f1d' }}>
                  {item.poster_url ? (
                    <img src={item.poster_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', padding: 10, textAlign: 'center' }}>
                      <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{item.title}</span>
                    </div>
                  )}
                </div>
                <h4 style={{ fontSize: '0.9rem', color: '#fff', marginTop: 10, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item.title}
                </h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Star size={14} fill="#f59e0b" color="#f59e0b" />
                    <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#fbbf24' }}>
                      {item.rating.toFixed(1)}
                    </span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteRating(e, item.movie_id)}
                    title="Remove Rating"
                    style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      )}

      {activeTab === 'favorites' && (
        favoritesList.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>
            No favorite movies yet. Click the heart button on any movie card to add it to your favorites.
          </p>
        ) : (
          <div className="movie-grid">
            {favoritesList.map((item) => (
              <div
                key={item.movie_id}
                onClick={() => onSelectMovie({ movieId: item.movie_id })}
                className="glass-panel glass-panel-hover"
                style={{ padding: 12, cursor: 'pointer' }}
              >
                <div style={{ width: '100%', aspectRatio: '2/3', borderRadius: 8, overflow: 'hidden', background: '#0a0f1d' }}>
                  {item.poster_url ? (
                    <img src={item.poster_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', padding: 10, textAlign: 'center' }}>
                      <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{item.title}</span>
                    </div>
                  )}
                </div>
                <h4 style={{ fontSize: '0.9rem', color: '#fff', marginTop: 10, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item.title}
                </h4>
              </div>
            ))}
          </div>
        )
      )}

      {activeTab === 'history' && (
        historyList.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>
            No watch history recorded yet. Movies you inspect or rate will appear here automatically.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {historyList.map((item, idx) => (
              <div
                key={idx}
                onClick={() => onSelectMovie({ movieId: item.movie_id })}
                className="glass-panel glass-panel-hover"
                style={{
                  padding: '14px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <History size={16} color="var(--accent-cyan)" />
                  <div>
                    <h4 style={{ fontSize: '0.95rem', color: '#fff', fontWeight: 600 }}>{item.title}</h4>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)' }}>
                      {item.genres_list?.join(', ')}
                    </span>
                  </div>
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {item.watched_at}
                </span>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}
