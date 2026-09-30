/**
 * Dedicated Recommendations Page with In-Depth Algorithmic Transparency
 */

import React, { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, Cpu, CheckCircle } from 'lucide-react';
import MovieGrid from '../components/MovieGrid';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function RecommendationsPage({ onSelectMovie }) {
  const { summary } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [strategyData, setStrategyData] = useState({
    strategy: 'COLD_START_POPULARITY',
    strategy_badge: 'Cold-Start Popularity',
    strategy_description: '',
  });
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchRecs = async () => {
    setLoading(true);
    try {
      const [recRes, genRes] = await Promise.all([
        api.recommendations.getMine({ genre: selectedGenre, limit: 30 }),
        api.movies.genres(),
      ]);
      setRecommendations(recRes.recommendations || []);
      setStrategyData({
        strategy: recRes.strategy,
        strategy_badge: recRes.strategy_badge,
        strategy_description: recRes.strategy_description,
      });
      setGenres(genRes || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecs();
  }, [selectedGenre, summary?.total_ratings]);

  return (
    <div className="container" style={{ paddingTop: 30, paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 28 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <Sparkles size={24} color="var(--accent-cyan)" />
            <h1 className="font-display" style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff' }}>
              Your Recommendation Feed
            </h1>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: 750 }}>
            Powered by Item-to-Item Collaborative Filtering with Bayesian Cold-Start.
            Recommendations automatically calibrate as you rate more movies.
          </p>
        </div>

        <button
          onClick={fetchRecs}
          disabled={loading}
          className="btn-secondary"
          style={{ padding: '10px 18px' }}
        >
          <RefreshCw size={15} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          Refresh Recommendations
        </button>
      </div>

      {/* Algorithmic Status Card */}
      <div
        className="glass-panel"
        style={{
          padding: '24px 28px',
          marginBottom: 32,
          border: '1px solid rgba(6, 182, 212, 0.3)',
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(15, 23, 42, 0.8))',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <span style={{ fontSize: '1.4rem' }}>
            {strategyData.strategy === 'COLLABORATIVE_FILTERING' ? '🎯' : strategyData.strategy === 'HYBRID_TRANSITION' ? '⚡' : '❄️'}
          </span>
          <h3 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff' }}>
            Current Strategy: {strategyData.strategy_badge}
          </h3>
        </div>
        <p style={{ color: '#cbd5e1', fontSize: '0.92rem', lineHeight: 1.6, maxWidth: 850 }}>
          {strategyData.strategy_description}
        </p>
      </div>

      {/* Genre Filters */}
      {genres.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            overflowX: 'auto',
            paddingBottom: 14,
            marginBottom: 24,
          }}
        >
          <button
            onClick={() => setSelectedGenre('')}
            style={{
              padding: '7px 18px',
              borderRadius: 99,
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              border: selectedGenre === '' ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.1)',
              background: selectedGenre === '' ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.04)',
              color: selectedGenre === '' ? '#07090e' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}
          >
            All Recommended
          </button>

          {genres.map((g) => (
            <button
              key={g}
              onClick={() => setSelectedGenre(g)}
              style={{
                padding: '7px 16px',
                borderRadius: 99,
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                border: selectedGenre === g ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.1)',
                background: selectedGenre === g ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                color: selectedGenre === g ? 'var(--accent-cyan)' : 'var(--text-muted)',
                transition: 'all 0.2s',
              }}
            >
              {g}
            </button>
          ))}
        </div>
      )}

      {/* Grid */}
      <MovieGrid
        movies={recommendations}
        loading={loading}
        onSelectMovie={onSelectMovie}
        showExplanation={true}
        emptyMessage="No recommendations found for this genre filter."
      />
    </div>
  );
}
